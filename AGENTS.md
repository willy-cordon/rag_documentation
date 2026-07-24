# AGENTS.md

## graphify

This project has a knowledge graph at `graphify-out/` with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed Graphify skill or instructions before doing anything else.

### Official Graphify Rules

* For codebase questions, first run `graphify query "<question>"` when `graphify-out/graph.json` exists.
* Use `graphify path "<A>" "<B>"` for relationships.
* Use `graphify explain "<concept>"` for focused concepts.
* These commands return a scoped subgraph that is usually much smaller and more accurate than reading `GRAPH_REPORT.md` or recursively opening source files.
* Dirty `graphify-out/` files are expected after hooks or incremental updates. This is **not** a reason to ignore Graphify.
* Only skip Graphify when:

  * the task is specifically about stale or incorrect graph output;
  * the user explicitly asks not to use Graphify.
* If `graphify-out/wiki/index.md` exists, use it for repository navigation instead of broad source browsing.
* Read `graphify-out/GRAPH_REPORT.md` only for high-level architecture reviews or when query/path/explain do not provide enough context.
* After modifying source code, execute:

```bash
graphify update .
```

This performs an AST-only incremental update without semantic extraction.

---

# Project-specific Graphify Policy

## Primary Goal

Graphify is the **primary architectural discovery tool** for this repository.

Its purpose is to reduce unnecessary repository scanning, improve architectural understanding, identify dependencies, and help maintain documentation.

Graphify **does not replace**:

* source code inspection;
* unit or integration tests;
* README;
* documentation;
* ADRs;
* OpenAPI;
* human review.

Every Graphify result must be validated against the actual source code before making conclusions.

---

# Mandatory Usage

Graphify **MUST** be used before performing any task involving:

* architecture analysis;
* dependency analysis;
* implementation of a feature touching multiple files;
* refactoring;
* pull request review;
* documentation updates;
* impact analysis;
* FastAPI routing;
* RAG ingestion flow;
* document indexing;
* embeddings;
* Qdrant integration;
* Ollama integration;
* Docker architecture;
* service interactions;
* identifying affected components.

---

# Optional Usage

Graphify is **not required** for:

* typo fixes;
* formatting;
* comments;
* markdown wording;
* single-file text edits;
* changes where the user explicitly identifies the exact file to modify.

---

# Required Workflow

For architectural tasks always follow this order:

1. Graphify Query

Run the most appropriate Graphify command.

Preferred order:

* `graphify query`
* `graphify explain`
* `graphify path`
* `query_graph`
* `get_node`
* `get_neighbors`
* `shortest_path`

2. Identify Components

Determine:

* entry point;
* affected services;
* dependencies;
* downstream consumers;
* upstream callers;
* related modules.

3. Validate

Open the relevant source files.

Never trust Graphify blindly.

Graphify is an architectural index, not the source of truth.

4. Implement

Only after validating the code.

5. Update Graph

If source code changed:

```bash
graphify update .
```

6. Documentation Review

Determine whether any of these must be updated:

* README.md
* docs/
* architecture documentation
* API documentation
* diagrams
* examples
* AGENTS.md

Only update documents actually affected by the change.

---

# Pull Request Workflow

Before reviewing a Pull Request:

1. Use Graphify to identify impacted modules.
2. Review affected services.
3. Check dependency changes.
4. Identify architectural consequences.
5. Determine whether tests should change.
6. Determine whether documentation should change.
7. Identify observability implications.
8. Mention any risks.

Whenever available, prefer:

* `get_pr_impact`
* `triage_prs`

---

# Documentation Workflow

When asked to update documentation:

1. Use Graphify.
2. Identify affected components.
3. Determine which documentation references those components.
4. Update only impacted documents.
5. Explain why each document was modified.

Do not rewrite unrelated documentation.

---

# Repository Navigation Policy

Never start by recursively opening dozens of files.

Always ask Graphify which files are relevant first.

Only then inspect the source code.

This minimizes context usage and improves accuracy.

---

# Evidence Section

Whenever Graphify is used, include a short section like:

## Graphify Evidence

Tools used:

* graphify query
* get_node
* shortest_path

Relevant nodes:

* ...

Relevant relationships:

* ...

Source files verified:

* ...

Graph status:

* Current
  or
* Possibly stale

---

# Graph Maintenance

Regenerate or update the graph whenever:

* new modules are added;
* services are removed;
* FastAPI routes change;
* RAG ingestion changes;
* embeddings change;
* Qdrant structure changes;
* Ollama integration changes;
* Docker architecture changes;
* large refactors occur.

Incremental update:

```bash
graphify update .
```

Full rebuild when necessary:

```bash
graphify extract . --force
```

---

# Current Repository Status

Current Graphify output is generated primarily from code (AST).

Markdown documentation has not yet been fully indexed through semantic extraction.

Therefore:

* Graphify accurately represents code structure.
* Documentation relationships may be incomplete.
* README and docs should still be consulted when business or operational context is required.

---

# Decision Priority

When answering questions:

1. Source code
2. Graphify relationships
3. Tests
4. Documentation
5. README
6. User instructions

Never reverse this order.

---

# Security

Never index or expose:

* secrets;
* API keys;
* certificates;
* private customer data;
* uploads;
* backups;
* production databases;
* logs;
* generated artifacts excluded by `.graphifyignore`.

Respect `.graphifyignore` and `.gitignore` at all times.

---

# Final Rule

Graphify exists to improve architectural understanding—not to replace engineering judgment.

Always:

* query Graphify;
* validate the source code;
* explain the reasoning;
* implement carefully;
* keep the graph updated.
