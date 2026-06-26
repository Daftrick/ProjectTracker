# TODOS — ProjectTracker

Deferred items from active reviews. Each entry has a source and context so it can be picked up cold.

---

## v1.5 — Backend

### SQLite full migration (data de negocio)
**Source:** design doc / eng review (2026-06-17)
**Context:** auth.db is SQLite (done). All business data (projects, quotes, tasks, catalog) is still JSON + threading.Lock(). TOCTOU risk acknowledged — at 2-3 users it's near-zero, but the path to v1.5 is clear:
- `catalog_maps()` and `catalog_description_lookup()` in `tracker/catalog.py` are the only entry points to change.
- `quotes.py` lines 167 and 680 (`catalog = load("catalogo")`) also update.
- Admin CRUD in `admin.py` rewrites to SQLite.
- Constrained files (`quote_csv_import.py`, `consistency.py`, `pdfs.py`) need zero changes.
- Estimated effort: +1 day human / ~45 min CC.
**Trigger:** >5 concurrent users, data > 100MB, or complex queries needed.

### Audit log
**Source:** design doc (2026-06-17)
**Context:** `audit_log` table in `auth.db` — who did what, when, to which entity. Schema:
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action TEXT,        -- 'create', 'edit', 'delete', 'approve'
    entity TEXT,        -- 'quote', 'project', 'catalog_item', etc.
    entity_id TEXT,
    detail TEXT,        -- JSON blob with before/after values
    ts TEXT DEFAULT (datetime('now'))
);
```
Wire in as `@log_action` decorator on mutating routes. Zero impact on constrained files.

---

## v1.5 — Deployment

### Dominio propio → Cloudflare Tunnel
**Source:** CEO review (2026-06-17)
**Context:** User has a domain. DNS route:
```bash
cloudflared tunnel route dns projecttracker tracker.<tu-dominio>.com
```
Then update `/etc/cloudflared/config.yml` `hostname:` field.
**Deferred because:** domain access restriction decision not made yet (see below).

### Cloudflare Access (Zero Trust) — team-only visibility
**Source:** CEO review (2026-06-17)
**Context:** App already requires Flask-Login, so random visitors only see the login page. For an extra auth layer (Cloudflare verifies team email BEFORE the login page):
1. Zero Trust Dashboard → Applications → Add Self-Hosted Application
2. Set hostname: `tracker.<tu-dominio>.com`
3. Add policy: email ends in `@<tu-dominio>.com` (or explicit email allowlist)
4. Team members get a Cloudflare Access auth prompt before reaching the app
**Cost:** Free tier up to 50 users (more than enough).
**Trigger:** When team grows or when the login page being publicly visible becomes a concern.

### Healthcheck + alerta si el servicio cae
**Source:** CEO review (2026-06-17)
**Context:** Simple cron that pings localhost:8080 and notifies if down:
```bash
# crontab -e (as projecttracker) — cada 5 min:
*/5 * * * * curl -sf http://localhost:8080/login > /dev/null || \
            curl -d "ProjectTracker caído en $(hostname) — $(date)" \
            ntfy.sh/<tu-topic>
```
Requires `ntfy.sh` free account (or email alternative). Sends push notification to phone.

---

## v2 — Features

### Self-service password change for cotizadores
**Source:** design doc open question #3 (2026-06-17)
**Context:** In v1, admin resets passwords via `/users/<id>/reset-password`. Cotizadores cannot change their own password. Add `/profile/change-password` for non-admin users.

### Cotizador ve solo sus cotizaciones
**Source:** design doc Future section (2026-06-17)
**Context:** Currently all users see all quotes. Add `created_by_user_id` field on quote records and filter `/quotes` by current user for cotizador role. Admin sees all.

### GitHub Actions deploy (alternativa al cron polling)
**Source:** CEO review (2026-06-17)
**Context:** Current auto-deploy is cron polling (git fetch every 5 min). If faster deploys are needed, GitHub Actions + SSH over Cloudflare Access SSH tunnel:
```bash
cloudflared access ssh-gen --hostname ssh.tracker.<tu-dominio>.com
```
Then GitHub Action uses `appleboy/ssh-action` with the tunnel as ProxyCommand. More complex than the cron, but deploys in <1 min instead of <5 min.

---

## C.2 — Revit Schedule CSV importer

**Source:** CEO plan 2026-06-25 (cotizaciones-costos-revit)
**Status:** Diferido — aún no hay schedules de Revit configurados en producción.
**Prerequisito:** Definir y exportar al menos un schedule de Revit con los artículos/familias del proyecto antes de implementar.

### Flujo LDM (prioridad)
- `parse_revit_schedule_csv(file)` — parser puro que lee el CSV de Revit y devuelve lista de `{description, unit, qty}`.
- Formato típico de Revit: fila de título, fila vacía, fila de encabezados, filas de datos. Los encabezados a mapear son `Family and Type` → `description` y `Count` → `qty`. La unidad viene del catálogo o se ingresa manualmente.
- Import inline en la pantalla de nueva LDM (similar al flujo CSV actual de AutoCAD).

### Flujo COT (después del LDM)
- Tabla de mapeo `Family and Type` → `bundle_id`, editable en admin (`/admin/revit-mappings`).
- Al importar: las familias con mapeo → se expanden vía bundles → partidas de cotización. Las sin mapeo → se listan para asignar bundle o agregar directo.
- UI sugerida: al importar, pantalla de revisión en dos columnas (mapeadas / sin mapear) antes de crear la cotización.

### Consideraciones técnicas
- El separador en `Family and Type` de Revit usa ` : ` (espacio-dos-puntos-espacio) entre familia y tipo. Normalizar para el matching.
- Los schedules de Revit pueden tener filas de agrupación (e.g. `Family: Conduit`) que son encabezados de grupo, no datos — filtrar por `Count` vacío o cero.
- Extensión natural de `tracker/csv_import.py` o nuevo `tracker/revit_import.py`.
- Hook en `missing_ldm_items_from_bundles()` para el flujo LDM → COT inverso.
