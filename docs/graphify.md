# Graphify

## Purpose

Graphify builds a local knowledge graph of this repository so an agent can follow calls and dependencies across FastAPI, RAG ingestion, Qdrant, and Ollama. It does not replace source inspection, tests, Swagger, the README, or functional documentation.

Graphify is isolated: `graphifyy` is not in `requirements.txt`, is not installed in the Docker image, and is not part of the FastAPI runtime.

## Installation

- Official package: `graphifyy` (double `y`).
- Installed version: `0.9.25`.
- Tool environment: `.tools/graphify-venv`.
- `uv` and `pipx` were unavailable, so an exclusive virtual environment was used.

```powershell
.\.tools\graphify-venv\Scripts\graphify.exe --version
```

## Exclusions and privacy

Graphify respects `.gitignore` and supports `.graphifyignore` with Git-like syntax. Both files exclude secrets, virtual environments, persistent data, models, logs, uploads, backups, and generated output.

In particular, `.env`, `qdrant_storage/`, `ollama/`, `models/`, `data/`, `uploads/`, database exports, and keys/certificates are not indexed. `.env.example` is allowed.

## Generation

Run from the repository root:

```powershell
.\.tools\graphify-venv\Scripts\graphify.exe extract . --backend ollama --out . --max-concurrency 1 --timing
```

`--backend ollama` keeps semantic extraction local. It requires Ollama and Graphify's `OLLAMA_BASE_URL`/`OLLAMA_MODEL`; these are independent from the API variables. Output is written to `graphify-out/` and includes `graph.json`, `GRAPH_REPORT.md`, and `graph.html`, plus regenerable metadata.

If Ollama is unavailable, `extract . --code-only` creates a local AST/code map without model calls, but documents do not receive semantic extraction.

### Current validation status

The committed output in this workspace was generated with `--code-only`: 72 nodes, 109 edges, 9 communities, and about 153 KB across the six top-level output files. A full mixed-repository extraction was attempted locally through Ollama. It did not complete within five minutes with `qwen3:4b`, so the current report must be treated as a code-only map: README, Markdown documents, Docker Compose, and `AGENTS.md` are not represented in the graph yet. No external provider was used.

## Queries and MCP

```powershell
.\.tools\graphify-venv\Scripts\graphify.exe query "where does FastAPI start and how does a question reach Ollama" --graph graphify-out\graph.json
.\.tools\graphify-venv\Scripts\graphify.exe path "rag_chat" "generate_text" --graph graphify-out\graph.json
.\.tools\graphify-venv\Scripts\graphify.exe explain "QdrantService" --graph graphify-out\graph.json
```

The local MCP server uses stdio and publishes no port:

```powershell
.\.tools\graphify-venv\Scripts\python.exe -m graphify.serve graphify-out\graph.json
```

The installed version exposes tools including `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `get_community`, `god_nodes`, and `graph_stats`. The process reads the graph at startup; restart it after regenerating `graph.json` unless a future version documents hot reload.

## OpenClaw integration

The official integration is registered in the project `AGENTS.md` with:

```powershell
.\.tools\graphify-venv\Scripts\graphify.exe claw install
```

The agent should read `graphify-out/GRAPH_REPORT.md`, query the graph, open and verify relevant source files, and warn when the graph is stale.

## Maintenance

Regenerate after structural changes, new modules, Docker changes, or RAG flow changes. No automatic Git hook is installed. For incremental changes use `graphify update .`; after deletions use `extract . --force` to remove stale nodes.

The graph output is versioned as an architecture artifact because this repository is small and the graph helps agents start with context. `graphify-out/cache/` and `cost.json` remain ignored as local/regenerable data. Review any new output for sensitive content before committing.

## Troubleshooting and removal

- If `graphify` is not on PATH, use the absolute executable path above.
- For Ollama errors, check `ollama list`, `OLLAMA_BASE_URL`, and `OLLAMA_MODEL` used by Graphify.
- If MCP shows old data, restart the stdio process.
- To remove it, delete `.tools/graphify-venv` and run `graphify claw uninstall` to remove the `AGENTS.md` section.

## Limitations

Dynamic relationships, environment-loaded configuration, HTTP calls, and real Qdrant/Ollama behavior require manual verification. The graph can become stale, and quality depends on language support and local semantic extraction.
