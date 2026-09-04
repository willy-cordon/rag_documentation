# Graph Report - rag_documentation  (2026-09-04)

## Corpus Check
- 21 files · ~7,744 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 200 nodes · 278 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d7768b09`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AGENTS.md
- OllamaClient
- documents.py
- VectorStoreUnavailableError
- inference_service.py
- RAG Documentation API
- app/__init__.py
- services/__init__.py
- Graphify
- Manual del Sistema de Estacionamiento Medido
- Flujo completo de la aplicación
- InferenceClient

## God Nodes (most connected - your core abstractions)
1. `OllamaClient` - 18 edges
2. `Manual del Sistema de Estacionamiento Medido` - 13 edges
3. `Flujo completo de la aplicación` - 12 edges
4. `InferenceUnavailableError` - 11 edges
5. `InferenceModelNotFoundError` - 11 edges
6. `RAG Documentation API` - 11 edges
7. `VectorStoreUnavailableError` - 10 edges
8. `Graphify` - 10 edges
9. `InferenceClient` - 9 edges
10. `QdrantService` - 9 edges

## Surprising Connections (you probably didn't know these)
- `OllamaClientTest` --uses--> `InferenceModelNotFoundError`  [INFERRED]
  tests/test_ollama_service.py → app/services/inference.py
- `OllamaClientTest` --uses--> `OllamaClient`  [INFERRED]
  tests/test_ollama_service.py → app/services/ollama_service.py
- `answer_question()` --calls--> `embed_text()`  [EXTRACTED]
  app/services/rag_service.py → app/services/embedding_service.py
- `index_document()` --calls--> `embed_text()`  [EXTRACTED]
  app/services/rag_service.py → app/services/embedding_service.py
- `OllamaClient` --uses--> `InferenceUnavailableError`  [INFERRED]
  app/services/ollama_service.py → app/services/inference.py

## Import Cycles
- None detected.

## Communities (13 total, 2 thin omitted)

### Community 0 - "AGENTS.md"
Cohesion: 0.11
Nodes (17): Current Repository Status, Decision Priority, Documentation Workflow, Evidence Section, Final Rule, Graph Maintenance, graphify, Graphify Evidence (+9 more)

### Community 1 - "OllamaClient"
Cohesion: 0.12
Nodes (18): InferenceError, InferenceModelNotFoundError, InferenceUnavailableError, Exception, Contrato estable entre el RAG y cualquier servicio de inferencia., El servicio de inferencia no está disponible o respondió incorrectamente., El modelo configurado no está disponible en el proveedor., Error base comunicable por cualquier proveedor de inferencia. (+10 more)

### Community 2 - "documents.py"
Cohesion: 0.08
Nodes (28): index_documents(), ChatRequest, post, rag_chat(), Lee, divide, vectoriza y persiste el manual de documentación., Responde una pregunta usando búsqueda semántica y contexto documental., _positive_float(), _positive_int() (+20 more)

### Community 3 - "VectorStoreUnavailableError"
Cohesion: 0.13
Nodes (12): Exception, QdrantService, Indica si la colección configurada existe en Qdrant., Comprueba conectividad y reporta la colección vectorial activa., Qdrant no está disponible o rechazó una operación., Pequeña fachada para las operaciones de la colección RAG., Crea la colección si falta o valida su dimensión existente., Reemplaza todos los puntos de un documento de forma idempotente. (+4 more)

### Community 4 - "inference_service.py"
Cohesion: 0.12
Nodes (21): chat(), ChatRequest, post, Genera una respuesta directa usando Ollama, sin recuperar documentos., health(), lifespan(), Libera conexiones persistentes durante el apagado de la API., Endpoint liviano para comprobar que la API está levantada. (+13 more)

### Community 5 - "RAG Documentation API"
Cohesion: 0.11
Nodes (19): Alcance, Arquitectura, Bash, Git Bash o WSL, Certificados durante el build, Configuración, Estructura, Falta la colección vectorial, Flujos principales (+11 more)

### Community 9 - "Graphify"
Cohesion: 0.14
Nodes (11): Current validation status, Exclusions and privacy, Generation, Graphify, Installation, Limitations, Maintenance, OpenClaw integration (+3 more)

### Community 10 - "Manual del Sistema de Estacionamiento Medido"
Cohesion: 0.14
Nodes (13): 10. Reportes, 11. Preguntas frecuentes, 12. Soporte técnico, 1. Introducción al sistema, 2. Inicio de sesión, 3. Recuperación de contraseña, 4. Gestión de usuarios, 5. Creación de inspectores (+5 more)

### Community 11 - "Flujo completo de la aplicación"
Cohesion: 0.17
Nodes (12): Chat directo, Componentes y ubicación, Configuración y responsabilidades, Consulta RAG, Dónde está el modelo, Evolución futura, fuera de la demo, Fallos esperados, Flujo completo de la aplicación (+4 more)

### Community 12 - "InferenceClient"
Cohesion: 0.29
Nodes (3): InferenceClient, Operaciones requeridas sin depender del proveedor concreto., Protocol

## Knowledge Gaps
- **61 isolated node(s):** `Official Graphify Rules`, `Primary Goal`, `Mandatory Usage`, `Optional Usage`, `Required Workflow` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `VectorStoreUnavailableError` connect `VectorStoreUnavailableError` to `documents.py`, `inference_service.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `OllamaClient` connect `OllamaClient` to `inference_service.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `InferenceUnavailableError` connect `OllamaClient` to `documents.py`, `inference_service.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `OllamaClient` (e.g. with `InferenceModelNotFoundError` and `InferenceUnavailableError`) actually correct?**
  _`OllamaClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `InferenceModelNotFoundError` (e.g. with `OllamaClient` and `OllamaClientTest`) actually correct?**
  _`InferenceModelNotFoundError` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Official Graphify Rules`, `Primary Goal`, `Mandatory Usage` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AGENTS.md` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._