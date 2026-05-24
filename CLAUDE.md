## Git synchronization

This project is edited from multiple machines, but never intentionally at the
same time. Treat GitHub as the source of truth.

Rules:
- Before reading broadly or editing files, run `git status -sb`.
- If the working tree is clean, update from GitHub before starting work:
  `git pull --rebase origin main`.
- If there are local changes, unmerged paths, or the branch is ahead/behind,
  stop and understand the state before editing. Do not overwrite or discard
  local work silently.
- During work, stage only intentional source, data, documentation, and graph
  artifacts. Do not stage caches, logs, virtualenvs, temporary files, or local
  machine settings unless explicitly requested.
- After making updates, run the relevant checks, update Graphify when required,
  then run `git status -sb` again.
- Before pushing, pull/rebase once more if the remote moved, then commit and
  push the completed work to `origin main`.
- If push/authentication fails, report the exact state and the command the user
  must run from an authenticated terminal.

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
```
