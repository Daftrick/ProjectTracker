## Graphify

This project has a Graphify knowledge graph at:

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`
- `graphify-out/wiki/index.md` if present

Graphify is part of the normal code navigation and maintenance workflow for this project.

Before answering architecture, refactor, debugging, dependency, or codebase navigation questions, use the Graphify report, wiki, and graph traversal commands to identify relevant files, modules, god nodes, communities, and relationships before reading raw files or running broad searches.

After modifying code files in this session, run:

```bash
graphify update .