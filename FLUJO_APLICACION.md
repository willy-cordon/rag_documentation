# Flujo completo de la aplicación

## Componentes y ubicación

| Componente | Ubicación | Responsabilidad | Persistencia |
|---|---|---|---|
| FastAPI | `parking-ai-fastapi` | API, chunking y coordinación del RAG | Sin estado |
| Ollama | `parking-ai-ollama` | Runtime de generación y embeddings | `ollama_models` |
| `ollama-init` | Contenedor temporal | Garantiza que existan ambos modelos | Termina con código 0 |
| Qdrant | `parking-ai-qdrant` | Vectores, metadatos y búsqueda semántica | `qdrant_storage` |

FastAPI, Ollama y Qdrant se comunican por la red privada de Compose. Sólo FastAPI (`8000`) y Qdrant (`6333`, `6334`) publican puertos al host. Ollama no queda expuesto fuera de Docker.

## Dónde está el modelo

Los modelos no se incluyen en el repositorio ni en la imagen de FastAPI. El primer `docker compose up` ejecuta `ollama-init`, que solicita al servidor Ollama la descarga de:

- `llama3.2:latest`: generación de respuestas.
- `nomic-embed-text`: embeddings de documentos y preguntas.

Los archivos quedan en el volumen Docker `ollama_models`, montado en `/root/.ollama` dentro de Ollama. Recrear el contenedor conserva los modelos; eliminar el volumen obliga a descargarlos otra vez.

## Secuencia de arranque

```text
docker compose up
  ├─ inicia Qdrant ───────────────► healthcheck /readyz
  └─ inicia Ollama ───────────────► healthcheck ollama list
         └─ ejecuta ollama-init ──► pull generación + pull embeddings
                 └─ inicia FastAPI cuando init termina correctamente
```

FastAPI puede estar vivo aunque una dependencia caiga después. Por eso existen dos comprobaciones:

- `/health`: liveness; no consulta dependencias.
- `/ready`: readiness; valida Qdrant, ambos endpoints y ambos modelos.

## Límite de inferencia

El código de negocio no importa Ollama directamente:

```text
rag_service / API
        |
inference_service (fachada)
        |
InferenceClient (contrato)
        |
OllamaClient (adaptador actual)
```

El contrato define `generate()`, `embed()`, `readiness()` y `close()`. En esta demo la fábrica acepta `INFERENCE_PROVIDER=ollama`. En una evolución futura se podrá agregar otro adaptador manteniendo estables los casos de uso RAG.

Generación y embeddings tienen URLs y modelos separados aunque hoy apunten al mismo contenedor. Esto permite separarlos más adelante sin cambiar el dominio.

## Indexación

```text
POST /documents/index
  1. Lee documents/manual_estacionamiento_medido.md.
  2. Detecta secciones y crea chunks solapados.
  3. Solicita un embedding por chunk.
  4. Calcula la dimensión del vector.
  5. Selecciona la colección versionada de Qdrant.
  6. Reemplaza los puntos anteriores del mismo documento.
  7. Guarda vector, texto, sección, página, chunk y huella del modelo.
```

Los IDs son UUID5 determinísticos, por lo que repetir la indexación no genera duplicados.

## Versionado del espacio vectorial

La aplicación calcula:

```text
fingerprint = proveedor:modelo:revisión
colección = QDRANT_COLLECTION + "__" + sha256(fingerprint)[0:10]
```

Cambiar el proveedor, `EMBEDDING_MODEL` o `EMBEDDING_MODEL_REVISION` selecciona otra colección. La colección anterior no se borra, lo que permite rollback. La nueva debe poblarse mediante `/documents/index` antes de consultar.

La revisión debe incrementarse si el artefacto cambia internamente pero mantiene el mismo nombre. La dimensión sigue validándose como segunda barrera de seguridad.

## Consulta RAG

```text
POST /rag/chat
  1. Genera el embedding de la pregunta.
  2. Busca los RAG_TOP_K vectores más cercanos en Qdrant.
  3. Convierte los resultados en contexto con referencias.
  4. Envía contexto, pregunta y reglas al servicio generativo.
  5. Devuelve respuesta y fuentes con sus scores.
```

Si no hay resultados, responde que no dispone de información suficiente. El prompt del sistema obliga al modelo a usar únicamente el contexto recuperado.

## Chat directo

`POST /chat` llama a generación sin embeddings ni Qdrant. Sirve para verificar el runtime, pero no ofrece fundamentación documental.

## Configuración y responsabilidades

- `app/config.py`: entorno, modelos y huella de colección.
- `app/services/inference.py`: contrato y errores genéricos.
- `app/services/inference_service.py`: selección del adaptador y fachada.
- `app/services/ollama_service.py`: protocolo HTTP específico de Ollama.
- `app/services/embedding_service.py`: fachada de embeddings para el RAG.
- `app/services/qdrant_service.py`: colección, reemplazo y búsqueda.
- `app/services/rag_service.py`: orquestación de indexación y respuesta.
- `app/main.py`: ciclo de vida, `/health` y `/ready`.
- `docker-compose.yml`: dependencias, red, volúmenes y orden de arranque.

## Fallos esperados

| Fallo | Resultado |
|---|---|
| Ollama detenido | `/ready` y endpoints de inferencia devuelven 503 |
| Modelo ausente | `/ready` devuelve 503 e identifica el modelo |
| Qdrant detenido | `/ready` devuelve 503; operaciones RAG no continúan |
| Colección activa sin indexar | La consulta pide indexar el documento |
| Cambio de embedding | Se selecciona otra colección; requiere reindexación |
| Reinicio de contenedores | Modelos y vectores sobreviven en volúmenes |

## Evolución futura, fuera de la demo

La frontera creada permite desplegar generación y embeddings como servicios organizacionales separados. Todavía no se incorporan vLLM, KServe, Kubernetes, autenticación ni autoscaling: hacerlo ahora complicaría innecesariamente el desarrollo inicial.
