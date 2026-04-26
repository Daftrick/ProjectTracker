# ProjectTracker — Estado y Versiones

## Versión actual: v8.2 — 25-Apr-2026

---

## Convención de versionado

| Tipo de cambio | Efecto en versión | Ejemplo |
|---|---|---|
| Actualización estética (UI, estilos, layout, textos) | Incrementa el decimal consecutivamente | v5.0 → v5.1 → v5.2 |
| Actualización de funcionalidad (nueva feature, nueva ruta, nueva entidad) | Incrementa el número entero | v5.2 → v6.0 |

Regla: al subir versión mayor, el decimal se reinicia a 0.

**Fuente única de versión en código:** `tracker/domain.py` → constante `APP_VERSION`. Se inyecta a todos los templates via context processor en `tracker/__init__.py`; `base.html` la muestra con `{{ app_version }}`.

**Checklist al cerrar sesión:**
1. Actualizar `APP_VERSION` en `tracker/domain.py`
2. Actualizar `## Versión actual` en este archivo
3. Agregar entradas en `## Historial de cambios recientes`

---

## Stack técnico

| Elemento | Detalle |
|---|---|
| Lenguaje | Python 3.14 (`C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe`) |
| Framework | Flask ≥ 3.0.0 |
| PDF | fpdf2 ≥ 2.7.9 |
| Puerto | **8080** (default) — override con `PROJECT_TRACKER_PORT=N` |
| Debug | `FLASK_DEBUG=1` activa auto-reload |
| Inicio normal | `INICIAR.vbs` — instala deps, espera 3 s, abre `http://localhost:8080` y levanta Flask sin ventana visible |
| Inicio debug | `DEBUG.bat` — ejecuta `app.py` con ventana de consola |
| Reinicio | `REINICIAR.bat` |
| Persistencia | JSON plano en `data/` (sin base de datos) |
| Ruta raíz | `H:\My Drive\Omniious\Claude Code\ProjectTracker\` |

---

## Estructura de archivos

```
ProjectTracker/
├── app.py                      # Punto de entrada mínimo; llama create_app() y corre Flask
├── INICIAR.vbs                 # Lanzador principal sin ventana de consola
├── DEBUG.bat                   # Lanzador con ventana visible para depuración
├── REINICIAR.bat               # Reinicia el servidor
├── requirements.txt            # flask>=3.0.0, fpdf2>=2.7.9
├── ROADMAP_MEJORAS.md          # Backlog de mejoras acordadas
├── VERSIONES.md                # ← Este archivo (fuente de verdad)
│
├── tracker/
│   ├── __init__.py             # create_app(): registra blueprints, filtros Jinja, aliases legacy
│   ├── domain.py               # Catálogo de alcances, statuses, fdate/currency filters, get_progress
│   ├── storage.py              # load/save JSON, new_id (UUID 8 chars), today(), BASE_DIR, DATA_DIR
│   ├── services.py             # Lógica de negocio pura: crear proyectos+tareas, sincronizar alcances, cambiar status
│   ├── catalog.py              # hydrate_quote/ldm, catalog_maps, parse_*_items, quote_type_key/code
│   ├── validators.py           # validate_project_form, validate_quote_form, validate_ldm_form
│   ├── pdfs.py                 # build_quote_pdf, build_ldm_pdf (fpdf2); logo desde Drive o .codex_tmp
│   ├── drive.py                # load/save_config, folder_name, scan_drive_folder, find_delivery_files
│   │                           # Migraciones al arranque: migrate_task_statuses/names/folder_numbers
│   └── routes/
│       ├── __init__.py         # (vacío)
│       ├── projects.py         # Blueprint projects_bp — proyectos, tareas, entregas, ajustes, shutdown
│       ├── quotes.py           # Blueprint quotes_bp — cotizaciones CRUD + PDF
│       ├── materials.py        # Blueprint materials_bp — LDMs CRUD + PDF + API costo
│       └── admin.py            # Blueprint admin_bp — catálogo, proveedores, fichas, equipo
│
├── data/                       # Persistencia JSON (creada automáticamente)
│   ├── projects.json
│   ├── tasks.json
│   ├── deliveries.json
│   ├── quotes.json
│   ├── materiales.json         # LDMs (Listas de Materiales)
│   ├── fichas.json             # Fichas técnicas de equipos
│   ├── catalogo.json           # Catálogo maestro de artículos con precios
│   ├── proveedores.json
│   ├── team.json
│   └── config.json             # drive_projects_path, drive_fichas_path
│
├── templates/                  # Jinja2 (17 templates)
│   ├── base.html               # Layout principal con nav, flash messages, Bootstrap
│   ├── dashboard.html          # Lista proyectos activos/completados/cerrados
│   ├── project_new.html        # Formulario alta proyecto
│   ├── project_detail.html     # Vista detalle con tabs: tareas, docs, cotizaciones, LDMs, fichas
│   ├── quote_project_form.html # Alta/edición cotización (tabs P/G/E)
│   ├── quote_project_detail.html # Vista detalle cotización
│   ├── ldm_form.html           # Alta/edición LDM
│   ├── catalogo.html           # CRUD catálogo maestro
│   ├── proveedores.html        # CRUD proveedores
│   ├── fichas.html             # CRUD fichas técnicas globales
│   ├── team.html               # CRUD equipo
│   ├── settings.html           # Rutas de Drive
│   ├── drive_scan.html         # (parcial) explorador carpeta Drive
│   ├── delivery_preview.html   # Vista previa entrega ZIP
│   ├── tasks.html              # (legacy/auxiliar)
│   ├── task_edit.html          # Edición tarea individual
│   ├── doc_edit.html           # Edición documento
│   ├── documents.html          # Lista documentos
│   └── quotes.html             # Lista cotizaciones global
│
└── tests/
    ├── test_services.py        # unittest: crear proyecto, sync alcances, bloqueos, subtareas obs
    └── test_validators.py      # unittest: formularios vacíos, filas vacías, números inválidos
```

---

## Entidades de datos

### Proyecto (`projects.json`)
```
id, name, clave, client, version, fecha (AAMMDD), alcances[], notes,
folder_num (NNN auto-incremental), closed_at, created_at
```
Carpeta Drive: `IE-{folder_num}-{clave}` (ej. `IE-004-OM001`)

### Tarea (`tasks.json`)
```
id, project_id, alcance (id de alcance), title, source (propia|externa),
external_dep, info_status, status, parent_task_id (null=principal),
notes, history[{from, to, date, note}], created_at
```
Las tareas con `parent_task_id` son subtareas de observación (auto-creadas al pasar a "Observaciones").

### Cotización (`quotes.json`)
```
id, project_id, quote_number, quote_type (General|Preliminar|Extraordinaria),
version, client, project_name, date, currency, tax_rate, items[],
subtotal, tax, total, notes, created_at
```
Item: `{catalog_item_id, description, unit, qty, price, total, catalog_description, section}`

### LDM — Lista de Materiales (`materiales.json`)
```
id, project_id, ldm_number (LDM-{clave}-{NN}), seq,
proveedor, fecha, items[], subtotal_cot, cot_proveedor, notes, created_at
```
Item: `{catalog_item_id, description, unit, qty, precio_cot, total_cot}`

### Catálogo (`catalogo.json`)
```
id, nombre, descripcion, unidad, precio, created_at
```
IDs son UUID de 8 chars en mayúsculas. Artículos se vinculan a items de COT y LDM por `catalog_item_id`.

### Proveedor (`proveedores.json`)
```
id, nombre, contacto, email, telefono, categoria, notas, created_at
```

### Ficha técnica (`fichas.json`)
```
id, code (TIPO-MARCA-MODELO), tipo, marca, modelo, descripcion,
filename (PDF en drive_fichas_path), projects[], notes, created_at
```

### Entrega (`deliveries.json`)
```
id, project_id, date, version, dtype (completa|parcial), zip_name, zip_path,
files_included[], notes
```

### Config (`data/config.json`)
```
drive_projects_path  # ruta local a la carpeta raíz de proyectos en Drive
drive_fichas_path    # ruta local a la carpeta de fichas técnicas PDF
```

---

## Alcances disponibles

| ID | Nombre | Fuente | Bloqueado por |
|---|---|---|---|
| `iluminacion` | IE - Iluminación | externa | — |
| `contactos` | IE - Contactos | propia | — |
| `hvac` | IE - HVAC | externa | — |
| `emergencia` | Sistema de Emergencia | propia | — |
| `fotovoltaico` | Sistema Fotovoltaico | propia | — |
| `subestacion` | Subestación Eléctrica | propia | — |
| `cuadro_cargas` | Cuadro de Cargas | propia | iluminacion, contactos, hvac, emergencia, fotovoltaico, subestacion |
| `diagrama_unifilar` | Diagrama Unifilar | propia | cuadro_cargas |
| `cotizacion` | Cotización | propia | — |

Statuses de tarea: `Pendiente → En progreso → Revisión → Observaciones → Aprobado`

Tipos de ficha: `LUM, CONT, INT, THERM, TFO, PANEL, CABLE, COND, UPS, FV, AC, OTRO`

---

## Funcionalidades implementadas

| Módulo | Feature | Archivo |
|---|---|---|
| Proyectos | CRUD completo, apertura/cierre | `routes/projects.py` |
| Proyectos | Sincronización de alcances post-creación | `routes/projects.py` + `services.py` |
| Tareas | Cambio de status con historial y bloqueos | `routes/projects.py` + `services.py` |
| Tareas | Subtareas automáticas de observación | `services.py:apply_task_status_change` |
| Entregas | Generación de ZIP desde carpeta Drive | `routes/projects.py:create_delivery` |
| Entregas | Servir archivos individuales del proyecto | `routes/projects.py:serve_project_file` |
| Drive | Escaneo y clasificación de archivos por carpeta | `drive.py:scan_drive_folder` |
| Drive | Estado de exportaciones CSV de plano (`Pendiente`, `Importado`, `Desactualizado`) | `drive.py:decorate_csv_plano` |
| Drive | Detección de cotizaciones de proveedor por nombre | `drive.py:provider_quote_status` |
| Drive | Migraciones de datos al arranque | `drive.py:migrate_*` |
| Cotizaciones | CRUD P/G/E, numeración automática | `routes/quotes.py` + `catalog.py` |
| Cotizaciones | Generación de PDF con portada y condiciones | `pdfs.py:build_quote_pdf` |
| Cotizaciones | Hidratación desde catálogo (por ID o por nombre) | `catalog.py:hydrate_quote` |
| Cotizaciones | Secciones opcionales con encabezado y subtotal por sección en formulario, vista y PDF | `validators.py` + `catalog.py` + `pdfs.py` |
| LDMs | CRUD, PDF, set costo manual | `routes/materials.py` |
| LDMs | API JSON para actualizar costo (`/api/ldm/<id>/costo`) | `routes/materials.py:api_ldm_set_costo` |
| Catálogo | CRUD + búsqueda + API JSON (`/api/catalogo`) | `routes/admin.py` |
| Catálogo | Bulk delete vía API (`/api/catalogo/bulk-delete`) | `routes/admin.py` |
| Catálogo | Alta rápida desde formulario de COT/LDM | `routes/admin.py:api_catalogo_add` |
| Proveedores | CRUD + búsqueda | `routes/admin.py` |
| Fichas | CRUD global + vinculación a proyectos | `routes/admin.py` |
| Equipo | CRUD miembros | `routes/admin.py` |
| Ajustes | Rutas Drive (projects y fichas) | `routes/projects.py:settings` |
| App | Shutdown graceful vía POST `/shutdown` | `routes/projects.py:shutdown` |
| Validación | Servidor: proyecto, cotización, LDM | `validators.py` |
| Filtros | `fdate` (YYYY-MM-DD → DD/MM/YYYY), `currency` ($X,XXX.XX) | `domain.py` |

---

## Rutas HTTP

### Blueprint `projects_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET | `/` | `dashboard` | Dashboard de proyectos |
| GET/POST | `/projects/new` | `new_project` | Alta de proyecto |
| GET | `/projects/<id>` | `project_detail` | Detalle con tabs |
| POST | `/projects/<id>/update` | `update_project` | Editar datos del proyecto |
| POST | `/projects/<id>/close` | `close_project` | Cerrar proyecto |
| POST | `/projects/<id>/reopen` | `reopen_project` | Reabrir proyecto |
| POST | `/projects/<id>/delete` | `delete_project` | Eliminar proyecto y dependientes |
| POST | `/projects/<id>/alcances/update` | `update_project_alcances` | Sincronizar alcances |
| POST | `/projects/<id>/tasks/<tid>/status` | `update_task_status` | Cambiar status tarea |
| POST | `/projects/<id>/tasks/<tid>/info` | `update_task_info` | Actualizar source/external_dep |
| POST | `/projects/<id>/tasks/<tid>/note` | `save_task_note` | Guardar notas de tarea |
| POST | `/projects/<id>/deliveries/create` | `create_delivery` | Generar ZIP de entrega |
| POST | `/projects/<id>/deliveries/<did>/delete` | `delete_delivery` | Eliminar registro entrega |
| GET | `/projects/<id>/files/<filename>` | `serve_project_file` | Servir archivo de Drive |
| GET/POST | `/settings` | `settings` | Configurar rutas Drive |
| POST | `/shutdown` | `shutdown` | Detener servidor |

### Blueprint `quotes_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/quote/new` | `new_quote` | Nueva cotización |
| GET/POST | `/projects/<id>/quote/<qid>/edit` | `edit_quote` | Editar cotización |
| GET | `/projects/<id>/quote/<qid>/view` | `view_quote` | Vista de sólo lectura |
| POST | `/projects/<id>/quote/<qid>/delete` | `delete_quote` | Eliminar cotización |
| GET | `/projects/<id>/quote/<qid>/pdf` | `quote_pdf` | Generar PDF en Drive |

### Blueprint `materials_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/ldm/new` | `new_ldm` | Nueva lista de materiales |
| GET/POST | `/projects/<id>/ldm/<lid>/edit` | `edit_ldm` | Editar LDM |
| POST | `/projects/<id>/ldm/<lid>/delete` | `delete_ldm` | Eliminar LDM |
| POST | `/projects/<id>/ldm/<lid>/set_cot` | `set_ldm_cot` | Guardar # cotización proveedor |
| GET | `/projects/<id>/ldm/<lid>/pdf` | `ldm_pdf` | Generar PDF LDM en Drive |
| POST | `/api/ldm/<lid>/costo` | `api_ldm_set_costo` | API JSON: actualizar costo LDM |

### Blueprint `admin_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/catalogo` | `catalogo` | CRUD catálogo maestro |
| POST | `/catalogo/<id>/edit` | `edit_catalogo` | Editar artículo (soporta AJAX) |
| POST | `/catalogo/<id>/delete` | `delete_catalogo` | Eliminar artículo (soporta AJAX) |
| POST | `/api/catalogo/bulk-delete` | `bulk_delete_catalogo` | Eliminar varios artículos |
| GET | `/api/catalogo` | `api_catalogo` | Buscar artículos (JSON, max 30) |
| POST | `/api/catalogo/add` | `api_catalogo_add` | Agregar artículo vía JSON |
| GET/POST | `/proveedores` | `proveedores` | CRUD proveedores |
| POST | `/proveedores/<id>/edit` | `edit_proveedor` | Editar proveedor |
| POST | `/proveedores/<id>/delete` | `delete_proveedor` | Eliminar proveedor |
| GET/POST | `/fichas` | `fichas` | CRUD fichas técnicas |
| POST | `/fichas/<id>/link/<pid>` | `link_ficha` | Vincular ficha a proyecto |
| POST | `/fichas/<id>/unlink/<pid>` | `unlink_ficha` | Desvincular ficha |
| POST | `/fichas/<id>/delete` | `delete_ficha` | Eliminar ficha |
| GET/POST | `/team` | `team` | CRUD equipo |
| POST | `/team/<id>/delete` | `delete_member` | Eliminar miembro |

> **Nota:** `tracker/__init__.py:_register_legacy_endpoint_aliases` registra aliases sin el prefijo del blueprint para que los `url_for(...)` en templates sin prefijo sigan funcionando.

---

## Templates

| Template | Ruta(s) que lo usa |
|---|---|
| `base.html` | Todos (herencia Jinja2) |
| `dashboard.html` | `GET /` |
| `project_new.html` | `GET/POST /projects/new` |
| `project_detail.html` | `GET /projects/<id>` |
| `quote_project_form.html` | `GET/POST /projects/<id>/quote/new` y `.../edit` |
| `quote_project_detail.html` | `GET /projects/<id>/quote/<qid>/view` |
| `ldm_form.html` | `GET/POST /projects/<id>/ldm/new` y `.../edit` |
| `catalogo.html` | `GET/POST /catalogo` |
| `proveedores.html` | `GET/POST /proveedores` |
| `fichas.html` | `GET/POST /fichas` |
| `team.html` | `GET/POST /team` |
| `settings.html` | `GET/POST /settings` |
| `drive_scan.html` | Parcial/incluido en `project_detail.html` |
| `delivery_preview.html` | Vista previa entrega |
| `quotes.html` | Lista global de cotizaciones |
| `tasks.html` | Vista auxiliar de tareas |
| `task_edit.html` | Edición de tarea individual |
| `documents.html` | Lista de documentos |
| `doc_edit.html` | Edición de documento |

---

## Convenciones de nomenclatura

**CSV plano (cuantificaciones AutoCAD):**
```
{CLAVE}-v{VER}-i{CONSEC}-{FECHA}.csv
Ej: OM001-v2-i1-20260420.csv
```
Detectado en `scan_drive_folder` con regex `^{clave}-v\d` (case-insensitive).

**LDM PDF:**
```
LDM-{CLAVE}-{NN}-{FECHA}.pdf
Ej: LDM-OM001-02-260420.pdf
```
`NN` = `ldm.seq` con cero a la izquierda (2 dígitos). `FECHA` = `%y%m%d`.

**Cotización proveedor (CPROV):**
```
CPROV-{CLAVE}-{LDM}-{PROVEEDOR}-{NUM}.pdf
```
Clasificado como `cot_files` en el escáner si empieza con `CPROV-` o `COT-`.

**Cotización cliente (COT):**
```
COT-{CLAVE}-{TIPO}{NN}-{FECHA}.pdf
Ej: COT-OM001-G01-20260420.pdf
```
Donde `TIPO` ∈ {`G`, `P`, `E`} y `NN` es el secuencial de ese tipo dentro del proyecto. `FECHA` formato `YYYYMMDD` (8 dígitos, sin guiones).

**Carpeta del proyecto en Drive:**
```
IE-{folder_num}-{clave}
Ej: IE-004-OM001
```

**Archivos eléctricos:**
- Planos DWG: `IE-{CLAVE}-{VERSION}-{FECHA}.dwg`
- Planos PDF: `IE-{CLAVE}-{VERSION}-{FECHA}.pdf`
- Memorias: `MEM-{CLAVE}-{VERSION}-{FECHA}.pdf`
- XREFs: `XREF-{CLAVE}-{VERSION}-{FECHA}.*`

---

## Tipos de cotización

| Código | Tipo | Descripción | Secuencial |
|---|---|---|---|
| `P` | Preliminar | Estimado antes de tener proyecto ejecutivo definitivo | `len(preliminar_quotes_en_proyecto) + 1` |
| `G` | General | Cotización estándar con alcance completo | `len(general_quotes_en_proyecto) + 1` |
| `E` | Extraordinaria | Trabajos adicionales no contemplados originalmente | `len(extraordinary_quotes_en_proyecto) + 1` |

La función `next_quote_number(project, all_quotes, quote_type, date_str)` en `catalog.py` genera el número automáticamente. El número puede sobreescribirse manualmente en el formulario.

Los aliases aceptados en formularios: `general`, `preliminar`, `extraordinaria`, `extraordinario`.

---

## Historial de cambios recientes

| Fecha | Cambio |
|---|---|
| 2026-04-24 | Refactorización de `app.py` monolito → blueprints (`routes/projects`, `quotes`, `materials`, `admin`) |
| 2026-04-24 | Extracción de lógica de negocio a `tracker/services.py` (crear proyecto+tareas, sync alcances, cambio status) |
| 2026-04-24 | Adición de `tracker/validators.py` con validadores reutilizables para proyecto, cotización y LDM |
| 2026-04-24 | Suite de tests: `tests/test_services.py` y `tests/test_validators.py` |
| 2026-04-24 | Alias de endpoints legacy para mantener compatibilidad de templates existentes |
| 2026-04-24 | Estado verificado: 4 proyectos, 30 tareas, 2 cotizaciones, 8 LDMs, 2 entregas, 458 artículos catálogo, 4 proveedores |
| 2026-04-25 | Creación de `VERSIONES.md` como fuente de verdad para sesiones futuras |
| 2026-04-25 | `project_detail.html` — fix CSS `.drive-file-link` a `display:flex`: ícono de apertura/descarga queda en el mismo renglón que el nombre de archivo en la sección Documentos Drive |
| 2026-04-25 | `tracker/domain.py` — constante `APP_VERSION` como fuente única de versión; inyectada via context processor en `__init__.py`; `base.html` usa `{{ app_version }}` |
| 2026-04-25 | Versión bumped v5.0 → v5.1 (patch: fix UI + mejora de mantenibilidad de versión) |
| 2026-04-25 | Estado de exportaciones CSV en Drive: parseo `{CLAVE}-v{VER}-i{CONSEC}-{FECHA}.csv`, badges de estado en Documentos y pruebas de escaneo |
| 2026-04-25 | Versión bumped v5.1 → v6.0 (feature: estado de CSV de plano) |
| 2026-04-25 | Repositorio Git local sincronizable con GitHub remoto `https://github.com/Daftrick/ProjectTracker.git` (`origin`) |
| 2026-04-26 | Cotizaciones: secciones opcionales para agrupar partidas, con subtotales por sección en vista y PDF sin salto de página forzado |
| 2026-04-26 | Versión bumped v6.0 → v7.0 (feature: secciones en cotizaciones) |
| 2026-04-26 | Lanzadores: `INICIAR.vbs`/`INICIAR.bat` ya no abren otra pestaña ni levantan otra instancia si el puerto 8080 está activo; `REINICIAR.bat` reinicia sólo el proceso dueño del puerto y relanza sin abrir navegador |
| 2026-04-26 | Versión bumped v7.0 → v8.0 (feature: lanzadores idempotentes) |
| 2026-04-25 | Tabla de alcances: filas expandibles con observaciones+notas+historial completo (botón ▼ por alcance) |
| 2026-04-25 | Versión bumped v8.0 → v8.1 (patch: UX tabla alcances) |
| 2026-04-25 | logica_cuantificaciones.txt v2.0 — sincronizado con estado real: secciones COT, scanner CSV, blueprints, esquemas JSON, port 8080, rutas implementadas vs. pendientes |
| 2026-04-25 | Versión bumped v8.1 → v8.2 (patch: documentación interna actualizada) |

---

## Pendientes / En desarrollo

**Alta prioridad:**
- Importación de CSV desde AutoCAD → LDM (diseño completo en `REFERENCIA_ESTRUCTURAS_CSV.txt` y `logica_cuantificaciones.txt` si existe)
- Mostrar errores de validación junto a cada campo en formularios (actualmente sólo como flash messages globales)
- Preservar valores capturados en formularios después de validación fallida

**Media prioridad (ver `ROADMAP_MEJORAS.md`):**
- Filtros y búsqueda en formularios de cotización/LDM (autocompletado de catálogo)
- Confirmaciones más finas en acciones destructivas
- Automatización de consistencia entre cotización y materiales (comparar total COT vs subtotal LDMs)
- Mejoras de codificación/acentos en PDFs generados

**Baja prioridad:**
- Mejor integración con Drive (crear carpetas automáticamente)
- Dashboard de margen por proyecto (total cotizado − costo proveedor)

---

## Cómo ejecutar los tests

```bash
cd "H:\My Drive\Omniious\Claude Code\ProjectTracker"
python -m compileall app.py tracker tests
python -m unittest discover -s tests
```

## Cómo iniciar en modo debug

```bash
cd "H:\My Drive\Omniious\Claude Code\ProjectTracker"
set FLASK_DEBUG=1
python app.py
```
