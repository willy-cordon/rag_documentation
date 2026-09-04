# RAG Documentation API

Demo de una API RAG para consultar documentación Markdown. FastAPI indexa el documento, Qdrant conserva sus vectores y un servicio de inferencia genera embeddings y respuestas fundamentadas.

## Arquitectura

```text
Cliente / Swagger (:8000)
            |
         FastAPI
       /      |       \
 generación  embeddings  búsqueda vectorial
       \      |       /
        Ollama       Qdrant
       (Docker)      (Docker)
```

Los componentes se ejecutan en contenedores separados. FastAPI usa un contrato con operaciones `generate()` y `embed()`, no el runtime directamente. La demo implementa ese contrato con Ollama; otro adaptador puede incorporarse después sin reescribir indexación o consultas.

Los modelos no están en la imagen de FastAPI ni en Git. `ollama-init` los descarga en el volumen `ollama_models`; Qdrant persiste sus colecciones en `qdrant_storage`.

- [Flujo completo de la aplicación](FLUJO_APLICACION.md)
- [Diagrama visual de arquitectura](arquitectura-rag.html)

## Flujos principales

1. **`POST /documents/index`**: lee el manual, genera chunks y embeddings y los guarda en Qdrant.
2. **`POST /rag/chat`**: vectoriza la pregunta, recupera chunks y genera una respuesta usando ese contexto.
3. **`POST /chat`**: genera una respuesta directa, sin consultar Qdrant.
4. **`GET /health`**: confirma que FastAPI está vivo.
5. **`GET /ready`**: comprueba Qdrant, inferencia y ambos modelos.

## Requisitos

- Docker Desktop o Docker Engine con Docker Compose v2.
- Espacio para imágenes, modelos y vectores.
- Internet durante el primer arranque.

No hace falta instalar Python ni Ollama en el host. La configuración predeterminada funciona por CPU; la primera inferencia puede tardar varios minutos sin GPU.

## Instalación

### PowerShell

```powershell
Copy-Item .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps -a
Invoke-RestMethod http://localhost:8000/ready
```

### Bash, Git Bash o WSL

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps -a
curl -fsS http://localhost:8000/ready
```

En el primer arranque, `ollama-init` descarga `llama3.2:latest` y `nomic-embed-text`. Debe finalizar como `Exited (0)`. `fastapi`, `ollama` y `qdrant` deben quedar `healthy`.

Swagger: [http://localhost:8000/docs](http://localhost:8000/docs). Qdrant: [http://localhost:6333/dashboard](http://localhost:6333/dashboard).

## Configuración

| Variable | Uso | Predeterminado |
|---|---|---|
| `INFERENCE_PROVIDER` | Adaptador activo | `ollama` |
| `GENERATION_BASE_URL` | Endpoint de generación | `http://ollama:11434` |
| `GENERATION_MODEL` | Modelo generativo | `llama3.2:latest` |
| `GENERATION_MAX_TOKENS` | Límite de salida | `256` |
| `EMBEDDING_BASE_URL` | Endpoint de embeddings | `http://ollama:11434` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `nomic-embed-text` |
| `EMBEDDING_MODEL_REVISION` | Revisión lógica vectorial | `v1` |
| `INFERENCE_TIMEOUT` | Timeout de lectura/escritura | `300` |
| `INFERENCE_CONNECT_TIMEOUT` | Timeout de conexión | `5` |
| `INFERENCE_MAX_CONNECTIONS` | Máximo de conexiones | `10` |
| `QDRANT_URL` | URL interna de Qdrant | `http://qdrant:6333` |
| `QDRANT_COLLECTION` | Prefijo de colección | `estacionamiento_documentation` |
| `CHUNK_SIZE` | Tamaño aproximado del chunk | `1200` |
| `CHUNK_OVERLAP` | Solapamiento entre chunks | `200` |
| `RAG_TOP_K` | Chunks recuperados | `3` |

### Versionado de embeddings

La colección efectiva se llama `estacionamiento_documentation__<huella>`. La huella deriva del proveedor, modelo y revisión. Si cambia `EMBEDDING_MODEL` o `EMBEDDING_MODEL_REVISION`, se utiliza otra colección y hay que ejecutar `/documents/index`. La anterior se conserva para rollback. Así no se mezclan espacios vectoriales incompatibles aunque tengan la misma dimensión.

## Uso

```powershell
# Indexar
Invoke-RestMethod -Uri http://localhost:8000/documents/index -Method Post

# Consultar mediante RAG
$body = @{ question = '¿Cómo doy de alta una persona para controlar autos estacionados?' } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/rag/chat -Method Post -ContentType 'application/json' -Body $body

# Chat directo
$body = @{ question = 'Explicá qué es un embedding.' } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -ContentType 'application/json' -Body $body
```

## Operación y diagnóstico

```powershell
docker compose ps -a
docker compose logs --tail=100 fastapi
docker compose logs --tail=100 ollama
docker compose logs ollama-init
docker compose logs --tail=100 qdrant
docker compose exec ollama ollama list
```

### `ollama-init` falla

Revisá su log y, después de corregir conectividad o espacio, repetí:

```powershell
docker compose run --rm ollama-init
docker compose up -d fastapi
```

### `/health` funciona pero `/ready` devuelve 503

`/health` sólo verifica el proceso. `/ready` informa si falta un modelo o no responde una dependencia. Revisá el campo `detail` y los logs indicados.

### Falta la colección vectorial

Ejecutá `POST /documents/index`. También es necesario después de cambiar el modelo o revisión de embeddings.

### Timeout de inferencia

En CPU, la generación puede tardar varios minutos. Si supera el valor configurado, aumentá `INFERENCE_TIMEOUT` en `.env` y recreá FastAPI:

```powershell
docker compose up -d --force-recreate fastapi
```

### Certificados durante el build

`CERTIFICATE_VERIFY_FAILED` suele indicar inspección HTTPS corporativa. Instalá la CA corporativa en Docker conforme a la política interna. No desactives TLS ni uses `--trusted-host` permanentemente.

### Docker Hub no responde o muestra `Client.Timeout`

Comprobá la configuración en **Docker Desktop → Settings → Resources → Proxies**. El proxy de contenedores gobierna todas las descargas realizadas por `docker pull` y Compose. Si la red permite acceso directo, seleccioná `No proxy`; en una red corporativa, configurá el proxy autorizado por la organización. Después de aplicar y reiniciar Docker Desktop, validá:

```powershell
docker pull ollama/ollama:0.30.4
docker compose up -d --build
```

## Persistencia y limpieza

`docker compose down` conserva modelos y vectores. `docker compose down -v` elimina ambos volúmenes y obliga a descargar modelos y reindexar; usalo sólo cuando quieras borrar esos datos.

## Estructura

```text
app/api/                         endpoints HTTP
app/models/                      contratos de entrada y salida
app/services/inference.py        contrato independiente del proveedor
app/services/inference_service.py selección y fachada del proveedor
app/services/ollama_service.py   adaptador HTTP de Ollama
app/services/qdrant_service.py   persistencia y búsqueda vectorial
app/services/rag_service.py      indexación y consulta RAG
documents/                       documentos indexables
tests/                           pruebas unitarias
docker-compose.yml               FastAPI + Ollama + init + Qdrant
```

## Alcance

Es una demo inicial. No incluye autenticación, alta disponibilidad, autoscaling ni un runtime organizacional. El contrato de inferencia deja preparado el límite arquitectónico para una evolución posterior sin agregar esa complejidad ahora.

La documentación de Graphify está en [docs/graphify.md](docs/graphify.md).
