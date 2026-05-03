# ProjectTracker — Estado y Versiones

## Versión actual: v25.1 — 03-May-2026

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
| Excel | openpyxl ≥ 3.1.0 |
| Puerto | **8080** (default) — override con `PROJECT_TRACKER_PORT=N` |
| Debug | `FLASK_DEBUG=1` activa auto-reload |
| Inicio normal | Windows: `INICIAR.vbs` — instala deps, espera 3 s, abre `http://localhost:8080` y levanta Flask sin ventana visible |
| Inicio normal (macOS) | `INICIAR.command` — instala deps, espera 3 s, abre `http://localhost:8080` y levanta Flask en Terminal |
| Inicio debug | `DEBUG.bat` — ejecuta `app.py` con ventana de consola |
| Inicio debug (macOS) | `DEBUG.command` — ejecuta `app.py` con auto-reload y abre la app |
| Reinicio | Windows: `REINICIAR.bat` |
| Reinicio (macOS) | `REINICIAR.command` — detiene el proceso del puerto 8080 y relanza sin abrir otra pestaña del navegador |
| Persistencia | JSON plano en `data/` (sin base de datos) |
| Ruta raíz | `H:\My Drive\Omniious\Claude Code\ProjectTracker\` |

---

## Estructura de archivos

```
ProjectTracker/
├── app.py                      # Punto de entrada mínimo; llama create_app() y corre Flask
├── INICIAR.vbs                 # Lanzador principal Windows sin ventana de consola
├── INICIAR.command             # Lanzador principal macOS
├── DEBUG.command               # Lanzador debug macOS
├── DEBUG.bat                   # Lanzador con ventana visible para depuración
├── REINICIAR.command           # Reinicio macOS
├── REINICIAR.bat               # Reinicia el servidor
├── requirements.txt            # flask>=3.0.0, fpdf2>=2.7.9, openpyxl>=3.1.0
├── ROADMAP_MEJORAS.md          # Backlog de mejoras acordadas
├── VERSIONES.md                # ← Este archivo (fuente de verdad)
│
├── tracker/
│   ├── __init__.py             # create_app(): registra blueprints, filtros Jinja, aliases legacy
│   ├── domain.py               # Catálogo de alcances, statuses, fdate/currency filters, get_progress
│   ├── storage.py              # load/save JSON, new_id (UUID 8 chars), today(), BASE_DIR, DATA_DIR
│   ├── services.py             # Lógica de negocio pura: crear proyectos+tareas, sincronizar alcances, cambiar status
│   ├── catalog.py              # hydrate_quote/ldm, catalog_maps, parse_*_items, quote_type_key/code, migrate_catalog_fields
│   ├── catalog_search.py       # tokenize, match_item, filter_catalog, list_categories (búsqueda por tokens AND + categoría)
│   ├── consistency.py          # compute_consistency, compare_items por catalog_item_id (margen 30%/0%)
│   ├── csv_import.py           # Parser CSV para importar exportaciones LISP como LDM
│   ├── validators.py           # validate_project_form, validate_quote_form, validate_ldm_form
│   ├── pdfs.py                 # build_quote_pdf, build_ldm_pdf (fpdf2); logo desde Drive o .codex_tmp
│   ├── drive.py                # load/save_config, folder_name, scan_drive_folder, find_delivery_files
│   │                           # Migraciones al arranque: migrate_task_statuses/names/folder_numbers
│   └── routes/
│       ├── __init__.py         # (vacío)
│       ├── projects.py         # Blueprint projects_bp — proyectos, tareas, entregas, ajustes, shutdown
│       ├── quotes.py           # Blueprint quotes_bp — cotizaciones CRUD + PDF + Excel
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
    ├── test_drive.py           # unittest: escaneo Drive, CSVs de plano y archivos ignorados
    ├── test_csv_import.py      # unittest: parser CSV para LDM
    ├── test_validators.py      # unittest: formularios vacíos, filas vacías, números inválidos
    ├── test_catalog_search.py         # unittest: tokens AND, categoría, list_categories, smoke /api/catalogo
    ├── test_consistency.py            # unittest: agregaciones, umbrales 30%/0%, issues por artículo, bundles, reglas, ignorados
    ├── test_bundles.py                # unittest: normalización, versiones, expansión de bundles
    ├── test_comparison_rules.py       # unittest: reglas activas, conversión COT/LDM, tolerancia
    ├── test_comparison_ignored.py     # unittest: artículos ignorados no generan issues pero conservan costo
    ├── test_admin_bundles_routes.py   # unittest: rutas Admin bundles y reglas
    ├── test_admin_forms.py            # unittest: validación inline y preservación de formularios administrativos
    ├── test_project_view.py           # unittest: contexto de project_detail (tareas, fichas, márgenes)
    ├── test_deletions.py              # unittest: cascadas al eliminar proyecto y limpieza de referencias catálogo
    ├── test_form_models.py            # unittest: view-models de cotización y LDM desde formularios inválidos
    └── test_project_detail_bundle_ui.py  # unittest: render de la sección técnica de bundles en project_detail
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
notes, checklist[{id, text, done, done_at}], history[{from, to, date, note}], created_at
```
Las tareas con `parent_task_id` son subtareas de observación (auto-creadas al pasar a "Observaciones"). Pueden incluir `checklist` para dar seguimiento puntual y marcar cumplimiento por ítem.

### Cotización (`quotes.json`)
```
id, project_id, quote_number, quote_type (General|Preliminar|Extraordinaria),
version, client, project_name, date, currency, tax_rate, items[],
subtotal, tax, total, notes, project_basis_note, created_at
```
Item: `{catalog_item_id, description, unit, qty, price, total, catalog_description, section}`

### LDM — Lista de Materiales (`materiales.json`)
```
id, project_id, ldm_number (LDM-{clave}-{NN}), seq,
proveedor, fecha, items[], subtotal_cot, cot_proveedor, notes,
csv_origen, csv_sources[], created_at
```
Item: `{catalog_item_id, description, unit, qty, precio_cot, total_cot, qty_csv, qty_editada, origen}`

### Catálogo (`catalogo.json`)
```
id, nombre, descripcion, unidad, precio, categoria, created_at
```
IDs son UUID de 8 chars en mayúsculas. Artículos se vinculan a items de COT y LDM por `catalog_item_id`. El campo `categoria` es libre (con datalist sugerido) y se migra suavemente vía `migrate_catalog_fields()` al arranque.

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
| Drive | Escaneo y clasificación de archivos por carpeta; ignora `.bak`, `.dwl`, `.dwl2` | `drive.py:scan_drive_folder` |
| Drive | Estado de exportaciones CSV de plano (`Pendiente`, `Importado`, `Desactualizado`) | `drive.py:decorate_csv_plano` |
| Drive | Detección de cotizaciones de proveedor por nombre | `drive.py:provider_quote_status` |
| Drive | Migraciones de datos al arranque | `drive.py:migrate_*` |
| Cotizaciones | CRUD P/G/E, numeración automática | `routes/quotes.py` + `catalog.py` |
| Cotizaciones | Generación de PDF con portada y condiciones | `pdfs.py:build_quote_pdf` |
| Cotizaciones | Exportación Excel (.xlsx): guarda el archivo directamente en la carpeta Drive del proyecto (igual que los PDFs); encabezado con número/cliente/proyecto/fecha/moneda, artículos con nombre/unidad/cantidad/precios/totales, subtotales por sección cuando aplica, cierre con IVA y TOTAL en negrita | `routes/quotes.py:quote_excel` + `_build_quote_workbook` |
| Cotizaciones | Hidratación desde catálogo (por ID o por nombre) | `catalog.py:hydrate_quote` |
| Cotizaciones | Secciones opcionales con encabezado y subtotal por sección en formulario, vista y PDF | `validators.py` + `catalog.py` + `pdfs.py` |
| Cotizaciones | Nota base de proyecto en portada del PDF según tipo: preliminar sin nota, general con último DWG, extraordinaria con nota manual | `routes/quotes.py` + `drive.py:latest_dwg_stem` + `pdfs.py` |
| LDMs | CRUD, PDF, set costo manual | `routes/materials.py` |
| LDMs | Importación CSV de plano → nueva LDM con revisión previa, vínculo `csv_origen` y bloqueo de reimportación del mismo CSV. Auto-vinculación de `catalog_item_id` por nombre exacto (case-insensitive) al importar. Preview muestra badge verde por artículo vinculado y hint ámbar por artículo sin vincular. | `routes/materials.py:import_ldm_csv` + `csv_import.py` |
| LDMs | API JSON para actualizar costo (`/api/ldm/<id>/costo`) | `routes/materials.py:api_ldm_set_costo` |
| Catálogo | CRUD + búsqueda por tokens AND (sin acentos) + filtro por categoría + API JSON (`/api/catalogo`, `/api/catalogo/categorias`) | `routes/admin.py` + `catalog_search.py` |
| Catálogo | Bulk delete vía API (`/api/catalogo/bulk-delete`) | `routes/admin.py` |
| Catálogo | Alta rápida desde formulario de COT/LDM (acepta categoría) | `routes/admin.py:api_catalogo_add` |
| Catálogo | Migración suave que agrega campo `categoria=''` a artículos existentes al arranque | `catalog.py:migrate_catalog_fields` |
| COT/LDM | Filtro inline de partidas capturadas: caja con tokens AND, busca en descripción/unidad/sección, oculta filas no machean sin afectar el submit | `quote_project_form.html` + `ldm_form.html` |
| Consistencia | Reporte automatizado COT vs LDM por proyecto: cotización General más reciente vs suma de costos LDM, agregación por `catalog_item_id`, margen %, status (ok/warning/critical) con umbrales 30%/0% | `consistency.py` |
| Consistencia | KPI clickeable en cada card del dashboard con margen % y badge de estado | `dashboard.html` |
| Consistencia | Tab dedicado en detalle de proyecto con totales, badges de issues y tabla por artículo (qty COT vs LDM, precio venta vs costo promedio ponderado, margen unitario, etiquetas missing_in_ldm/missing_in_cot/qty_mismatch/below_cost) | `project_detail.html` |
| Proveedores | CRUD + búsqueda | `routes/admin.py` |
| Fichas | CRUD global + vinculación a proyectos | `routes/admin.py` |
| Equipo | CRUD miembros | `routes/admin.py` |
| Ajustes | Rutas Drive (projects y fichas) | `routes/projects.py:settings` |
| Documentos | CSVs de plano en pestaña Documentos — columna LDM lista archivos `{clave}-v{N}-i{N}-{fecha}.csv` con nombre, fecha, tamaño y botón Descargar; aviso vacío cuando no hay archivos | `routes/projects.py` + `project_detail.html` |
| Observaciones | Guardar texto de observación existente vía ruta dedicada | `routes/projects.py:update_observation` |
| Observaciones | Toggle de ítem de checklist de observación vía ruta dedicada | `routes/projects.py:toggle_checklist_item` |
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
| POST | `/projects/<id>/observations/<obs_id>/update` | `update_observation` | Guardar texto de observación existente |
| POST | `/projects/<id>/observations/<obs_id>/checklist/<item_id>` | `toggle_checklist_item` | Toggle ítem de checklist de observación |

### Blueprint `quotes_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/quote/new` | `new_quote` | Nueva cotización |
| GET/POST | `/projects/<id>/quote/<qid>/edit` | `edit_quote` | Editar cotización |
| GET | `/projects/<id>/quote/<qid>/view` | `view_quote` | Vista de sólo lectura |
| POST | `/projects/<id>/quote/<qid>/delete` | `delete_quote` | Eliminar cotización |
| GET | `/projects/<id>/quote/<qid>/pdf` | `quote_pdf` | Generar PDF en Drive |
| GET | `/projects/<id>/quote/<qid>/excel` | `quote_excel` | Descargar Excel (.xlsx) |

### Blueprint `materials_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/ldm/new` | `new_ldm` | Nueva lista de materiales |
| GET/POST | `/projects/<id>/ldm/import/<filename>` | `import_ldm_csv` | Importar CSV de plano como nueva LDM |
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
| GET | `/api/catalogo` | `api_catalogo` | Buscar artículos (JSON, max 50, tokens AND + filtro `categoria`) |
| GET | `/api/catalogo/categorias` | `api_catalogo_categorias` | Lista única de categorías existentes (JSON) |
| POST | `/api/catalogo/add` | `api_catalogo_add` | Agregar artículo vía JSON (acepta `categoria`) |
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
| `ldm_form.html` | `GET/POST /projects/<id>/ldm/new`, `.../ldm/import/<filename>` y `.../edit` |
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
El contenido importable acepta encabezados `description,unit,qty` o `descripcion,unidad,cantidad`
con separador coma o punto y coma. Filas de metadatos opcionales: `#proveedor`, `#fecha`, `#proyecto_clave`.

**Archivos ignorados por escáner Drive:**
```
*.bak
*.dwl
*.dwl2
*.zip
```

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

Reglas de portada PDF:
- Preliminar: no muestra nota base.
- General: muestra `Cotización realizada con base en el proyecto: {último DWG sin extensión}` usando el `.dwg` más reciente/versionado en la carpeta Drive del proyecto.
- Extraordinaria: muestra la misma leyenda con el texto capturado manualmente en el formulario.

---

## Historial de cambios recientes

| Fecha | Cambio |
|---|---|
| 2026-05-03 | Sistema completo de auditoría de catálogo eliminado: función `audit_deleted_catalog_items()` para analizar cotizaciones y LDMs con referencias obsoletas |
| 2026-05-03 | Gestión visual de catálogo eliminado: badges con fecha de eliminación, indicadores visuales en filas problemáticas, estados diferenciados (sin resolver/preservado/normal) |
| 2026-05-03 | Flujo de tres acciones para catálogo eliminado: preservar histórica (conservar referencia), reconectar a nuevo artículo, purgar definitivamente |
| 2026-05-03 | Página de auditoría dedicada `/audit/deleted-catalog`: dashboard con métricas, tabla detallada por documento, recomendaciones de flujo de trabajo |
| 2026-05-03 | Funciones backend: `preserve_deleted_catalog_item_in_record()`, `restore_deleted_catalog_item_in_record()`, `purge_deleted_catalog_items_from_record()` |
| 2026-05-03 | UI mejorada: botones de acción con iconos descriptivos, modales de confirmación, JavaScript para operaciones AJAX en formularios de cotización |
| 2026-05-03 | Enlace en menú principal: "Auditoría Catálogo" en sección Sistema del sidebar |
| 2026-05-03 | Versión bumped v23.1 → v24.0 (feature: sistema completo de auditoría y gestión de catálogo eliminado) |
| 2026-04-24 | Refactorización de `app.py` monolito → blueprints (`routes/projects`, `quotes`, `materials`, `admin`) |
| 2026-04-24 | Extracción de lógica de negocio a `tracker/services.py` (crear proyecto+tareas, sync alcances, cambio status) |
| 2026-04-24 | Adición de `tracker/validators.py` con validadores reutilizables para proyecto, cotización y LDM |
| 2026-04-24 | Suite de tests: `tests/test_services.py` y `tests/test_validators.py` |
| 2026-04-24 | Alias de endpoints legacy para mantener compatibilidad de templates existentes |
| 2026-04-24 | Estado verificado: 4 proyectos, 30 tareas, 2 cotizaciones, 8 LDMs, 2 entregas, 458 artículos catálogo, 4 proveedores |
| 2026-04-25 | Creación de `VERSIONES.md` como fuente de verdad para sesiones futuras |
| 2026-04-25 | `project_detail.html` — fix CSS `.drive-file-link` a `display:flex`: ícono de apertura/descarga queda en el mismo renglón que el nombre de archivo en la sección Documentos Drive |
| 2026-05-03 | **Drive — integración mejorada (v24.1)**: `scan_drive_folder` diferencia errores por tipo (`unconfigured`/`root_missing`/`folder_missing`) con campo `error_type`; detecta archivos base faltantes (`missing_base`: IE-*.dwg/.pdf, MEM-*, COT-*); fix de bug de clave de caché (usaba `projects_root` en lugar de la ruta específica del proyecto, causando colisiones entre proyectos); reset de pattern `csv_plano` por clave para evitar match cruzado entre proyectos. Nueva función `create_project_folder()`. Nuevo endpoint `POST /projects/<id>/drive/create-folder`. `project_detail.html`: el bloque de error Drive distingue los tres tipos con iconos/colores diferenciados y muestra botón "Crear carpeta en Drive" cuando `error_type == folder_missing`. Cuando el scan es exitoso, muestra alerta con badges de archivos base faltantes. `settings.html`: nuevo panel de estado de rutas (✓/✗) que valida si las rutas existen en disco, tanto en GET como en POST con errores. `routes/projects.py`: settings GET calcula y pasa `path_status` al template. |
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
| 2026-04-26 | Observaciones: checklist opcional por subtarea, marcado de cumplimiento desde el desglose de alcance y cierre/reapertura automática según puntos cumplidos |
| 2026-04-26 | Versión bumped v8.2 → v9.0 (feature: checklist de observaciones) |
| 2026-04-26 | Observaciones existentes: botón para generar checklist desde la nota y generación automática desde la nota si el checklist manual queda vacío |
| 2026-04-26 | Versión bumped v9.0 → v9.1 (patch: generación visible de checklist) |
| 2026-04-26 | Observaciones: se elimina generación de checklist desde nota, se agrega edición de observaciones existentes, nuevas observaciones incrementan `Obs. #N` aun si el alcance ya está en Observaciones y el contador del dashboard mide observaciones activas |
| 2026-04-26 | Versión bumped v9.1 → v9.2 (patch: edición manual de observaciones) |
| 2026-04-26 | Bug fix: botón "Guardar" en modal editar observación no respondía en móvil — se añadió `modal-dialog-scrollable` y se reemplazó listener `show.bs.modal` (relatedTarget frágil en móvil) por click listeners directos en `.obs-edit-btn` |
| 2026-04-26 | Versión bumped v9.2 → v9.3 (patch: fix botón guardar observación en móvil) |
| 2026-04-26 | CSVs de plano en pestaña Documentos: columna LDM muestra archivos `{clave}-v{N}-i{N}-{fecha}.csv` con nombre, fecha, tamaño y botón Descargar; aviso vacío cuando no hay archivos |
| 2026-04-26 | Nuevas rutas Flask: `POST /projects/<id>/observations/<obs_id>/update` y `POST /projects/<id>/observations/<obs_id>/checklist/<item_id>` para guardar observaciones y hacer toggle de checklist |
| 2026-04-26 | Bug fix: modal editar observación no respondía en Chrome móvil — modales movidos fuera de `#main` (CSS transition en el contenedor rompía z-index en WebKit), JS cambiado de `click` listeners en elementos ocultos a evento `show.bs.modal` |
| 2026-04-26 | Versión bumped v9.3 → v10.0 (feature: CSVs de plano en Documentos + rutas de observaciones/checklist) |
| 2026-04-27 | Importación CSV→LDM: parser `tracker/csv_import.py`, ruta `GET/POST /projects/<id>/ldm/import/<filename>`, botón en Documentos y dropdown en Materiales para crear LDM desde CSV detectado |
| 2026-04-27 | Drive scanner: se ignoran archivos auxiliares de AutoCAD `*.bak`, `*.dwl`, `*.dwl2` para que no aparezcan en Documentos/Otros |
| 2026-04-27 | Tests: parser CSV de LDM y escaneo Drive con archivos auxiliares ignorados |
| 2026-04-27 | Versión bumped v10.0 → v11.0 (feature: importación CSV→LDM) |
| 2026-04-27 | PDFs de cotización: nota base después del título según tipo; generales usan el último `.dwg` sin extensión y extraordinarias permiten nota manual desde la app |
| 2026-04-27 | Versión bumped v11.0 → v12.0 (feature: nota base de proyecto en PDF de cotización) |
| 2026-04-27 | macOS: nuevo lanzador `INICIAR.command` para abrir Project Tracker con doble clic, instalar dependencias, evitar instancias duplicadas y abrir el navegador |
| 2026-04-27 | Versión bumped v12.0 → v13.0 (feature: lanzador nativo para macOS) |
| 2026-04-27 | macOS: nuevos lanzadores `DEBUG.command` y `REINICIAR.command` para depuración y reinicio, alineados con el flujo ya disponible en Windows |
| 2026-04-27 | Versión bumped v13.0 → v14.0 (feature: paridad de lanzadores Windows/macOS) |
| 2026-04-27 | `pdfs.py:build_ldm_pdf` — rediseño del PDF de Listas de Materiales adoptando la estética del PDF de cotizaciones (banner negro + logo, paleta navy/ink/muted, header de páginas y tabla con marca/detalle del catálogo). Layout colapsado en una sola hoja: banner con logo + bloque PROYECTO/PROVEEDOR/FECHA + Detalle de partidas + tabla. Sin portada separada, sin caja de totales, sin alcance, sin términos y condiciones, sin firma. Subtotal cotizado se conserva sólo cuando los items traen precios. |
| 2026-04-27 | Versión bumped v14.0 → v14.1 (patch: rediseño estético del PDF de LDM) |
| 2026-04-27 | `pdfs.py:build_ldm_pdf` — banner del logo extendido a 56 mm con dimensiones explícitas (`LOGO_W=60`, `LOGO_H=40`) y centrado horizontal/vertical calculado automáticamente en lugar de coordenadas mágicas |
| 2026-04-27 | `pdfs.py:build_ldm_pdf` — márgenes laterales reducidos a 2.5 mm vía constante `LATERAL_MARGIN`; header/footer/info/tabla derivan de `pdf.l_margin` y `content_width`, las columnas (incluyendo descripción) recalculan ancho automáticamente |
| 2026-04-27 | `pdfs.py:build_ldm_pdf` — columnas UNIDAD y CANT. con ancho compartido (`UNIT_QTY_W=18`) y texto centrado tanto en header como en valores |
| 2026-04-27 | Versión bumped v14.1 → v14.2 (patch: pulido del PDF de LDM — banner, márgenes y columnas) |
| 2026-04-27 | `pdfs.py:build_quote_pdf` — paridad con LDM: márgenes laterales a 2.5 mm vía `LATERAL_MARGIN`, header/footer/scope/tabla derivados de `pdf.l_margin` y `content_width`. Columnas UNIDAD/CANT. con ancho compartido (`UNIT_QTY_W=18`) y texto centrado; descripción absorbe el ancho extra automáticamente. Constantes `NUM_W`, `PRICE_W` para mantener la suma == ancho de contenido. La portada (coordenadas absolutas 16/178) se conserva intacta. |
| 2026-04-27 | Versión bumped v14.2 → v14.3 (patch: paridad de márgenes y columnas en PDF de cotizaciones) |
| 2026-04-27 | `pdfs.py:build_quote_pdf` — columnas P. UNIT. e IMPORTE con ancho compartido (`PRICE_W=28`) y texto centrado (header y valores); UNIDAD/CANT. reducidas a `UNIT_QTY_W=16` para dar aire. Subtotal de sección también centrado. |
| 2026-04-27 | `pdfs.py:build_quote_pdf` — reordenado: el bloque "Alcance" se renderiza antes que el título "Detalle de partidas" para que el contexto preceda al desglose. |
| 2026-04-27 | Versión bumped v14.3 → v14.4 (patch: ajustes finos en columnas y orden de secciones del PDF de cotizaciones) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — ajuste de tipografía de la tabla de partidas: nombre del artículo a 10 pt, marca y detalle a 7.5 pt, header a 8 pt, datos numéricos a 10 pt. Line-heights recalibrados (5.0 / 3.7 / 3.7) y fila mínima 14 mm. `PRICE_W` aumentado a 30 mm para alojar valores en 10 pt centrados. |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — `LATERAL_MARGIN` subido de 2.5 mm a 5 mm en ambos PDFs. |
| 2026-04-27 | Versión bumped v14.4 → v14.5 (patch: tipografía y márgenes de tabla de partidas, ambos PDFs) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — bug fix: descripciones largas se renderizaban con marca/detalle encima de la segunda línea del título. Causa: `wrap_text` calculaba el wrap con el font activo (8.6pt) en lugar del font de render (10pt B), subestimando líneas. Fix: setear font correcto antes de `wrap_text` para que las métricas coincidan con el render real. |
| 2026-04-27 | Versión bumped v14.5 → v14.6 (patch: fix overlap de marca sobre título multi-línea) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — fix definitivo de altura de filas: el conteo de líneas para `row_h` ahora viene de `multi_cell(..., dry_run=True, output="LINES")`, garantizando que coincida con el render real (mi `wrap_text` pre-wrappea con conectores pero fpdf2 puede repartir distinto al renderizar). Se cambia `align="L"` para evitar artefactos de justificación, y el cursor entre bloques (título → marca → detalle) usa `pdf.get_y()` en lugar de coordenadas calculadas. |
| 2026-04-27 | Versión bumped v14.6 → v14.7 (patch: dry_run para conteo exacto de líneas y align="L" en descripciones) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — bug fix: textos con `|` ahora pegan el separador a los grupos inmediatos de ambos lados (`Delgada | 27 [mm]`) usando espacios no rompibles sólo donde hace falta, evitando que fpdf2 parta palabras como "Delgada" o deje `|` suelto al final/inicio de línea. El wrap sin `|` conserva cortes normales por grupos. También se cambió la fecha vacía de `—` a `-` para evitar errores de Helvetica. |
| 2026-04-27 | Versión bumped v14.7 → v14.8 (patch: fix de saltos raros alrededor de `|` en PDFs) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — columnas compactadas para ampliar `DESCRIPCION`: cotizaciones pasan a `#=8`, `UNIDAD/CANT.=14`, `P.UNIT./IMPORTE=28`; LDM pasa a `#=8`, `UNIDAD/CANT.=15`, `P.UNIT./IMPORTE=28`. La descripción gana ancho sin volver a justificar texto a la derecha. |
| 2026-04-27 | Versión bumped v14.8 → v14.9 (patch: más ancho útil para nombres en PDFs) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — ajuste fino de wrap en descripciones: se protegen unidades compuestas como `120/240 [V]`, `240-600 [V]`, `35 [mm] (1 1/4")` y configuraciones `3F - 4H` para evitar cortes entre valor/unidad o guiones colgados. |
| 2026-04-27 | Versión bumped v14.9 → v14.10 (patch: agrupación de unidades compuestas en PDFs) |
| 2026-04-27 | `pdfs.py` (LDM y cotizaciones) — pre-wrap propio para la columna `DESCRIPCION`: calcula líneas con el ancho real de columna y el font activo antes de llamar a `multi_cell`, moviendo el grupo anterior junto al `|` y al siguiente grupo cuando hace falta. Evita cortes internos como `Interrupt/or Principal` sin volver a crear bloques no rompibles demasiado largos. |
| 2026-04-27 | Versión bumped v14.10 → v14.11 (patch: pre-wrap fino de separadores `|` en PDFs) |
| 2026-04-28 | Formularios principales: alta de proyecto, cotizaciones y LDMs ahora conservan la captura cuando falla validación y muestran errores junto al campo o sección correspondiente |
| 2026-04-28 | Versión bumped v14.11 → v14.12 (patch: UX de validación inline y preservación de formularios) |
| 2026-04-28 | Arquitectura: nuevo `tracker/form_models.py` para reconstruir view-models de cotizaciones y LDMs desde formularios inválidos; `routes/quotes.py` y `routes/materials.py` quedan más delgados |
| 2026-04-28 | Versión bumped v14.12 → v14.13 (patch: extracción de form view-models) |
| 2026-04-28 | Formularios administrativos: catálogo, proveedores, fichas, equipo y ajustes ahora muestran errores inline y conservan captura cuando falla validación; ajustes valida rutas locales antes de guardar |
| 2026-04-28 | Tests: `tests/test_admin_forms.py` cubre preservación de captura y errores inline en formularios administrativos |
| 2026-04-28 | Versión bumped v14.13 → v14.14 (patch: validación inline en formularios administrativos) |
| 2026-04-28 | Arquitectura: nuevo `tracker/project_view.py` para construir el contexto completo de `project_detail`; `routes/projects.py` queda más delgado y enfocado en HTTP |
| 2026-04-28 | Tests: `tests/test_project_view.py` cubre agrupación de tareas/subtareas, fichas vinculadas, cierre permitido y cálculos de margen del detalle de proyecto |
| 2026-04-28 | Versión bumped v14.14 → v14.15 (patch: extracción del view-model de detalle de proyecto) |
| 2026-04-28 | Eliminaciones seguras: nuevo `tracker/deletions.py`; borrar proyectos elimina datos dependientes y desvincula fichas, borrar artículos de catálogo limpia `catalog_item_id` en cotizaciones/LDMs para evitar referencias a objetos eliminados |
| 2026-04-28 | Confirmaciones destructivas: borrar proyecto muestra conteos de tareas, cotizaciones, LDMs, entregas y vínculos a fichas afectados; catálogo avisa cuando limpia referencias en documentos existentes |
| 2026-04-28 | Tests: `tests/test_deletions.py` cubre cascadas de proyecto y limpieza de referencias de catálogo |
| 2026-04-28 | Versión bumped v14.15 → v14.16 (patch: eliminaciones seguras y limpieza de referencias huérfanas) |
| 2026-04-28 | Catálogo histórico: borrar artículos del catálogo ahora desconecta `catalog_item_id` en cotizaciones/LDMs, pero conserva una copia `deleted_catalog_item` del artículo eliminado para mantener el renglón visible sin referenciar objetos inexistentes |
| 2026-04-28 | UI COT/LDM: los renglones originados en catálogo eliminado se muestran marcados en rojo; el detalle del proyecto muestra badges de alerta por documento y agrega acción `Purgar` para eliminar por completo esos renglones cuando se decida |
| 2026-04-28 | Backend: nuevas rutas `purge_quote_deleted_catalog_items` y `purge_ldm_deleted_catalog_items`; recalculan totales/subtotales después de purgar partidas o artículos marcados como catálogo eliminado |
| 2026-04-28 | Tests: `tests/test_deletions.py`, `tests/test_form_models.py` y `tests/test_validators.py` cubren snapshot histórico, preservación en formularios/validación y purga definitiva de renglones marcados |
| 2026-04-28 | Versión bumped v14.16 → v14.17 (patch: conservar items de catálogo borrado y permitir purga definitiva) |
| 2026-04-28 | Catálogo: nuevo módulo `tracker/catalog_search.py` (puro, sin I/O) con `tokenize`, `match_item`, `filter_catalog`, `list_categories`. Búsqueda por tokens AND, sin acentos, case-insensitive, indexada sobre nombre + descripción + categoría |
| 2026-04-28 | Catálogo: campo libre `categoria` en artículos. Migración suave `migrate_catalog_fields()` corre al arranque y agrega `categoria=''` a artículos existentes sin tocar otros campos |
| 2026-04-28 | API `/api/catalogo` ahora acepta `q` (tokens AND) y `categoria`; tope subido de 30 a 50 (`API_CATALOG_LIMIT`). Nueva ruta `GET /api/catalogo/categorias` para datalists/filtros. POST `/api/catalogo/add` acepta `categoria` |
| 2026-04-28 | UI catálogo: columna `Categoría` con badge, selector de filtro, datalist global con categorías existentes; modales de nuevo/editar incluyen el campo. Render alfabético siempre |
| 2026-04-28 | COT y LDM: filtro inline en el card-header de partidas (tokens AND, busca en descripción/unidad/sección, sin acentos). Las filas ocultas mantienen su input para el submit; contador `(X/Y visibles)` y botón limpiar |
| 2026-04-28 | Tests: `tests/test_catalog_search.py` cubre tokenización, match con tokens y categoría, filtrado, deduplicación de categorías y smoke de la API JSON |
| 2026-04-28 | Versión bumped v14.17 → v15.0 (feature: búsqueda por tokens, categoría general en catálogo, filtro inline de partidas en COT/LDM) |
| 2026-04-28 | Consistencia: nuevo módulo `tracker/consistency.py` (puro, sin I/O) con `pick_active_quote`, `aggregate_quote_items`, `aggregate_ldm_items`, `compare_items`, `compute_consistency`. Selecciona la cotización General más reciente como base; agrega artículos por `catalog_item_id` a través de todas las LDMs del proyecto; computa margen % y status discreto (ok/warning/critical/no_data) con umbrales 30%/0%. Detecta issues por artículo: missing_in_ldm, missing_in_cot, qty_mismatch, below_cost; severidad ordenada en la salida |
| 2026-04-28 | `project_view.py` ahora inyecta `consistency` al contexto del detalle de proyecto; `routes/projects.py:dashboard` carga catálogo + cotizaciones + LDMs hidratados una sola vez y llama `compute_consistency` por proyecto evitando N+1 |
| 2026-04-28 | Dashboard: nueva KPI clickeable por card de proyecto activo (margen %, badge ok/warning/critical/no_data) que enlaza directo a `#tab-consistencia` |
| 2026-04-28 | Detalle de proyecto: nuevo tab "Consistencia" con encabezado de KPIs (subtotal cotizado, costo proveedor, margen abs, margen %), badges de issues y tabla por artículo de catálogo con qty COT/LDM, precio venta, costo promedio ponderado, margen unitario y etiquetas de problema. El tab muestra mini-badge de severidad cuando hay critical/warning |
| 2026-04-28 | Tests: `tests/test_consistency.py` cubre umbrales 30%/0%, selección de General activa con fallback, agregación por `catalog_item_id` cruzando LDMs, detección de los 4 tipos de issue, escenarios sin COT/sin LDM y filtrado por `project_id` |
| 2026-04-28 | Versión bumped v15.0 → v16.0 (feature: automatización de consistencia COT vs LDM por artículo de catálogo, KPIs en dashboard y tab dedicado en detalle de proyecto) |
| 2026-04-28 | Hotfix detalle de proyecto: el tab de consistencia usa `cn['items']` en lugar de `cn.items` para evitar que Jinja lea el método interno del diccionario y lance `TypeError: 'builtin_function_or_method' object is not iterable` |
| 2026-04-28 | Versión bumped v16.0 → v16.1 (patch: corrección de render en tab Consistencia) |
| 2026-04-28 | Configuración Drive multiplataforma: `config.json` ahora conserva rutas independientes para Windows/macOS/Linux (`drive_projects_path_windows`, `drive_projects_path_macos`, etc.) y la app resuelve automáticamente la ruta activa según el sistema actual |
| 2026-04-28 | Ajustes: la pantalla de Google Drive muestra "Este equipo" y las rutas guardadas por sistema, permitiendo que Windows use `H:\...` y macOS use `/Users/.../Library/CloudStorage/...` sin sobrescribirse |
| 2026-04-28 | Escaneo/exportación: Documentos, entregas ZIP, PDFs de COT/LDM, importación CSV y descarga de archivos de proyecto usan la ruta Drive activa del sistema operativo actual |
| 2026-04-28 | Tests: `tests/test_drive.py` cubre convivencia de rutas Windows/macOS y resolución de rutas activas por plataforma |
| 2026-04-28 | Versión bumped v16.1 → v16.2 (patch: convivencia de rutas Drive entre Windows y macOS) |
| 2026-04-28 | Cotizaciones: nuevo botón **Excel** en la tabla de cotizaciones del detalle de proyecto y en la vista de detalle de cotización; genera y descarga un `.xlsx` con openpyxl — encabezado (número, cliente, proyecto, fecha, moneda), tabla de artículos (nombre, unidad, cantidad, precio unitario, total), subtotales por sección cuando aplica, y cierre con Subtotal / IVA / TOTAL en negrita. Sin colores ni tipografías especiales |
| 2026-04-28 | `requirements.txt` — agregada dependencia `openpyxl>=3.1.0` |
| 2026-04-28 | Versión bumped v16.2 → v16.3 (patch: exportación Excel de cotizaciones) |
| 2026-04-29 | Bug fix: `project_detail.html` — confirmación de eliminar LDM usaba `ldm.items\|length` que en Jinja resuelve al método built-in `.items()` del dict lanzando `TypeError: object of type 'builtin_function_or_method' has no len()`. Corregido a `ldm['items']\|length` (notación de corchetes). El mismo patrón ya estaba corregido en el tab de Consistencia con `cn['items']` |
| 2026-04-29 | Versión bumped v16.3 → v16.4 (patch: fix TypeError al abrir pestaña de proyecto con LDMs) |
| 2026-04-30 | Cotizaciones (`templates/quote_project_form.html`): selección múltiple de partidas con checkbox por fila + "seleccionar todo" en el header de la tabla. Barra de acciones masivas que aparece al haber selección con dropdown de sección destino (poblado dinámicamente con secciones existentes + opción `(Sin sección)`) y botones **Mover**, **Copiar** y **Eliminar** |
| 2026-04-30 | Mover relocaliza las filas físicamente al final de la sección destino preservando orden relativo; `syncItemSections()` reasigna el `item_section[]` oculto al guardar. Copiar clona las filas con `cloneNode` + helper `copyInputValues` para transferir los `.value` actuales de los inputs (que `cloneNode` no copia). Eliminar pide confirmación |
| 2026-04-30 | "Seleccionar todo" respeta el filtro inline de partidas (sólo afecta filas visibles) y refleja estado indeterminado cuando hay selección parcial. Las filas seleccionadas se resaltan visualmente. Los checkboxes no llevan atributo `name`, así que no se envían al backend ni cambian el contrato del form |
| 2026-04-30 | Versión bumped v16.4 → v17.0 (feature: selección múltiple de partidas en cotización con mover/copiar/eliminar entre secciones) |
| 2026-05-02 | Bug fix: `INICIAR.bat` instalaba `flask fpdf2` de forma literal sin incluir `openpyxl`; corregido a `pip install -r requirements.txt` para garantizar que todas las dependencias del archivo se instalen al reiniciar |
| 2026-05-02 | `routes/quotes.py:quote_excel` — cambio de comportamiento: el Excel de cotización ya no se descarga en el navegador sino que se guarda en la carpeta Drive del proyecto (igual que los PDFs). Ruta valida que la carpeta Drive exista antes de intentar guardar y redirige a `#tab-quote` con flash de éxito o error. `_build_quote_excel_response` renombrada a `_build_quote_workbook` y refactorizada para devolver `(wb, filename)` en lugar de una respuesta `send_file` |
| 2026-05-02 | Versión bumped v17.0 → v17.1 (patch: fix instalación de openpyxl en INICIAR.bat + Excel de cotización guarda en Drive como los PDFs) |
| 2026-05-02 | Consistencia COT/LDM: auditoría visual ampliada con detección de margen bajo por artículo (`low_margin`), totales ligados/no ligados a catálogo, delta de cantidades, margen unitario porcentual y acciones sugeridas por problema. |
| 2026-05-02 | `templates/project_detail.html` — mejora del tab **Consistencia** con cobertura por catálogo, acciones sugeridas, filtro local de artículos/issues, columna Δ Qty, margen unitario con porcentaje y diagnóstico accionable por renglón. |
| 2026-05-02 | Tests: `tests/test_consistency.py` amplía cobertura para margen bajo, acciones sugeridas y totales ligados/no ligados a catálogo. |
| 2026-05-02 | Versión bumped v17.1 → v18.0 (feature: auditoría visual ampliada de consistencia COT/LDM) |
| 2026-05-02 | Bundles Fase 1: nuevos módulos `tracker/bundles.py` y `tracker/comparison_rules.py` para núcleo de bundles manuales versionados, expansión técnica de COT a materiales esperados y reglas de equivalencia COT↔LDM. |
| 2026-05-02 | Persistencia: `storage.py` agrega llaves `bundles` y `comparison_rules`; se crean `data/bundles.json` y `data/comparison_rules.json` como listas JSON vacías iniciales. |
| 2026-05-02 | Consistencia técnica: `compute_consistency()` agrega `bundle_consistency` con expected/actual/rows/summary, partidas COT con bundle, partidas sin mapeo y componentes inválidos, sin romper la consistencia comercial existente. |
| 2026-05-02 | Tests: nuevos `tests/test_bundles.py` y `tests/test_comparison_rules.py`; `tests/test_consistency.py` cubre expansión por bundles y reglas de conversión técnica. |
| 2026-05-02 | Versión bumped v18.0 → v19.0 (feature: núcleo de bundles versionados + reglas de comparación técnica COT/LDM) |
| 2026-05-02 | Bundles Fase 2: nueva UI Admin para crear bundles, editar artículo comercial asociado, duplicar versiones, activar versiones, eliminar versiones y editar componentes por versión. |
| 2026-05-02 | Reglas COT/LDM Fase 2: nueva UI Admin para crear, editar, activar/desactivar y eliminar reglas de comparación con factor, dirección, redondeo y tolerancia. |
| 2026-05-02 | Navegación: `base.html` agrega accesos laterales a **Bundles** y **Reglas COT/LDM**. |
| 2026-05-02 | Tests: nuevo `tests/test_admin_bundles_routes.py`; `tests/test_project_view.py` agrega `bundles` y `comparison_rules` al mock de `load()` para cubrir nuevas dependencias del contexto. |
| 2026-05-02 | Versión bumped v19.0 → v20.0 (feature: UI Admin para bundles versionados y reglas de comparación COT/LDM) |
| 2026-05-02 | Bundles Fase 3: `project_detail.html` muestra consistencia técnica por bundles con material esperado, unidad, cantidad esperada, cantidad equivalente en LDM, diferencia, estado y trazabilidad COT/LDM. |
| 2026-05-02 | Consistencia técnica UI: agrega filtro local, badges de faltantes/insuficientes/excedentes/extras/OK y alertas para componentes inválidos, partidas COT sin bundle y LDMs sin catálogo. |
| 2026-05-02 | El badge del tab **Consistencia** considera tanto consistencia comercial como técnica. |
| 2026-05-02 | Tests: nuevo `tests/test_project_detail_bundle_ui.py` para validar render de la sección técnica por bundles. |
| 2026-05-02 | Versión bumped v20.0 → v21.0 (feature: visualización de consistencia técnica por bundles en detalle de proyecto) |
| 2026-05-02 | Hotfix detalle de proyecto: hardening defensivo del tab Consistencia técnica para evitar errores de render cuando falten bundles, reglas, cantidades, trazabilidad o estructuras internas en proyectos con datos incompletos. |
| 2026-05-02 | Versión bumped v21.0 → v21.1 (patch: hardening del tab Consistencia técnica para datos incompletos) |
| 2026-05-02 | Hotfix detalle de proyecto: hardening adicional de filas comerciales en Consistencia; se reemplazan accesos frágiles a campos opcionales como `qty_delta`, `price_cot`, `cost_avg`, `margin_unit`, `issue_details` y `primary_action` por accesos seguros con defaults. |
| 2026-05-02 | Versión bumped v21.1 → v21.2 (patch: hardening adicional de filas comerciales sin `qty_delta` u otros campos opcionales) |
| 2026-05-02 | Bundles/Reglas COT-LDM: corrección de render en `/bundles` pasando `get_active_bundle_version` y `catalog_by_id` al template; listas de artículos/reglas ordenadas alfabéticamente. |
| 2026-05-02 | Versión bumped v21.2 → v21.3 (patch: hardening de pantalla Bundles y orden alfabético de selectores). |
| 2026-05-02 | Reglas COT/LDM: corrección de opciones visibles para Dirección (`LDM → COT`, `COT → LDM`) y Redondeo (`Sin redondeo`, `Hacia arriba`, `Hacia abajo`, `Redondeo normal`); validación defensiva en `admin.py`. |
| 2026-05-02 | Versión bumped v21.3 → v21.4 (patch: corrige formulario de reglas COT/LDM y normaliza dirección/redondeo al guardar). |
| 2026-05-02 | Nueva entidad `comparison_ignored_items`: permite configurar artículos de catálogo que se ignoran en el cruce COT/LDM sin sacarlos del costo total del proyecto. |
| 2026-05-02 | Consistencia comercial: los artículos ignorados se excluyen de issues como faltante/excedente/diferencia, pero sus importes permanecen dentro del subtotal/costo global de la LDM. |
| 2026-05-02 | Consistencia técnica por bundles: materiales configurados como ignorados se excluyen de la tabla esperado vs real y se reportan en un resumen independiente. |
| 2026-05-02 | UI Reglas COT/LDM: nueva sección “Artículos ignorados en comparación” con crear/editar/activar/desactivar/eliminar, alcance `Comercial + Técnica`, `Solo comercial` o `Solo técnica`. |
| 2026-05-02 | Tests: se agregó `tests/test_comparison_ignored.py` y cobertura en `tests/test_consistency.py` para validar que los artículos ignorados no generan diferencias, pero conservan costo. |
| 2026-05-02 | Versión bumped v21.4 → v22.0 (feature: artículos ignorados en comparación COT/LDM como costos no atribuibles directamente al cliente). |
| 2026-05-02 | `tracker/csv_import.py` — `parse_ldm_csv(path, catalog=None)`: parámetro opcional `catalog` construye índice `{nombre.lower() → id}` en O(1) y vincula automáticamente `catalog_item_id` a cada artículo importado cuya descripción coincida exactamente (case-insensitive) con un `nombre` del catálogo. Funciones auxiliares `_build_catalog_index` y `_match_catalog`. Items sin coincidencia conservan `catalog_item_id=''`. |
| 2026-05-02 | `tracker/routes/materials.py` — `import_ldm_csv` pasa `catalog=load(“catalogo”)` al parser; el auto-link es transparente para el resto del flujo. |
| 2026-05-02 | `templates/ldm_form.html` — nueva UIX en la vista previa de importación CSV: banner de resumen con conteo de artículos vinculados vs. sin vincular; badge verde “Vinculado al catálogo” y hint ámbar “Busca en catálogo” por fila. |
| 2026-05-02 | `tests/test_csv_import.py` — 3 tests nuevos cubren auto-link exitoso, match case-insensitive y ausencia de catálogo (backward-compat). |
| 2026-05-02 | Versión bumped v22.0 → v23.0 (feature: auto-vinculación catalog_item_id al importar CSV desde LISP). |
| 2026-05-03 | `pdfs.py:build_ldm_pdf` — corrección de acentos: footer “Pagina” → “Página”; encabezados de tabla “DESCRIPCION” → “DESCRIPCIÓN” (con y sin precios). Auditoría completa de templates, validators y rutas confirmó que el resto del sistema ya tenía acentos correctos. |
| 2026-05-03 | Versión bumped v23.0 → v23.1 (patch: corrección de acentos en PDF de LDM — mejora 4 del roadmap). |
| 2026-05-03 | Sistema completo de auditoría de catálogo eliminado: función `audit_deleted_catalog_items()` para analizar cotizaciones y LDMs con referencias obsoletas, página `/audit/deleted-catalog`, flujo de tres acciones (preservar/reconectar/purgar), badges visuales y funciones backend `preserve_/restore_/purge_deleted_catalog_item_in_record()`. |
| 2026-05-03 | Versión bumped v23.1 → v24.0 (feature: sistema completo de auditoría y gestión de catálogo eliminado). |
| 2026-05-03 | **Drive — integración mejorada**: `scan_drive_folder` diferencia errores por tipo (`unconfigured`/`root_missing`/`folder_missing`); detecta archivos base faltantes (`missing_base`); fix de bug de caché de proyecto cruzado; botón “Crear carpeta en Drive” desde UI cuando `error_type == folder_missing`; alertas de archivos base faltantes; validación de rutas en Ajustes con panel de estado ✓/✗. |
| 2026-05-03 | Versión bumped v24.0 → v24.1 (patch: Drive con tipos de error diferenciados, creación de carpeta y validación de rutas). |
| 2026-05-03 | `tracker/bundles.py` — `expand_quote_bundles()` agrega `comparison_rule_id` en cada entrada de `bundle_rows`, habilitando el cruce con reglas activas en la capa de consistencia. |
| 2026-05-03 | `tracker/consistency.py` — `compute_consistency()` ahora calcula `bundles_no_active_version` (subset de invalid_components por razón), `components_no_rule` (bundle_rows con regla referenciada inexistente) y `technical_suggested_actions` (acciones en orden de prioridad). Los cuatro campos nuevos se incluyen en `bundle_consistency`. |
| 2026-05-03 | `templates/project_detail.html` — sección técnica de consistencia rediseñada: KPI 4 cambia a “Bundles sin versión activa”; tres bloques de alerta diferenciados (versión faltante → rojo con link a Bundles, regla faltante → amarillo con link a Reglas, componentes inválidos → rojo genérico); panel de acciones sugeridas técnicas; toggle nav-pills “Por material” / “Por bundle”; tabla de materiales mejorada con columna “Acción sugerida”; vista anidada por bundle con sub-tabla de componentes (factor, cantidad esperada, equivalente LDM, Δ, badge, acción). Función JS `switchTechView` para alternar entre vistas. |
| 2026-05-03 | Tests: 26 tests pasan (test_bundles: 4, test_comparison_rules: 4, test_consistency: 18, test_project_detail_bundle_ui: 1). |
| 2026-05-03 | Versión bumped v24.1 → v25.0 (feature: auditoría visual de consistencia técnica COT/LDM por bundles con vistas material/bundle, alertas diferenciadas y acciones sugeridas). |
| 2026-05-03 | Confirmaciones destructivas estandarizadas: modal Bootstrap `#modalConfirmDelete` reutilizable en toda la app con título, detalle de impacto y botones Cancelar/Eliminar. Funciones globales `confirmDelete()` y `submitFormWithConfirm()` en `base.html`. Cotización: tipo, fecha, partidas, total. LDM: proveedor, artículos, costo. Entrega: versión, tipo, archivos + nota "ZIP no se borra". Ficha: tipo/marca/modelo + alerta de proyectos vinculados. Proveedor: categoría, contacto, email. Miembro de equipo: rol, email. Purge catálogo: lista de artículos afectados. Catálogo individual: nuevo endpoint `GET /api/catalogo/<id>/impact` que devuelve referencias activas en cotizaciones/LDMs ANTES de eliminar. Catálogo masivo: modal con conteo y advertencia de desconexión. |
| 2026-05-03 | Versión bumped v25.0 → v25.1 (patch: confirmaciones destructivas estandarizadas con modal de impacto). |

---

## Pendientes / En desarrollo

**Alta prioridad:**
- Probar bundles reales en proyectos existentes y ajustar reglas de equivalencia COT/LDM.
- Estandarizar confirmaciones destructivas (eliminar cotización, LDM, entrega, ficha, proveedor, miembro de equipo, artículo de catálogo con referencias).
- Evaluar si conviene sincronización parcial COT ↔ bundle ↔ LDM (diseño pendiente).

**Media prioridad (ver `ROADMAP_MEJORAS.md`):**
- Limpieza residual de lógica en templates → view-models o servicios.
- Mejorar filtros y búsqueda en cotizaciones, LDMs, documentos, proveedores y fichas.

**Baja prioridad:**
- Mejoras de UX general (navegación, mensajes flash, carga, móvil).
- Exportaciones y reportes: resumen ejecutivo por proyecto, reportes históricos.

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
