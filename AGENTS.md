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

## mise

This project uses `mise.toml` to pin agent-friendly environment variables and
the normal maintenance tasks.

Rules:
- After Git synchronization, run `mise install` on a fresh machine or whenever
  `mise.toml` changes.
- If mise asks whether to trust the config, inspect `mise.toml` first; trust it
  only when it contains the expected project env vars and task definitions.
- Prefer mise tasks over spelling commands by hand:
  - `mise run syntax` for Python syntax checks.
  - `mise run test` for the unittest suite.
  - `mise run graph-update` after code or graph-relevant documentation changes.
  - `mise run organize` for a normal closeout pass that runs syntax, tests, and
    Graphify refresh.
- When running ad hoc Python or Graphify commands, prefer `mise exec -- <cmd>`
  so `PYTHONUTF8` and `PYTHONDONTWRITEBYTECODE` stay consistent.
- If mise is unavailable, fall back to the explicit command from `mise.toml` and
  report that the mise wrapper was not used.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
