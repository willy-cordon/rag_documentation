# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 72 nodes · 109 edges · 9 communities (7 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0430d2db`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7

## God Nodes (most connected - your core abstractions)
1. `OllamaUnavailableError` - 9 edges
2. `OllamaModelNotFoundError` - 9 edges
3. `rag_chat()` - 7 edges
4. `chunk_document()` - 7 edges
5. `generate_text()` - 7 edges
6. `QdrantService` - 7 edges
7. `index_document()` - 7 edges
8. `answer_question()` - 7 edges
9. `index_documents()` - 6 edges
10. `embed_text()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `index_documents()` --indirect_call--> `OllamaModelNotFoundError`  [INFERRED]
  app/api/documents.py → app/services/ollama_service.py
- `index_documents()` --indirect_call--> `OllamaUnavailableError`  [INFERRED]
  app/api/documents.py → app/services/ollama_service.py
- `index_documents()` --calls--> `index_document()`  [EXTRACTED]
  app/api/documents.py → app/services/rag_service.py
- `rag_chat()` --indirect_call--> `OllamaModelNotFoundError`  [INFERRED]
  app/api/documents.py → app/services/ollama_service.py
- `rag_chat()` --indirect_call--> `OllamaUnavailableError`  [INFERRED]
  app/api/documents.py → app/services/ollama_service.py

## Import Cycles
- None detected.

## Communities (9 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.17
Nodes (14): index_documents(), ChatRequest, rag_chat(), Lee, divide, vectoriza y persiste el manual de documentación., Responde una pregunta usando búsqueda semántica y contexto documental., health(), Endpoint liviano para comprobar que la API está levantada., OllamaModelNotFoundError (+6 more)

### Community 1 - "Community 1"
Cohesion: 0.23
Nodes (8): _positive_float(), _positive_int(), Lee un entero positivo desde el entorno y falla con un mensaje claro., Lee un decimal positivo desde el entorno y falla con un mensaje claro., embed_text(), Genera un vector semántico para un texto usando Ollama., generate_embedding(), Solicita a Ollama el embedding de un único texto.

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (12): chunk_document(), DocumentChunk, Fragmento de texto listo para generar un embedding y guardarse en Qdrant., Lee un documento validando que permanezca dentro de ``documents/``., Separa el Markdown en pares ``(sección, contenido)``., Divide texto largo en ventanas con solapamiento para conservar contexto., Convierte un documento completo en chunks con IDs determinísticos., read_document() (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (8): QdrantService, Pequeña fachada para las operaciones de la colección RAG., Crea la colección si falta o valida su dimensión existente., Reemplaza todos los puntos de un documento de forma idempotente., Busca los fragmentos más parecidos al vector de consulta., Indica si la colección configurada existe en Qdrant., PointStruct, ScoredPoint

### Community 4 - "Community 4"
Cohesion: 0.33
Nodes (6): chat(), ChatRequest, Genera una respuesta directa usando Ollama, sin recuperar documentos., generate_answer(), Atajo para generar una respuesta sin contexto RAG., ChatResponse

### Community 5 - "Community 5"
Cohesion: 0.40
Nodes (5): generate_text(), Envía un prompt al endpoint de generación de Ollama y valida su respuesta., answer_question(), Recupera contexto relevante y genera una respuesta fundamentada., Source

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `QdrantService` connect `Community 3` to `Community 1`?**
  _High betweenness centrality (0.282) - this node is a cross-community bridge._
- **Why does `chunk_document()` connect `Community 2` to `Community 1`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `answer_question()` connect `Community 5` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `OllamaUnavailableError` (e.g. with `index_documents()` and `rag_chat()`) actually correct?**
  _`OllamaUnavailableError` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `OllamaModelNotFoundError` (e.g. with `index_documents()` and `rag_chat()`) actually correct?**
  _`OllamaModelNotFoundError` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `rag_chat()` (e.g. with `OllamaModelNotFoundError` and `OllamaUnavailableError`) actually correct?**
  _`rag_chat()` has 2 INFERRED edges - model-reasoned connections that need verification._