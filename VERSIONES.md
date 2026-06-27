# ProjectTracker — Estado y Versiones

## Versión actual: v45.6 — 27-Jun-2026

### v45.6 — Permisos ampliados para cotizadores
- **Bundles**: cotizadores pueden crear, editar, eliminar bundles y gestionar versiones; se removió `_require_admin_post` y `@admin_required` de todos los routes de mutación
- **Proyectos**: cotizadores pueden crear y editar proyectos; botón "Nuevo proyecto" visible en dashboard para todos los usuarios autenticados
- **Eliminar proyecto protegido**: `delete_project` ahora tiene `@admin_required` (antes estaba desprotegido); botón Eliminar oculto para no-admins en el detail
- **Sidebar Bundles**: link visible para cotizadores desde v45.5+

## Versión actual: v45.5 — 27-Jun-2026

### v45.5 — Limpieza pestaña Documentos y badge XREF
- **Pestaña Documentos eliminada**: `#tab-docs` (Historial de Entregas) removida del nav y del contenido en `project_detail.html`
- **Badge XREF eliminado**: badge `file_xref` y CSS `.fnb-xref` removidos del encabezado del proyecto

## Versión actual: v45.4 — 27-Jun-2026

### v45.4 — Gestión de usuarios completa
- **Eliminar usuario**: botón Eliminar con confirmación JS; ruta `POST /usuarios/<id>/delete`; protección contra auto-eliminación
- **Editar nombre de usuario**: ícono lápiz abre modal con nombre prellenado; ruta `POST /usuarios/<id>/edit-username`; valida duplicados antes de guardar
- `graphify` en PATH confirmado como shim no-op (`~/.local/bin/graphify`) — exits limpio cuando no hay binario real

## Versión actual: v45.3 — 27-Jun-2026

### v45.3 — PDF portada + editor de cotizaciones: pulido visual y sincronización
- **PDF portada — márgenes unificados**: integrantes, dirección, separador, título y "Propuesta para" usan `l_margin=5mm` y `content_width=200mm` — iguales al recuadro gris
- **PDF portada — integrantes sobre logo**: fondo reducido 112→85mm, logo ajustado a `x=60 y=10 w=90`, contactos renderizados debajo del fondo (y=88+) alineados a la derecha
- **PDF portada — header simplificado**: eliminado número de cotización del header de páginas internas; columnas fecha/proyecto dimensionadas con `get_string_width`
- **PDF T&C**: ":" después de cada subtítulo; `pre_ln=0` (sin espacio antes del bloque), `post_ln=4mm` después del encabezado
- **Editor — Notas generales y Especificaciones técnicas eliminadas**: secciones removidas del formulario de cotización
- **Editor — T&C e Integrantes colapsados por default**: `aria-expanded="false"` / `collapse` (sin `show`) en ambos paneles
- **Plantillas — "Renglón N" → "Integrante N"**: etiqueta de contactos en `quote_templates.html`
- **Sincronización integrantes**: el form carga desde `contacts_default` de la plantilla cuando no hay integrantes guardados por cotización; los guardados sobrescriben el default (mismo patrón que T&C)
- 341 tests pasan

## Versión actual: v45.2 — 27-Jun-2026

### v45.2 — `graphify` local en PATH como shim seguro
- `graphify` ya existe en `~/.local/bin` como enlace al wrapper del repo
- El wrapper no intenta invocarse a sí mismo y sale en limpio como no-op cuando no hay binario real instalado
- El comando ya no bloquea otros procesos del terminal
- 341 tests pasan

## Versión anterior: v45.1 — 27-Jun-2026

### v45.1 — Hook Graphify tolerante sin binario local
- `mise run graph-update` y `mise run graph-check` usan `tools/graphify_task.py`
- Si `graphify` no está instalado/en PATH, la tarea avisa y termina correctamente en vez de romper el cierre
- Si `graphify` existe y devuelve error, el wrapper conserva el código de salida fallido
- 341 tests pasan

## Versión anterior: v45.0 — 27-Jun-2026

### v45.0 — Contactos de portada en cotizaciones
- Plantillas de cotización agregan hasta 4 renglones de contacto para portada, cada uno con toggle, nombre y puesto
- Perfil de empresa agrega correo y teléfono; el PDF los muestra debajo de la dirección como `correo - teléfono`
- Portada de cotización renderiza los contactos activos después del logo y antes de la dirección
- PDF actualiza los textos `Detalle de Partidas`, `Nombre, Firma y Fecha` y `Representante Autorizado`
- 338 tests pasan

## Versión anterior: v44.2 — 27-Jun-2026

### v44.2 — Títulos de términos en Title Case
- Secciones de Términos y Condiciones usan títulos sin punto final y con mayúscula inicial por palabra: `Información Base y Ajustes`, `Condiciones de Pago`, `Trabajos Adicionales`, etc.
- Plantillas normalizan títulos por clave, ignorando títulos legacy guardados
- PDF renderiza títulos canónicos por `key` aunque la cotización tenga títulos anteriores en `specs.terms`
- 338 tests pasan

## Versión anterior: v44.1 — 27-Jun-2026

### v44.1 — Plantillas sin notas/specs legacy
- Plantillas de cotización eliminan los bloques `Notas predeterminadas` y `Especificaciones técnicas predeterminadas`
- `quote_templates_config.py` deja de exponer `notes_default` y `specs_default`; conserva compatibilidad ignorando esos campos si existen en datos viejos
- Cotizaciones nuevas ya no prellenan Notas ni Especificaciones técnicas desde plantillas; solo secciones y Términos y Condiciones
- PDF usa el título exacto `Términos y Condiciones`
- 338 tests pasan

## Versión anterior: v44.0 — 27-Jun-2026

### v44.0 — Plantillas de términos y PDF con secciones independientes
- Plantillas de cotización agregan `terms_default` para editar textos y toggles de Términos y condiciones por tipo de cotización
- Cotizaciones nuevas aplican los términos predeterminados de la plantilla seleccionada al cargar o cambiar tipo
- PDF separa `Especificaciones técnicas`, `Términos y condiciones` y `Notas`; specs ya no sustituyen ni ocultan los términos
- Los checkboxes de términos siguen controlando qué secciones aparecen en el PDF
- 338 tests pasan

## Versión anterior: v43.4 — 27-Jun-2026

### v43.4 — PDF header: eliminar número de cotización
- Header de páginas internas muestra solo nombre de proyecto (izquierda) y fecha (derecha)
- Simplifica el header y elimina cualquier posibilidad de desborde del número de cotización
- 337 tests pasan

## Versión anterior: v43.3 — 27-Jun-2026

### v43.3 — PDF header: columnas dinámicas para evitar desborde con fuente monoespaciada
- Header (páginas 2+): en vez de proporciones fijas (62/22/16%), se mide el ancho real de la fecha y el número de cotización con `get_string_width` y la columna del proyecto recibe el espacio restante
- Elimina la sobreposición visible "COT-CCAL-P01-202606277 de junio de 2026" causada por que la fuente monoespaciada ocupa más ancho que DejaVu Sans con los mismos porcentajes
- 337 tests pasan

## Versión anterior: v43.2 — 27-Jun-2026

### v43.2 — PDF portada: ajustes visuales recuadro gris
- Margen interior reducido: `left_x` 11mm → 7mm (padding lateral de 2mm desde el borde del recuadro)
- VERSIÓN se mueve de x=91 a x=76mm: `fecha_w` fijo en 55mm (cabe "30 de septiembre de 2026"); `version_w` crece a ~25mm como remanente
- Caja de totales más grande: 88mm → 96mm de ancho, 34mm → 38mm de alto; finaliza a 2mm del borde derecho del recuadro gris
- 337 tests pasan

### v43.1 — PDF: fuente Atkinson Hyperlegible Mono + portada a ancho completo
- Fuente cambiada a **Atkinson Hyperlegible Mono** (Regular + Bold) en todos los PDFs; fallback a DejaVu Sans si los archivos no están disponibles
- Recuadro gris de portada expandido a `content_width` (200mm) igualando el bloque de Alcance; panel izquierdo crece de 70 → 92mm, box de totales se desplaza a x=111
- Fecha en recuadro de portada: ancho dinámico (65mm) elimina desborde; escalado de fuente proporcional como respaldo para meses largos
- 337 tests pasan

### v43.0 — Editor de cotización: topbar completo + toggles + T&C editables
- **Topbar del editor**: todos los controles de `project_detail` replicados en el editor — Vista previa (PDF inline), Resumen, Descargar PDF, Descargar Excel, Aprobar/Toggle extraordinaria, CSV, Duplicar, Purgar catálogo eliminado (condicional), Eliminar con confirmación
- **Notas generales**: toggle ON/OFF (form-switch); campo oculto cuando está desactivado
- **Especificaciones técnicas**: toggle ON/OFF para el bloque completo
- **Disciplina / Descripción portada**: campo editable en datos generales; vacío = sin segunda línea en portada del PDF
- **Nombre de proyecto en 2 renglones**: info box de portada usa `get_string_width` para distribuir palabras en hasta 2 líneas en vez de truncar con "..."
- **Términos y condiciones editables por cotización**: 9 secciones (Vigencia, Precios, Información base, Condiciones de pago, Plazos, Trabajos adicionales, Exclusiones, Garantía, Aceptación) con toggle ON/OFF individual y textarea editable; se almacenan en `specs["terms"]`; cotizaciones sin terms almacenados usan el comportamiento anterior sin cambios
- **Fix 500 en editor**: `quote.items` en Jinja2 resuelve al método built-in `dict.items()` en vez de la clave; corregido a `quote['items']`
- 337 tests pasan

## Versión anterior: v42.1 — 27-Jun-2026

### v42.1 — Acciones de cotización expandidas en pantallas grandes
- Botones CSV, Duplicar, Purgar y Eliminar ahora aparecen inline en pantallas ≥lg (`d-none d-lg-inline*`)
- El dropdown `···` se mantiene para pantallas menores a lg (`d-lg-none`) — sin duplicar código de confirmación
- 337 tests pasan

### v42.0 — Página de cotizaciones cross-proyecto
- Nueva ruta `GET /cotizaciones` (`quotes_bp.all_quotes`): carga todas las cotizaciones de todos los proyectos, une metadata del proyecto, ordena por fecha descendente y computa badge de aprobación
- Nuevo template `quotes_summary.html`: tabla con columnas Proyecto, Número, Tipo, Fecha, Total, Estado; métricas rápidas (total registros, aprobadas, monto aprobado); filtro JS en tiempo real; botón "Ver proyecto" primario lleva directo al tab Cotización; empty state
- Enlace "Cotizaciones" en sidebar izquierdo bajo Principal (entre Proyectos y Recursos)
- La edición de cotizaciones es exclusiva de la vista interna de cada proyecto — la página global solo ofrece acceso de lectura/navegación
- 337 tests pasan

## Versión anterior: v41.0 — 27-Jun-2026

### v41.0 — Dashboard simplificado + prefijo en sidebar
- Dashboard: eliminados semáforo y KPI de consistencia COT vs LDM; ruta simplificada (sin hydrate ni compute_consistency)
- Cards de proyecto muestran nombre, código `{Prefijo}-{###}-{Clave}`, cliente y total cotizado
- Sidebar muestra `company.prefix` como nombre de la app (fallback a nombre de empresa)
- 337 tests pasan

## v40.0 — 26-Jun-2026

### v40.0 — Clave de proyecto con prefijo de empresa
- Eliminados `disciplina`, `fecha` y `version` del nivel de proyecto (viven en los archivos)
- Clave adopta formato `{Prefijo}-{###}-{Clave}` donde el número es consecutivo automático
- Nuevo campo `prefix` en perfil de empresa (Admin → Empresa); si está vacío usa el nombre de la empresa
- `project_view.py`: `file_ie`/`file_xref` generados con el prefijo dinámico
- `project_new.html`: formulario simplificado, vista previa muestra `PREFIJO-###-Clave`
- `project_detail.html`: header y modal Editar muestran prefijo dinámico; CSS sobrante eliminado (~64 líneas de clases sin uso)
- 337 tests pasan

### v39.0 — Refactoring cotizador (simplificación mayor)
- App replanteada como cotizador puro: se suprimen tracker de tareas y sistema de alcances
- `project_detail.html`: eliminados tab Alcances, tab Avance, 6 modales relacionados (Info Externa, Cambiar estado, Editar observación, Modificar alcances, Actualizar etapa, Presupuesto por etapa) y handlers JS asociados; tab Cotización es ahora el primero y activo por defecto; selector de estado manual (Activo/Entregado/Archivado) reemplaza barra de progreso de alcances; disciplina en modal Editar cambia de `<select>` a `<input>` libre
- `dashboard.html`: eliminada barra de progreso de alcances por proyecto; se muestra total cotizado individual por tarjeta; sección `completed` renombrada a `delivered` (alineado con ruta); sección Archivados usa texto correcto
- `templates/project_new.html`: disciplina como texto libre sin catálogo
- `base.html`: quitados links de nav Alcances, Disciplinas, Tipos de Proyecto, Kanban
- `routes/projects.py`: rutas kanban, toggle_obra, update_task_status, update_observation_checklist, update_observation, update_task_info, save_task_note, update_project_alcances eliminadas; agregada `update_project_status` (Activo/Entregado/Archivado)
- `services.py`: `create_project()` sin tareas; funciones de alcances y tareas mantenidas pero sin llamadas activas
- `validators.py`: `validate_project_form` simplificada (sin alcances)
- 337 tests pasan

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
| PDF | fpdf2 ≥ 2.7.9; pdfplumber ≥ 0.11.0 |
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
├── requirements.txt            # flask>=3.0.0, fpdf2>=2.7.9, openpyxl>=3.1.0, pdfplumber>=0.11.0
├── ROADMAP_MEJORAS.md          # Backlog de mejoras acordadas
├── VERSIONES.md                # ← Este archivo (fuente de verdad)
│
├── tracker/
│   ├── __init__.py             # create_app(): registra blueprints, filtros Jinja, aliases legacy
│   ├── domain.py               # Catálogo de alcances, STAGES, statuses, fdate/currency filters, get_progress, project_stage
│   ├── storage.py              # load/save JSON, new_id (UUID 8 chars), today(), BASE_DIR, DATA_DIR
│   ├── services.py             # Lógica de negocio pura: crear proyectos+tareas, sincronizar alcances, cambiar status
│   ├── project_view.py         # View-model de project_detail: alcances, Drive, cotizaciones, LDMs y consistencia
│   ├── admin_filters.py        # Filtros puros para proveedores y fichas técnicas
│   ├── catalog.py              # hydrate_quote/ldm, catalog_maps, parse_*_items, quote_type_key/code, migrate_catalog_fields
│   ├── catalog_search.py       # tokenize, match_item, filter_catalog, list_categories (búsqueda por tokens AND + categoría)
│   ├── consistency.py          # Resumen visual COT vs LDM: cotización activa, costos, margen y cobertura básica
│   ├── csv_import.py           # Parser CSV para importar exportaciones LISP como LDM
│   ├── csv_catalog_validation.py # Validación estricta de CSV LDM/COT contra catálogo
│   ├── pdf_ldm_import.py       # Extractor PDF de proveedor para crear LDM con mapeo a catálogo
│   ├── ldm_sync.py             # Sincronización parcial de LDM desde bundles directos
│   ├── validators.py           # validate_project_form, validate_quote_form, validate_ldm_form
│   ├── pdfs.py                 # build_quote_pdf, build_ldm_pdf (fpdf2); logo desde Drive o .codex_tmp
│   ├── drive.py                # load/save_config, folder_name, scan_drive_folder, find_delivery_files
│   │                           # Migraciones al arranque: migrate_task_statuses/names/folder_numbers/in_obra
│   └── routes/
│       ├── __init__.py         # (vacío)
│       ├── projects.py         # Blueprint projects_bp — proyectos, tareas, entregas, ajustes, shutdown
│       ├── quotes.py           # Blueprint quotes_bp — cotizaciones CRUD + PDF + Excel
│       ├── quotes_mobile.py    # Blueprint quotes_mobile_bp — cotizador mobile-first /cotizar/mobile/*
│       ├── materials.py        # Blueprint materials_bp — LDMs CRUD + PDF/CSV/PDF proveedor + sync bundles + API costo
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
├── templates/                  # Jinja2
│   ├── base.html               # Layout principal con nav, flash messages, Bootstrap
│   ├── dashboard.html          # Lista proyectos activos/completados/cerrados
│   ├── project_new.html        # Formulario alta proyecto
│   ├── project_detail.html     # Vista detalle con tabs: tareas, docs, cotizaciones, LDMs, fichas
│   ├── quote_project_form.html # Alta/edición cotización (tabs P/G/E)
│   ├── quote_project_detail.html # Vista detalle cotización
│   ├── ldm_form.html           # Alta/edición LDM
│   ├── ldm_pdf_import.html     # Preview/mapeo de PDF proveedor a LDM
│   ├── catalogo.html           # CRUD catálogo maestro
│   ├── proveedores.html        # CRUD proveedores
│   ├── fichas.html             # CRUD fichas técnicas globales
│   ├── team.html               # CRUD equipo
│   ├── settings.html           # Rutas de Drive
│   ├── audit_deleted_catalog.html # Auditoría de referencias a catálogo eliminado
│   ├── bundles.html            # Admin de bundles directos COT → LDM
│   ├── mobile_base.html        # Layout mobile-first (sin sidebar, botones ≥48px)
│   ├── mobile_projects.html    # Paso 1: selección de proyecto
│   ├── mobile_items.html       # Paso 2: catálogo con pills de disciplina + auto-save
│   ├── mobile_review.html      # Paso 3: revisión del borrador + generar PDF
│   └── kanban.html             # Portafolio Kanban: 4 columnas (Cotización→Diseño→Entregado→Obra)
│
└── tests/
    ├── test_services.py        # unittest: crear proyecto, sync alcances, bloqueos, subtareas obs
    ├── test_services_mobile.py # unittest: helpers mobile (filter_disciplina, upsert/remove draft, finalize)
    ├── test_drive.py           # unittest: escaneo Drive, CSVs de plano y archivos ignorados
    ├── test_csv_catalog_validation.py # unittest: validador estricto CSV vs catálogo
    ├── test_csv_import.py      # unittest: parser CSV para LDM
    ├── test_ldm_csv_import_route.py   # unittest: bloqueo de importación LDM por catálogo
    ├── test_quote_csv_import.py       # unittest: parser CSV para COT desde LISP
    ├── test_quote_csv_import_route.py # unittest: importación COT desde upload/Drive
    ├── test_quote_sections.py         # unittest: secciones contiguas y ordenables en cotizaciones
    ├── test_validators.py      # unittest: formularios vacíos, filas vacías, números inválidos
    ├── test_catalog_search.py         # unittest: tokens AND, categoría, list_categories, smoke /api/catalogo
    ├── test_consistency.py            # unittest: resumen visual simple COT vs LDM, margen y avisos básicos
    ├── test_bundles.py                # unittest: normalización, versiones, expansión de bundles
    ├── test_admin_bundles_routes.py   # unittest: rutas Admin bundles directos
    ├── test_admin_filters.py          # unittest: filtros administrativos y smoke de rutas proveedores/fichas
    ├── test_admin_forms.py            # unittest: validación inline y preservación de formularios administrativos
    ├── test_audit_deleted_catalog_route.py # unittest: auditoría de referencias a catálogo eliminado
    ├── test_project_view.py           # unittest: contexto de project_detail, filas LDM y CSVs importables
    ├── test_deletions.py              # unittest: cascadas al eliminar proyecto y limpieza de referencias catálogo
    ├── test_form_models.py            # unittest: view-models de cotización y LDM desde formularios inválidos
    ├── test_project_detail_bundle_ui.py  # unittest: render del resumen COT vs LDM simplificado
    ├── test_materials_csv_export.py      # unittest: exportación CSV de LDM existente
    ├── test_ldm_sync.py                  # unittest: sincronización parcial LDM desde bundles
    ├── test_ldm_pdf_import_routes.py     # unittest: importación PDF proveedor, token temporal y proyectos cerrados
    ├── test_tube_fixtures.py             # unittest: fixtures CSV LDM y COT para tubería (13+2 LDM, 11+3 COT)
    ├── test_quotes_mobile.py             # unittest: rutas mobile /cotizar/mobile/* (18 integration tests)
    ├── test_kanban.py                    # unittest: project_stage (10 unit) + rutas kanban (4 integration)
    ├── test_semaphore.py                 # unittest: project_semaphore (11 unit tests)
    ├── test_company_templates.py         # unittest: company_config + templates_config (9 unit tests)
    └── test_avance_routes.py             # unittest: rutas tab Avance (15 integration tests)
```

---

## Entidades de datos

### Proyecto (`projects.json`)
```
id, name, clave, client, status (Activo|Entregado|Archivado), notes,
folder_num (NNN auto-incremental), deadline, drive_url, updated_at,
closed_at, created_at
```
Código visible: `{company.prefix}-{folder_num}-{clave}` (ej. `DIDE-004-OM001`)

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
| Cotizaciones | Importación COT desde CSV manual o Drive con validación estricta previa contra catálogo: cada `description` debe resolver a `catalogo.nombre` normalizado y `unit` debe coincidir con `catalogo.unidad`; partidas inválidas bloquean el preview/importación. | `routes/quotes.py` + `quote_csv_import.py` + `csv_catalog_validation.py` |
| Cotizaciones | Secciones opcionales con encabezado y subtotal por sección en formulario, vista y PDF | `validators.py` + `catalog.py` + `pdfs.py` |
| Cotizaciones | Nota base de proyecto en portada del PDF según tipo: preliminar sin nota, general con último DWG, extraordinaria con nota manual | `routes/quotes.py` + `drive.py:latest_dwg_stem` + `pdfs.py` |
| LDMs | CRUD, PDF, CSV, set costo manual | `routes/materials.py` |
| LDMs | Importación CSV de plano → nueva LDM con revisión previa, vínculo `csv_origen` y bloqueo de reimportación del mismo CSV. Antes del preview valida estrictamente catálogo: cada `description` debe resolver por nombre normalizado y `unit` debe coincidir con `catalogo.unidad`; partidas inválidas bloquean la importación. | `routes/materials.py:import_ldm_csv` + `csv_import.py` + `csv_catalog_validation.py` |
| LDMs | Importación PDF de proveedor → preview/mapeo a catálogo y creación de LDM. Procables detecta proveedor, fecha y número de cotización cuando están disponibles. | `routes/materials.py:import_ldm_pdf_*` + `pdf_ldm_import.py` + `ldm_pdf_import.html` |
| LDMs | API JSON para actualizar costo (`/api/ldm/<id>/costo`) | `routes/materials.py:api_ldm_set_costo` |
| COT/LDM | Sincronización parcial desde bundles directos: agrega a una LDM existente sólo materiales faltantes o cantidades insuficientes calculadas desde la COT activa por `catalog_item_id`; no sobrescribe renglones existentes ni precios capturados | `ldm_sync.py` + `routes/materials.py:sync_ldm_bundles` |
| Catálogo | CRUD + búsqueda por tokens AND (sin acentos) + filtro por categoría + API JSON (`/api/catalogo`, `/api/catalogo/categorias`) | `routes/admin.py` + `catalog_search.py` |
| Catálogo | Bulk delete vía API (`/api/catalogo/bulk-delete`) | `routes/admin.py` |
| Catálogo | Bulk edit vía API (`/api/catalogo/bulk-edit`): precio, categoria y disciplina en lote con barra de selección sticky | `routes/admin.py` + `catalogo.html` |
| Alcances | Editor CRUD admin en `/alcances`: tabla + modal para crear, editar y eliminar alcances; persiste en `data/alcances.json`; fallback a `DEFAULT_ALCANCES` | `routes/admin.py` + `alcances_admin.html` + `domain.py` |
| Proyectos | Campo `disciplina` (IE/ARQ/EST/AA/HID/VOZ…) configurable por proyecto; controla prefijo de carpeta y nombre de archivo; lista editable en `/disciplinas` | `routes/admin.py` + `disciplinas_admin.html` + `domain.py` |
| Catálogo | Alta rápida desde formulario de COT/LDM (acepta categoría) | `routes/admin.py:api_catalogo_add` |
| Catálogo | Migración suave que agrega campo `categoria=''` a artículos existentes al arranque | `catalog.py:migrate_catalog_fields` |
| COT/LDM | Filtro inline de partidas capturadas: caja con tokens AND, busca en descripción/unidad/sección, oculta filas no machean sin afectar el submit | `quote_project_form.html` + `ldm_form.html` |
| Consistencia | Resumen visual simple COT vs LDM por proyecto: cotización base activa, extras activas, costo total LDM, margen absoluto/porcentaje y cobertura básica de datos | `consistency.py` |
| Consistencia | KPI en dashboard con margen % y badge de estado visual | `dashboard.html` |
| Consistencia | Sección en detalle de proyecto con totales y avisos informativos; sin tabla técnica por bundles ni diagnósticos por artículo | `project_detail.html` |
| Proveedores | CRUD + búsqueda libre sin acentos + filtro por categoría | `routes/admin.py` + `admin_filters.py` |
| Fichas | CRUD global + vinculación a proyectos + filtros por texto/tipo/vinculación | `routes/admin.py` + `admin_filters.py` |
| Equipo | CRUD miembros | `routes/admin.py` |
| Ajustes | Rutas Drive (projects y fichas) | `routes/projects.py:settings` |
| Documentos | CSVs de plano en pestaña Documentos — columna LDM lista archivos `{clave}-v{N}-i{N}-{fecha}.csv` con nombre, fecha, tamaño y botón Descargar; aviso vacío cuando no hay archivos | `routes/projects.py` + `project_detail.html` |
| Observaciones | Guardar texto de observación existente vía ruta dedicada | `routes/projects.py:update_observation` |
| Observaciones | Toggle de ítem de checklist de observación vía ruta dedicada | `routes/projects.py:toggle_checklist_item` |
| App | Shutdown graceful vía POST `/shutdown` | `routes/projects.py:shutdown` |
| Portafolio | Kanban `/kanban`: 4 columnas derivadas (Cotización/Diseño/Entregado/Obra) con semáforo, barra de progreso y toggle "Iniciar Obra" / "Regresar" para admin. Etapa calculada por `project_stage()` en `domain.py`; sólo `in_obra=True` se persiste. | `routes/projects.py` + `domain.py` + `kanban.html` |
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
| GET | `/kanban` | `kanban` | Portafolio Kanban — 4 columnas de etapa derivada |
| POST | `/projects/<id>/toggle_obra` | `toggle_obra` | Flip `in_obra` boolean (admin only) |

### Blueprint `quotes_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/quote/new` | `new_quote` | Nueva cotización |
| POST | `/projects/<id>/quote/import` | `import_quote_csv` | Importar COT desde CSV subido manualmente, con bloqueo estricto si catálogo/unidad no coinciden |
| GET | `/projects/<id>/quote/import-drive/<path:filename>` | `import_quote_csv_drive` | Importar COT desde CSV detectado en Drive, con bloqueo estricto si catálogo/unidad no coinciden |
| GET/POST | `/projects/<id>/quote/<qid>/edit` | `edit_quote` | Editar cotización |
| GET | `/projects/<id>/quote/<qid>/view` | `view_quote` | Vista de sólo lectura |
| POST | `/projects/<id>/quote/<qid>/delete` | `delete_quote` | Eliminar cotización |
| POST | `/projects/<id>/quote/<qid>/approve` | `approve_quote` | Aprobar cotización base o activar/desactivar extra |
| GET | `/projects/<id>/quote/<qid>/pdf` | `quote_pdf` | Generar PDF en Drive |
| GET | `/projects/<id>/quote/<qid>/excel` | `quote_excel` | Descargar Excel (.xlsx) |
| GET | `/cotizaciones` | `all_quotes` | Resumen global de cotizaciones cross-proyecto |
| GET | `/audit/deleted-catalog` | `audit_deleted_catalog` | Auditoría de referencias a catálogo eliminado |

### Blueprint `quotes_mobile_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET | `/cotizar/mobile/` | `mobile_projects` | Paso 1: lista proyectos activos con indicador de borrador |
| GET | `/cotizar/mobile/<id>/items` | `mobile_items` | Paso 2: catálogo con pills de disciplina; `?nueva=1` descarta borrador |
| POST | `/cotizar/mobile/<id>/items` | `mobile_add_item` | Agrega/actualiza ítem en borrador (auto-save a quotes.json) |
| POST | `/cotizar/mobile/<id>/remove_item` | `mobile_remove_item` | Elimina ítem del borrador por `catalog_item_id` |
| GET | `/cotizar/mobile/<id>/review` | `mobile_review` | Paso 3: revisión de ítems, totales y subtotal |
| POST | `/cotizar/mobile/<id>/generate_pdf` | `mobile_generate_pdf` | Paso 4: finaliza borrador → asigna `quote_number`, descarga PDF |

### Blueprint `materials_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/projects/<id>/ldm/new` | `new_ldm` | Nueva lista de materiales |
| GET/POST | `/projects/<id>/ldm/import/<filename>` | `import_ldm_csv` | Importar CSV de plano como nueva LDM, con bloqueo estricto si catálogo/unidad no coinciden |
| POST | `/projects/<id>/ldm/import-pdf` | `import_ldm_pdf_upload` | Subir PDF de proveedor para crear LDM |
| GET | `/projects/<id>/ldm/import-pdf/map` | `import_ldm_pdf_map` | Revisar y mapear artículos extraídos del PDF |
| POST | `/projects/<id>/ldm/import-pdf/create` | `import_ldm_pdf_create` | Crear LDM desde el mapeo del PDF |
| GET/POST | `/projects/<id>/ldm/<lid>/edit` | `edit_ldm` | Editar LDM |
| POST | `/projects/<id>/ldm/<lid>/delete` | `delete_ldm` | Eliminar LDM |
| POST | `/projects/<id>/ldm/<lid>/set_cot` | `set_ldm_cot` | Guardar # cotización proveedor |
| GET | `/projects/<id>/ldm/<lid>/pdf` | `ldm_pdf` | Generar PDF LDM en Drive |
| GET | `/projects/<id>/ldm/<lid>/csv` | `ldm_csv` | Descargar CSV de una LDM existente |
| POST | `/projects/<id>/ldm/<lid>/sync-bundles` | `sync_ldm_bundles` | Sincronizar faltantes técnicos desde bundles directos |
| POST | `/api/ldm/<lid>/costo` | `api_ldm_set_costo` | API JSON: actualizar costo LDM |

### Blueprint `admin_bp`

| Método | Path | Función | Descripción |
|---|---|---|---|
| GET/POST | `/catalogo` | `catalogo` | CRUD catálogo maestro |
| POST | `/catalogo/<id>/edit` | `edit_catalogo` | Editar artículo (soporta AJAX) |
| POST | `/catalogo/<id>/delete` | `delete_catalogo` | Eliminar artículo (soporta AJAX) |
| POST | `/api/catalogo/bulk-delete` | `bulk_delete_catalogo` | Eliminar varios artículos |
| POST | `/api/catalogo/bulk-edit` | `bulk_edit_catalogo` | Edición masiva de precio/categoria/disciplina |
| GET | `/api/catalogo` | `api_catalogo` | Buscar artículos (JSON, max 50, tokens AND + filtro `categoria`) |
| GET | `/api/catalogo/categorias` | `api_catalogo_categorias` | Lista única de categorías existentes (JSON) |
| POST | `/api/catalogo/add` | `api_catalogo_add` | Agregar artículo vía JSON (acepta `categoria`) |
| GET | `/api/catalogo/<id>/impact` | `api_catalogo_impact` | Referencias activas antes de eliminar catálogo |
| GET/POST | `/bundles` | `bundles` | CRUD principal de bundles directos |
| POST | `/bundles/<id>/update` | `update_bundle` | Editar bundle |
| POST | `/bundles/<id>/delete` | `delete_bundle` | Eliminar bundle |
| POST | `/bundles/<id>/versions/add` | `add_bundle_version_route` | Crear versión de bundle |
| POST | `/bundles/<id>/versions/<n>/update` | `update_bundle_version` | Editar versión de bundle |
| POST | `/bundles/<id>/versions/<n>/activate` | `activate_bundle_version_route` | Activar versión de bundle |
| POST | `/bundles/<id>/versions/<n>/delete` | `delete_bundle_version_route` | Eliminar versión de bundle |
| GET/POST | `/proveedores` | `proveedores` | CRUD proveedores |
| POST | `/proveedores/<id>/edit` | `edit_proveedor` | Editar proveedor |
| POST | `/proveedores/<id>/delete` | `delete_proveedor` | Eliminar proveedor |
| GET/POST | `/fichas` | `fichas` | CRUD fichas técnicas |
| POST | `/fichas/<id>/link/<pid>` | `link_ficha` | Vincular ficha a proyecto |
| POST | `/fichas/<id>/unlink/<pid>` | `unlink_ficha` | Desvincular ficha |
| POST | `/fichas/<id>/delete` | `delete_ficha` | Eliminar ficha |
| GET/POST | `/team` | `team` | CRUD equipo |
| POST | `/team/<id>/delete` | `delete_member` | Eliminar miembro |
| GET | `/alcances` | `alcances_admin` | Editor CRUD de alcances de proyecto |
| POST | `/api/alcances/save` | `alcances_api_save` | Guardar lista de alcances (JSON) |
| GET | `/disciplinas` | `disciplinas_admin` | Editor CRUD de disciplinas (prefijos) |
| POST | `/api/disciplinas/save` | `disciplinas_api_save` | Guardar lista de disciplinas (JSON) |

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
| `ldm_pdf_import.html` | `GET /projects/<id>/ldm/import-pdf/map` |
| `catalogo.html` | `GET/POST /catalogo` |
| `proveedores.html` | `GET/POST /proveedores` |
| `fichas.html` | `GET/POST /fichas` |
| `team.html` | `GET/POST /team` |
| `settings.html` | `GET/POST /settings` |
| `audit_deleted_catalog.html` | `GET /audit/deleted-catalog` |
| `bundles.html` | `GET/POST /bundles` y rutas de versiones de bundles |
| `kanban.html` | `GET /kanban` |
| `alcances_admin.html` | `GET /alcances` |
| `disciplinas_admin.html` | `GET /disciplinas` |
| `quotes_summary.html` | `GET /cotizaciones` |

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
{Prefijo}-{folder_num}-{clave}
Ej: DIDE-004-OM001  |  CCAL-007-TorreReforma
```
`Prefijo` = campo `prefix` de la empresa (Admin → Empresa). Fallback al nombre de la empresa.

**Archivos de proyecto:**
- Plano principal DWG: `{DISC}-{CLAVE}-{VERSION}-{FECHA}.dwg`
- Plano principal PDF: `{DISC}-{CLAVE}-{VERSION}-{FECHA}.pdf`
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
| 2026-06-27 | **v44.2 — Títulos de términos en Title Case**: secciones de Términos y Condiciones sin punto final y con mayúscula inicial por palabra; plantillas/PDF normalizan títulos por clave para ignorar títulos legacy guardados. |
| 2026-06-27 | **v44.1 — Plantillas sin notas/specs legacy**: eliminados los bloques `Notas predeterminadas` y `Especificaciones técnicas predeterminadas` de plantillas; las cotizaciones nuevas ya no prellenan notas/specs desde plantillas; el PDF usa el título `Términos y Condiciones`. |
| 2026-06-27 | **v44.0 — Plantillas de términos y PDF con secciones independientes**: `terms_default` en plantillas de cotización; UI para editar textos/toggles de Términos y condiciones por tipo; cotizaciones nuevas aplican esos defaults; el PDF renderiza Especificaciones técnicas, Términos y condiciones y Notas como secciones independientes, respetando checkboxes. |
| 2026-06-27 | **v42.1 — Acciones de cotización expandidas**: botones CSV/Duplicar/Purgar/Eliminar visibles inline en pantallas ≥lg; dropdown `···` solo en pantallas menores. |
| 2026-06-27 | **v42.0 — Página de cotizaciones cross-proyecto**: nueva ruta `GET /cotizaciones` con tabla de todas las cotizaciones agrupadas por proyecto; métricas rápidas (total, aprobadas, monto); filtro JS en tiempo real; botón "Ver proyecto →" como acción principal (edición solo desde la vista interna de cada proyecto). Enlace en sidebar izquierdo bajo Principal. `quotes_summary.html` nuevo. |
| 2026-06-27 | **v41.0 — Dashboard simplificado + prefijo en sidebar**: eliminados semáforo y KPI COT vs LDM; cards muestran código `{Prefijo}-{###}-{Clave}` y total cotizado; sidebar usa `company.prefix` como nombre de app. |
| 2026-06-26 | **v40.0 — Clave de proyecto con prefijo de empresa**: formato `{Prefijo}-{###}-{Clave}`; nuevo campo `prefix` en perfil de empresa; eliminados `disciplina`, `fecha`, `version` del nivel de proyecto. |
| 2026-06-26 | **v39.0 — Refactoring cotizador**: app replanteada como cotizador puro; suprimidos tracker de tareas y alcances; tab Cotización como primario. |
| 2026-06-26 | **v38.0 — Disciplina de proyecto configurable**: nuevo campo `disciplina` en proyectos que controla el prefijo de carpeta y nombre de archivo (`IE`, `ARQ`, `EST`, `AA`, `HID`, `VOZ`, …). Lista de disciplinas editable en admin (Sistema → Disciplinas). Badge de carpeta, preview de nombre de archivo y modal de edición actualizan dinámicamente al cambiar la disciplina. Proyectos existentes usan `IE` como fallback sin migración. `domain.py` expone `get_disciplinas()` con fallback a `DEFAULT_DISCIPLINAS`. Rutas: `GET /disciplinas`, `POST /api/disciplinas/save`. Nuevo template: `disciplinas_admin.html`. Convención de nomenclatura actualizada de `IE-{N}-{clave}` a `{DISC}-{N}-{clave}`. |
| 2026-06-26 | **v37.1 — Simplificación editor de alcances**: se retira el campo "Info Ext" (aparece en hoja de Info EXT del PDF) del modal y tabla del editor de alcances. El campo se conserva en el modelo de datos para compatibilidad con la generación de PDFs (`get_info_ext_excluded()`), pero deja de ser editable. |
| 2026-06-26 | **v37.0 — Alcances personalizables con editor CRUD**: los alcances del proyecto dejan de ser hardcoded. Nueva página admin (Sistema → Alcances) con tabla y modal para agregar, editar y eliminar alcances con soporte de fuente (propia/externa), etiqueta de dependencia y campo de bloqueo. Persiste en `data/alcances.json`; si el archivo no existe usa `DEFAULT_ALCANCES` como fallback. `domain.py` expone `get_alcances()`, `get_alcances_by_id()`, `get_info_ext_excluded()` — funciones dinámicas que leen del archivo en cada llamada. `check_blocked()` actualizado para usar datos vivos. Módulo-nivel `ALCANCES`, `ALCANCES_BY_ID`, `INFO_EXT_EXCLUDED` conservados como alias de compatibilidad. Rutas: `GET /alcances`, `POST /api/alcances/save`. Nuevo template: `alcances_admin.html`. Enlace en sidebar (Sistema). |
| 2026-06-25 | **v36.1 — Sticky headers + fixes de UI y bugs críticos**: (1) Header del catálogo (barra de bulk-edit + encabezados de columna) ahora permanece visible al hacer scroll — implementado con `position:sticky`, `ResizeObserver` para offset dinámico y colores de fondo hardcoded `#141c30`/`#1a2540` para el tema oscuro. (2) Mismo comportamiento sticky para headers de cotizaciones y LDM en detalle de proyecto. (3) Preview de nombre de archivo en formulario de nuevo proyecto corregido a colores del tema oscuro (antes fondo azul claro hardcoded). (4) CSRF token en bulk-edit del catálogo corregido (`window._csrf` indefinido → `document.querySelector('meta[name="csrf-token"]').content`). (5) Subida de logo de empresa ya no sobrescribe datos de compañía — se corrigió el uso de `get_company()` (mezcla defaults) por `load("company")` (JSON crudo). (6) `data/*.json` excluidos de git y volumen persistente configurado en Railway para que los datos sobrevivan redespliegues. |
| 2026-06-22 | **v36.0 — Editor PDF Asistido para Cotizaciones (Fase 12)**: nueva ruta `GET/POST /projects/<id>/quote/<qid>/pdf-editor` con layout de dos paneles (sidebar + preview). Sidebar con acordeón de 4 secciones editables: **Portada** (nota base del proyecto para tipos General/Extraordinaria), **Alcance** (texto libre que sobreescribe los dos párrafos estándar, almacenado en `specs.alcance_custom`), **Condiciones** (5 campos personalizados — validez, condiciones\_de\_pago, exclusiones, forma\_de\_entrega, contacto — que reemplazan los Términos y Condiciones estándar cuando alguno tiene valor, almacenados en `specs`), **Notas** (`quote.notes`). Panel derecho: preview HTML del PDF con las 3 páginas del documento (portada, tabla de partidas, condiciones/notas) con paleta navy/ink/muted del PDF real. Actualización en tiempo real vía JS con debounce 250ms: portada, alcance, condiciones y notas se reflejan en el preview sin recargar la página. Botón "Guardar cambios" (POST al mismo endpoint). Acceso desde la vista de detalle de cotización con botón **Editor PDF**. 5 tests nuevos en `test_quote_pdf_editor.py`. Suite total: 356 tests. |
| 2026-06-21 | **v35.1 — Corrección de bugs en sincronización de bundles (code review)**: 6 bugs corregidos tras revisión exhaustiva del diff v34.1/v35.0. (1) `ldm_sync.py`: clasificación `sync_issue` ahora usa presencia en `actual_items` en lugar de `actual_qty <= 0`, evitando que filas con qty negativo (devoluciones) sean etiquetadas como `missing_in_ldm`. (2) `materials.py`: guard de dedup bloquea agregar un `catalog_item_id` que ya tiene fila `origen=bundle_sync` en la LDM, previniendo duplicados por doble-submit o sesiones concurrentes. (3) `materials.py`: mensaje flash diferenciado cuando las selecciones del usuario ya no aparecen en las sugerencias recalculadas en POST (cotización o bundles cambiaron entre GET y POST). (4) `materials.py`: `subtotal_cot` se recalcula después de agregar filas sincronizadas, igual que en `purge_ldm_deleted_catalog_items`. (5) `validators.py` + `ldm_form.html`: `sync_total_expected_qty` y `sync_actual_qty` (campos nuevos de v35.0) ahora se round-tripean en los hidden inputs del formulario de edición; antes se perdían en el primer guardado. (6) `ldm_form.html`: `existing_ldm` excluye también `bundle_suggestion`, evitando que una LDM sugerida active el formulario de edición en paralelo. `.gitignore` agrega `.claude/settings.local.json`. |
| 2026-06-21 | **v35.0 — Sincronización asistida para LDM existente**: `/projects/<id>/ldm/<lid>/sync-bundles` ahora abre un preview por GET con diff de faltantes calculados desde COT activa + bundles antes de escribir. El usuario puede seleccionar subset de materiales (`selected_catalog_item_id[]`) y el POST agrega sólo las filas marcadas, sin modificar renglones ni precios existentes. El diff muestra esperado total, cantidad ya existente y cantidad a agregar; `tracker/ldm_sync.py` conserva metadatos `sync_expected_*` y agrega `sync_total_expected_qty`/`sync_actual_qty`. La pestaña Materiales muestra acción **Revisar** por LDM. Tests nuevos cubren preview, selección parcial, no-op sin selección y UI del botón. |
| 2026-06-21 | **v34.1 — Cobertura de tests de bundles y normalización de datos**: 11 tests nuevos en `test_bundles.py` en dos clases. `SeededBundlesTest` (4 tests): expansión del bundle de metro lineal tubería conduit galv. 16mm (`917E276F`, 9 componentes) y de salida eléctrica para luminaria (`B59B71BE`, 11 componentes), integridad de versión activa en todos los bundles seeded, sin `catalog_item_id` duplicados en el índice. `BundleEdgeCasesTest` (7 tests): componente `qty=0` → `invalid_components`, `catalog_item_id` vacío → `invalid_components`, bundle sin versiones → `bundle_without_active_version`, `activate_bundle_version` con versión inexistente → `ValueError`, `delete_bundle_version` con versión inexistente → `ValueError`, `waste_pct` aplicado correctamente, marcadores de sección omitidos del conteo. Normalización `int` → `float` en `BND-CIRC-CONT-20M` (`data/bundles.json`). Suite total: 296 tests. |
| 2026-06-19 | **v34.0 — Tests de cobertura: semáforo, company/templates, rutas Avance**: 35 tests nuevos cubren `project_semaphore` (11 unitarios: gris/verde/amarillo/rojo, deadline vs inactividad, fecha inválida), `company_config.py` (4 unitarios: defaults, merge, non-dict, save), `templates_config.py` (5 unitarios: defaults, empty list, stored, invariantes, save), y rutas del tab Avance (15 integración: `update_stage_status` 4, `toggle/add/delete_doc_checklist` 5, `update_stage_budget` 4, `project_progress_pdf` 2). Suite total: 282 tests. Archivos nuevos: `test_semaphore.py`, `test_company_templates.py`, `test_avance_routes.py`. |
| 2026-06-19 | **v33.0 — Portafolio Kanban (Fase 11)**: nueva vista `/kanban` con 4 columnas (Cotización, Diseño, Entregado, Obra). Etapa derivada automáticamente por `project_stage()` en `domain.py` — solo `in_obra: bool` se persiste en `projects.json`; las 3 etapas previas se calculan desde alcances y statuses existentes. Migración `migrate_in_obra()` en `drive.py` agrega el campo a proyectos existentes al arrancar. Admin puede mover proyectos a/de Obra con "Iniciar Obra" / "Regresar" (POST `/projects/<id>/toggle_obra`). Cards muestran semáforo, clave, cliente y barra de progreso. Nav principal incluye enlace "Portafolio" con ícono kanban. 14 tests nuevos (`test_kanban.py`: 10 unitarios de `project_stage` + 4 de integración de rutas). 247 tests en total. |
| 2026-06-17 | **v31.5 — Etapa de avance, presupuesto y PDF de reporte**: nuevo tab "Avance" en detalle de proyecto con estado por etapa de template (pending/in_progress/done + fecha), checklist de documentos requeridos con toggle/agregar/eliminar, presupuesto planeado vs real por etapa y totales, y PDF de reporte `/projects/<id>/reporte.pdf` con encabezado de empresa, tabla de etapas y checklist. Admin puede configurar etapas vía `template_id` del proyecto. Alerta de deadline en dashboard para proyectos vencidos o próximos. Nuevas rutas: `update_stage_status`, `toggle/add/delete_doc_checklist`, `update_stage_budget`, `project_progress_pdf`. |
| 2026-06-16 | **v31.4 — Company profile, project templates y disciplina en catálogo**: `company_config.py` persiste nombre, logo, dirección y RUT de la empresa; sustituye el nombre hardcoded en PDFs y la marca del sidebar. `templates_config.py` persiste plantillas de proyecto con etapas configurables (default: Residencial/Comercial). Campo `disciplina` en catálogo con filtro y migración suave al arrancar. Nuevas rutas: `/empresa`, `/empresa/logo`, `/project-templates`. Nuevos templates: `empresa.html`, `project_templates.html`. Campo `template_id` y `drive_url` en proyectos (alta y detalle). |
| 2026-06-16 | **v31.3 — Semáforo de proyecto y deadline**: `project_semaphore()` en `domain.py` — verde/amarillo/rojo/gris según `deadline` y `updated_at`. Rojo si deadline ≤3 días o inactividad ≥7 días; amarillo si deadline ≤7 días o inactividad ≥3 días; verde si hay deadline y actividad reciente; gris si no hay datos suficientes. Dashboard muestra dot de semáforo por proyecto activo. Campo `deadline` en formulario de alta y edición. `updated_at` se actualiza en cada mutación del proyecto. |
| 2026-06-19 | **v32.0 — Cotizador mobile-first (Fase 10)**: nuevo blueprint `quotes_mobile_bp` con flujo en 4 pasos bajo `/cotizar/mobile/`. Paso 1: selección de proyecto con indicador de borrador activo. Paso 2: catálogo con pills de disciplina (`filter_catalog_by_disciplina`), ítem re-agregado actualiza qty. Paso 3: revisión de ítems con subtotal/IVA/total, botón eliminar por ítem. Paso 4: finaliza borrador, asigna `quote_number`, descarga PDF directamente al browser. Borradores persistidos en `quotes.json` con `status='draft'` — sobreviven browser close y múltiples dispositivos. Auto-save en cada cambio. Atómico write en `storage.py` (`tempfile` + `os.replace`). Helpers puros en `services.py`: `filter_catalog_by_disciplina`, `upsert_mobile_draft`, `remove_item_from_draft`, `finalize_mobile_draft`. 40 tests nuevos (22 unitarios + 18 de integración). 233 tests en total. |
| 2026-06-10 | **v31.2 — Fix de duplicado de versión de bundle**: en `add_bundle_version_route` (`tracker/routes/admin.py`), la búsqueda de la versión de origen al usar "Copiar v&lt;N&gt;" en el formulario "Duplicar versión" ahora normaliza el bundle (`normalize_bundle`) antes de llamar a `_find_version`. Antes, para bundles legacy/incompletos donde el campo `version` de alguna versión faltaba o no era numérico, `_find_version` podía no encontrar la versión origen y la nueva versión se creaba sin componentes (vacía) de forma silenciosa. Búsqueda dirigida de patrones similares (buscar en copia normalizada, mutar y guardar el original desconectado) en `tracker/services.py`, `tracker/catalog.py` y `tracker/drive.py`: sin otros casos encontrados. 177 tests. |
| 2026-06-10 | **v31.1 — Ajustes de cantidades y fix de guardado de bundles**: las flechas de los campos de cantidad en cotizaciones, LDM e importación PDF ahora incrementan/decrementan en unidades enteras (`step="1"`); los componentes de bundle aceptan cualquier valor decimal (`step="any"`). Corregido bug en `_find_version` (`tracker/routes/admin.py`) que normalizaba el bundle dos veces y guardaba copias desconectadas: editar y guardar una versión de bundle no persistía los cambios (label, notas, componentes, cantidades). 177 tests. |
| 2026-06-03 | **v31.0 — Validador CSV contra catálogo**: LDM y COT ahora bloquean la importación antes del preview si alguna partida no tiene coincidencia exacta contra `catalogo.nombre` normalizado o si la unidad del CSV no coincide con `catalogo.unidad`. LDM usa el mismo matching normalizado que COT; ambos parsers agregan `csv_row_number` para errores accionables. Nuevos tests de helper, parsers y rutas. 177 tests. |
| 2026-06-03 | Versión bumped v30.0 → v31.0 (feature: validación estricta CSV LDM/COT contra catálogo). |
| 2026-05-28 | **Documentación v30.0**: se actualizan árboles reales de `templates/` y `tests/`, tabla de rutas vigentes, conteo de suite a 167 tests, pendientes de bundles directos y estado parcial de sincronización asistida/filtros en los roadmaps. |
| 2026-05-28 | **v30.0 — Detección CSV COT desde Drive + aprobación de cotizaciones + ZIP de entrega mejorado**: dropdown "Importar CSV Drive" en tab Cotización detecta archivos `{CLAVE}-v*-i*-COT-*.csv` en carpeta Drive con estado (pendiente/importado/desactualizado); ruta `/projects/<id>/quote/import-drive/<path:filename>` lee directo sin subir; upload manual se conserva como opción secundaria. Approval status de cotizaciones: una base activa por proyecto, Extraordinarias toggle independiente, migración idempotente en startup. LDM PDF simplificado: solo nombre y marca. ZIP de entrega incluye LDM PDFs y ordena archivos por fecha de modificación. 167 tests. |
| 2026-05-28 | Versión bumped v29.0 → v30.0 (features: CSV COT Drive + quote approval + ZIP LDM + meta pre-fill PDF import) |
| 2026-05-28 | **Importación PDF de proveedor a LDM**: desde Materiales se puede subir PDF, revisar extracción, mapear artículos al catálogo y crear una LDM. El extractor específico de Procables identifica partidas y metadatos cuando están disponibles. |
| 2026-05-28 | **Robustez PDF LDM**: `pdfplumber>=0.11.0` queda declarado en dependencias; la extracción se guarda temporalmente del lado servidor y la sesión conserva sólo un token; proyectos cerrados bloquean upload, mapeo y creación. |
| 2026-05-28 | **COT/LDM simplificado**: Reglas COT/LDM salen del flujo operativo visible; se retiran administración, navegación y comparación técnica. Los JSON históricos pueden permanecer inactivos sin migración destructiva. |
| 2026-05-28 | **Bundles directos**: los componentes de bundle dejan de depender de `comparison_rule_id`; la sincronización COT → LDM compara faltantes directamente por `catalog_item_id`. |
| 2026-05-28 | **Detalle de proyecto**: la antigua consistencia técnica se reemplaza por un resumen visual COT vs LDM con cotización activa, extras, costo LDM, margen y avisos básicos. |
| 2026-05-28 | **Tests**: se agregan pruebas de importación PDF a LDM y se retiran expectativas de reglas COT/LDM operativas. Suite verificada: 154 tests. |
| 2026-05-28 | Versión bumped v28.2 → v29.0 (feature: importación PDF proveedor + COT/LDM simplificado con bundles directos) |
| 2026-05-08 | Cotizaciones: se retoma el flujo de secciones en el editor; al reabrir una cotización se reconstruyen encabezados repetidos cuando la misma sección aparece en bloques separados por partidas sin sección |
| 2026-05-08 | Cotizaciones: ordenar una sección desde el formulario mueve el bloque completo (encabezado + partidas) y preserva la sección de cada partida al guardar, manteniendo reflejo consistente en vista previa y PDF sin salto de página forzado por sección |
| 2026-05-08 | Tests: nuevo `tests/test_quote_sections.py` cubre agrupación contigua de secciones y presencia de los helpers de template para reconstrucción/ordenamiento |
| 2026-05-08 | Versión bumped v27.1 → v27.2 (patch: secciones de cotización capturables y ordenables de forma estable) |
| 2026-05-23 | **LISP — COT simbología: rediseño completo** (`Lisp/CedulaRecTables.lsp`). `crt-cot-sym-collect-from-ss` ahora genera descripciones 100 % fijas del catálogo; elimina helpers `crt-cot-desc-*`. Lógica: SMB01/VAR/PZ/CONTACTO dedicado/APAGADOR dedicado → clave fija `SALLUM` + `INSTLUM`; SMB02 TAG∈A → `APA`, TAG∈C → `CTK`; SMB03 no-LED → `SALLUM`+`INSTLUM`, SMB03 LED → `SALLUM`+`INSTLED` (ML por LONGITUD). Claves fijas evitan acumulación duplicada entre bloques del mismo tipo. |
| 2026-05-23 | **LISP — cable COT**: `crt-cable-commercial-description` simplificada para delegar en `crt-cable-description`; `crt-cb-make-commercial-rows` exporta unidad `"m"` (antes `"ML"`). Resultado: 29/29 descripciones de cable COT coinciden exactamente con el catálogo LDM, habilitando auto-vinculación en importación. |
| 2026-05-23 | **Catálogo (`data/catalogo.json`)**: 494 artículos totales (472 → 494). Eliminados 7 cables desnudo fuera de alcance (calibres 2 AWG–4/0 AWG de aluminio ≥6 AWG y desnudo >14 AWG); agregados 5 cables desnudo (14–6 AWG) con IDs SHA1. Unidad corregida: `C61F3E26` (Metálico Flexible 35mm) pza→ml. +10 entradas de tubería de sesiones anteriores. +14 entradas de accesorios (PAD/Flexible 35mm/41mm/63mm: junta, conector, copa, reducción, tapón). |
| 2026-05-23 | **Tests** (`tests/test_tube_fixtures.py`): nuevo archivo con 29 tests para tubería LDM y COT. LDM: 13 tests individuales por tipo/diámetro + 2 de integración (mixto, metadatos). COT: 11 tests individuales + 3 de integración (metadatos, mixto, redondeo). Usa `csv.writer` para escape correcto de `"` en símbolos de pulgada como `(1")`. 153/153 tests pasan. |
| 2026-05-23 | Versión bumped v27.2 → v28.0 (feature: COT simbología con catálogo fijo, fix cable COT, limpieza catálogo desnudo/accesorios, fixtures de tubería) |
| 2026-05-23 | **COT import / catálogo**: `catalog_name_key` ahora normaliza acentos y separadores (`|`, paréntesis, corchetes, comillas y signos) para que el auto-link sea tolerante a variantes del CSV LISP sin perder coincidencia exacta por palabras. |
| 2026-05-23 | **Catálogo simbología COT**: agregados conceptos fijos `SALLUM`, `INSTLUM`, `INSTLED`, `CTK`, `APA` para linkeo automático de SMB01, SMB02, SMB03 LED y SMB03 no-LED al importar COT. Catálogo total: 499 artículos. |
| 2026-05-23 | **Tests** (`tests/test_quote_csv_import.py`): fixtures COT de simbología para SMB01, SMB02, SMB03-LED y SMB03 no-LED; cubren linkeo automático de `SALLUM`, `INSTLUM`, `INSTLED`, `CTK`, `APA` y normalización de acentos/separadores. |
| 2026-05-23 | Versión bumped v28.0 → v28.1 (patch: auto-vinculación robusta de simbología COT) |
| 2026-05-23 | **Verificaciones roadmap**: `CEDULARECEXPORTTAKEOFF` queda retirado del flujo activo; el redondeo operativo queda pendiente hasta cerrar bundles/reglas reales; nombres COT confirmados para SMB01/SMB02/SMB03/VAR/PZ/CONTACTO/APAGADOR, pendientes sólo especiales y HVAC. |
| 2026-05-23 | **Bundles reales iniciales** (`data/bundles.json`): sembrados bundles activos para `Desarrollo de Circuito Eléctrico` sin tubería de Iluminación, Contactos y HVAC usando cantidades explícitas de catálogo: THHW-LS 12/10/8 AWG y desnudo 12 AWG. |
| 2026-05-23 | **Tests** (`tests/test_bundles.py`): se valida que los bundles sembrados expanden una COT a materiales LDM esperados y agregan correctamente el conductor desnudo compartido. |
| 2026-05-23 | Versión bumped v28.1 → v28.2 (patch: bundles reales iniciales para circuitos sin tubería) |
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
| 2026-05-06 | LDMs: nueva exportación CSV directa desde la pestaña Materiales para cada lista existente. Endpoint `GET /projects/<id>/ldm/<lid>/csv`, descarga `LDM-....csv` con `description`, `unit`, `qty`, `catalog_item_id`, proveedor, fecha y número de lista; botón **CSV** junto a PDF. |
| 2026-05-06 | Sincronización parcial COT ↔ bundle ↔ LDM: nuevo módulo puro `tracker/ldm_sync.py` que calcula faltantes técnicos desde la COT activa y bundles, respeta reglas COT/LDM para convertir a artículo/unidad de compra y genera renglones `origen='bundle_sync'` sin sobrescribir renglones existentes ni precios capturados. |
| 2026-05-06 | Materiales: nuevo POST `/projects/<id>/ldm/<lid>/sync-bundles` y botón **Completar** por LDM. La acción agrega sólo faltantes o cantidades insuficientes detectadas por la consistencia técnica; si no hay diferencias muestra flash informativo. |
| 2026-05-06 | Tests: nuevos `tests/test_materials_csv_export.py` y `tests/test_ldm_sync.py`; `tests/test_project_detail_bundle_ui.py` cubre los botones CSV y Completar. |
| 2026-05-06 | Versión bumped v25.1 → v26.0 (feature: exportación CSV de LDM existente + sincronización parcial de LDM desde bundles). |
| 2026-05-06 | Limpieza residual de rutas/templates (mejora 4): `project_view.py` ahora preprocesa `importable_csvs` y `ldm_rows` para la pestaña Materiales; `project_detail.html` deja de filtrar CSVs y contar artículos eliminados desde Jinja. |
| 2026-05-06 | Arquitectura: eliminado `tracker/projects.py`, copia residual no registrada en `create_app()`; las rutas vigentes siguen en `tracker/routes/projects.py`. |
| 2026-05-06 | Tests: `tests/test_project_view.py` cubre los nuevos view-models de Materiales (`ldm_rows`, catálogo eliminado y CSVs importables). |
| 2026-05-06 | Versión bumped v26.0 → v26.1 (patch: limpieza residual de rutas/templates, primer corte de la mejora 4). |
| 2026-05-06 | Bug fix auditoría de catálogo eliminado: `/audit/deleted-catalog` ahora carga LDMs desde `materiales` en lugar de una llave inexistente `ldms` y deja de depender de `DATA_DIR` en `routes/quotes.py`. |
| 2026-05-06 | Auditoría de catálogo eliminado: los renglones LDM reportan precios desde `precio_cot`/`total_cot` cuando no existen `price`/`total`, preservando compatibilidad con cotizaciones. |
| 2026-05-06 | Tests: nuevo `tests/test_audit_deleted_catalog_route.py` cubre el render de `/audit/deleted-catalog` con LDMs que tienen catálogo eliminado. |
| 2026-05-06 | Versión bumped v26.1 → v26.2 (patch: fix Internal Server Error en auditoría de catálogo eliminado). |
| 2026-05-06 | Mejora 5 filtros (primer corte): nuevo `tracker/admin_filters.py` con filtros puros para proveedores y fichas técnicas, búsqueda por tokens sin acentos y listas únicas de categorías. |
| 2026-05-06 | Proveedores: `/proveedores` ahora combina búsqueda libre (nombre, contacto, email, teléfono, notas) con filtro exacto por categoría y muestra conteo visible vs. total. |
| 2026-05-06 | Fichas técnicas: `/fichas` ahora combina búsqueda por texto con tipo de equipo y estado de vinculación (`con-proyecto`/`sin-proyecto`), manteniendo la lista global más usable. |
| 2026-05-06 | Tests: nuevo `tests/test_admin_filters.py` cubre helpers puros y smoke de rutas filtradas para proveedores/fichas. |
| 2026-05-06 | Versión bumped v26.2 → v27.0 (feature: filtros administrativos combinables en proveedores y fichas técnicas). |
| 2026-05-06 | Mejora 3 limpieza residual completa: `tracker/project_view.py` prepara `task_rows`, `quote_rows`, clases de archivos Drive y `consistency_view` para que `project_detail.html` no calcule conteos, estados ni matching técnico crítico en Jinja. |
| 2026-05-06 | Consistencia en detalle de proyecto: filas comerciales y técnicas ahora llegan con clases, iconos, etiquetas, acciones sugeridas, texto de búsqueda y componentes de bundle ya asociados desde Python. |
| 2026-05-06 | Tests: `tests/test_project_view.py` amplía cobertura para filas de alcances, cotizaciones, clases Drive y view-model de consistencia; `tests/test_project_detail_bundle_ui.py` se ajusta al nuevo `consistency_view`. |
| 2026-05-06 | Versión bumped v27.0 → v27.1 (patch: limpieza residual completa de rutas/templates — mejora 3 del roadmap). |

---

## Pendientes / En desarrollo

**Alta prioridad:**
- Validar `CEDULARECEXPORTCOT` con planos reales en AutoCAD (Fase 2 del ROADMAP_INTEGRACION_LISP_CSV_APP).
- Probar los bundles reales iniciales en proyectos existentes y ajustar componentes directos COT → LDM con datos de compra.
- Ampliar bundles de salidas: las COT de salidas ya tienen un primer corte para circuitos sin tubería; falta definir tubería, accesorios, compras mínimas y componentes por familia.

**Media prioridad (ver `ROADMAP_MEJORAS.md`):**
- Completar filtros pendientes en documentos/listas globales; en el detalle de proyecto ya hay filtros para cotizaciones y LDMs.

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
