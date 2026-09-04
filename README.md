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

Antes de comenzar, verificá que Docker Desktop esté iniciado y que Ollama responda en el equipo host:

```powershell
docker version
docker compose version
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

Desde la raíz de este repositorio, ejecutá en PowerShell:

```powershell
Copy-Item .env.example .env
ollama pull llama3.2:latest
ollama pull nomic-embed-text
docker compose config --quiet
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

En Bash, Git Bash o WSL, el flujo equivalente es:

```bash
cp .env.example .env
ollama pull llama3.2:latest
ollama pull nomic-embed-text
docker compose config --quiet
docker compose up -d --build
docker compose ps
curl -fsS http://localhost:8000/health
```

El estado esperado para `fastapi` y `qdrant` es `healthy`. Swagger queda disponible en [http://localhost:8000/docs](http://localhost:8000/docs).

Ollama debe ejecutarse en el equipo host, no dentro de este Compose. En Windows no hace falta ejecutar `ollama serve` si la aplicación de Ollama ya está activa. La URL predeterminada `http://host.docker.internal:11434` permite que FastAPI acceda al servicio del host desde Docker Desktop.

La primera indexación descarga o carga el modelo de embeddings, y la primera consulta carga el modelo generativo en memoria. En equipos sin GPU estos pasos pueden tardar más que las ejecuciones siguientes. Si la primera consulta supera 120 segundos, aumentá `OLLAMA_TIMEOUT` a `180` o `300` en `.env` y recreá FastAPI:

```powershell
docker compose up -d --force-recreate fastapi
```

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

### Problemas frecuentes

#### Falta el archivo `.env`

Si Compose muestra `env file .../.env not found`, crealo desde el ejemplo y validá nuevamente la configuración:

```powershell
Copy-Item .env.example .env
docker compose config --quiet
```

#### FastAPI no puede conectarse con Ollama

Primero comprobá Ollama desde el host:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
ollama list
```

Después comprobá la misma conexión desde el contenedor:

```powershell
docker compose exec fastapi python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags', timeout=5).status)"
```

El resultado esperado es `200`. Si falla, confirmá que Ollama esté iniciado, que el firewall permita la conexión desde Docker y que `OLLAMA_URL` coincida con el entorno. En Linux sin Docker Desktop, Ollama también debe escuchar en una interfaz accesible desde el contenedor; no lo expongas fuera de una red confiable.

#### El modelo configurado no existe

Ejecutá `ollama list` y compará los nombres con `OLLAMA_MODEL` y `OLLAMA_EMBEDDING_MODEL` en `.env`. Para instalar los valores predeterminados:

```powershell
ollama pull llama3.2:latest
ollama pull nomic-embed-text
```

#### La instalación de Python falla por certificados

Si el build muestra `CERTIFICATE_VERIFY_FAILED` o `EE certificate key too weak`, normalmente hay un proxy corporativo, antivirus o inspección HTTPS reemplazando el certificado de PyPI. Actualizá esa herramienta para que emita certificados con una clave segura, instalá la CA corporativa en Docker o excluí `pypi.org` y `files.pythonhosted.org` de la inspección HTTPS según la política de tu organización. No desactives la validación TLS ni agregues `--trusted-host` como solución permanente.

#### Advertencia de compatibilidad de Qdrant

El Compose usa `qdrant/qdrant:latest`. Si el servidor avanza más rápido que `qdrant-client`, puede aparecer una advertencia de diferencia de versiones aunque el servicio funcione. Para despliegues reproducibles, fijá la imagen de Qdrant a una versión compatible con el cliente declarado en `requirements.txt`, o actualizá ambos componentes y repetí las pruebas de indexación y búsqueda.

Después de corregir un problema, revisá el estado y los logs:

```powershell
docker compose ps
docker compose logs --tail=100 fastapi
docker compose logs --tail=100 qdrant
```

Detener los servicios:

```powershell
docker compose down
```

El volumen `qdrant_storage` conserva los datos. Usá `docker compose down -v` únicamente si querés eliminar también la colección persistida.

## Graphify

La documentacion del grafo local, sus exclusiones, consultas y actualizacion esta en [`docs/graphify.md`](docs/graphify.md). Graphify es una herramienta auxiliar de desarrollo y no forma parte de las dependencias ni del arranque productivo de FastAPI.

## Licencia y alcance

El manual incluido es ficticio y está pensado para pruebas técnicas del flujo RAG. No representa instrucciones reales de un municipio ni integra pasarelas de pago o sistemas externos.
