# RAG Documentation API

MVP de una API para consultar documentación propia mediante RAG (Retrieval-Augmented Generation). El ejemplo utiliza un manual ficticio del sistema de Estacionamiento Medido, pero la arquitectura puede adaptarse a otros documentos Markdown.

La aplicación recibe una pregunta, busca los fragmentos más relevantes en Qdrant y le entrega ese contexto a un modelo local de Ollama. La respuesta incluye las fuentes recuperadas para facilitar la trazabilidad.

## Arquitectura

```text
Cliente / Swagger
        |
        v
FastAPI (Docker :8000)
        |-- /chat ----------------> Ollama: generación directa
        |-- /documents/index ------> lectura -> chunks -> embeddings -> Qdrant
        `-- /rag/chat -------------> embedding -> búsqueda -> contexto -> Ollama

Qdrant (Docker :6333/:6334)
Ollama (host local :11434)
```

No se utilizan LangChain, LlamaIndex ni otra base vectorial. El flujo está implementado directamente con FastAPI, `httpx` y `qdrant-client`.

## Requisitos

- Docker Desktop con Docker Compose.
- Ollama instalado y ejecutándose en el equipo host.
- Modelo de generación: `llama3.2:latest` (configurable).
- Modelo de embeddings: `nomic-embed-text` (configurable).

Python local no es necesario para ejecutar la API, porque las dependencias se instalan dentro de Docker.

## Instalación

Desde esta carpeta (`labs`):

```powershell
Copy-Item .env.example .env
ollama pull llama3.2:latest
ollama pull nomic-embed-text
docker compose config
docker compose up -d --build
docker compose ps
```

Ollama debe estar ejecutándose en Windows. No hace falta ejecutar `ollama serve` si ya está activo como aplicación. La URL predeterminada `http://host.docker.internal:11434` permite acceder a Ollama desde el contenedor.

## Configuración

Editá `.env` para cambiar valores sin modificar el código:

| Variable | Uso | Valor predeterminado |
|---|---|---|
| `OLLAMA_URL` | URL de Ollama vista desde Docker | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | Modelo que genera respuestas | `llama3.2:latest` |
| `OLLAMA_EMBEDDING_MODEL` | Modelo para embeddings | `nomic-embed-text` |
| `OLLAMA_TIMEOUT` | Timeout HTTP, en segundos | `120` |
| `OLLAMA_NUM_PREDICT` | Máximo de tokens generados | `256` |
| `QDRANT_URL` | URL interna de Qdrant | `http://qdrant:6333` |
| `QDRANT_COLLECTION` | Nombre de la colección vectorial | `estacionamiento_documentation` |
| `CHUNK_SIZE` | Tamaño aproximado de cada fragmento | `1200` |
| `CHUNK_OVERLAP` | Solapamiento entre fragmentos | `200` |
| `RAG_TOP_K` | Cantidad de resultados recuperados | `3` |

## Uso

Swagger queda disponible en [http://localhost:8000/docs](http://localhost:8000/docs).

Comprobar el estado de la API:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Indexar el documento incluido:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/documents/index -Method Post
```

La indexación es repetible: elimina los puntos existentes del documento y los vuelve a insertar con IDs determinísticos.

Consultar la documentación con RAG:

```powershell
$body = @{ question = '¿Cómo doy de alta una persona para controlar autos estacionados?' } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/rag/chat -Method Post -ContentType 'application/json' -Body $body
```

La respuesta contiene `question`, `answer` y `sources`. Cada fuente identifica el documento, la sección, el chunk y el score de similitud.

También existe un chat directo, que no consulta Qdrant:

```powershell
$body = @{ question = 'Explicá qué es un embedding.' } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -ContentType 'application/json' -Body $body
```

## Estructura del proyecto

```text
app/
  api/       Endpoints HTTP.
  models/    Modelos de entrada y salida.
  services/  Lectura, chunking, embeddings, Ollama, Qdrant y RAG.
documents/  Documentación Markdown que se indexa.
Dockerfile  Imagen de la API.
docker-compose.yml  API + Qdrant.
```

## Operación y diagnóstico

Dashboard y API de Qdrant: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

```powershell
docker compose logs -f fastapi
docker compose logs -f qdrant
Invoke-RestMethod http://localhost:6333/collections | ConvertTo-Json -Depth 5
```

Si aparece un error de modelo, verificá `ollama list` y que los nombres de `.env` coincidan con los modelos instalados. Si la API no conecta con Ollama, confirmá que Ollama esté activo y que `OLLAMA_URL` sea accesible desde Docker.

Detener los servicios:

```powershell
docker compose down
```

El volumen `qdrant_storage` conserva los datos. Usá `docker compose down -v` únicamente si querés eliminar también la colección persistida.

## Graphify

La documentacion del grafo local, sus exclusiones, consultas y actualizacion esta en [`docs/graphify.md`](docs/graphify.md). Graphify es una herramienta auxiliar de desarrollo y no forma parte de las dependencias ni del arranque productivo de FastAPI.

## Licencia y alcance

El manual incluido es ficticio y está pensado para pruebas técnicas del flujo RAG. No representa instrucciones reales de un municipio ni integra pasarelas de pago o sistemas externos.
