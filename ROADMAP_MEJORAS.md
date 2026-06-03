# Roadmap de mejoras — ProjectTracker

Este archivo guarda el backlog vigente para retomar mejoras en futuras conversaciones.

---

## Estado general actualizado

### Ya completado

- [x] Artículos ignorados en comparación COT/LDM: se conservan como costo del proyecto, pero no se atribuyen directamente al cliente en el cruce.
- [x] Reducir el monolito de `app.py`.
- [x] Separar rutas por dominio en blueprints.
- [x] Crear módulos claros para dominio, almacenamiento, catálogo, Drive, PDFs y validaciones.
- [x] Extraer lógica de negocio a `tracker/services.py`.
- [x] Agregar validaciones de servidor para proyectos, cotizaciones y LDMs.
- [x] Mostrar errores inline y conservar captura en formularios principales.
- [x] Agregar validaciones inline en formularios administrativos.
- [x] Agregar búsqueda por tokens y categorías en catálogo.
- [x] Agregar filtro inline en partidas de cotizaciones y LDMs.
- [x] Implementar consistencia COT vs LDM como primera versión funcional.
- [x] Agregar KPI de consistencia en dashboard y tab dedicado en detalle de proyecto.
- [x] Mejorar integración Drive con rutas multiplataforma.
- [x] Guardar PDFs y Excel de cotización/LDM en carpeta Drive del proyecto.
- [x] Agregar pruebas unitarias para servicios, validaciones, catálogo, Drive, consistencia y eliminaciones.
- [x] Fase 1 — Núcleo de bundles versionados y reglas de comparación técnica COT/LDM. Implementado en v19.0.
- [x] Fase 2 — UI Admin para bundles versionados y reglas de comparación COT/LDM. Implementado en v20.0.
- [x] Fase 3 — Visualización de consistencia técnica por bundles en detalle de proyecto. Implementado en v21.0.
- [x] Mejora 4 — Corrección de acentos y codificación: auditoría completa de templates, validators, rutas y PDFs. Únicos bugs reales encontrados en `build_ldm_pdf` ("Pagina" → "Página", "DESCRIPCION" → "DESCRIPCIÓN"). Implementado en v23.1.
- [x] Revisión de datos históricos con catálogo eliminado: sistema completo de auditoría visual con badges, flujo de tres acciones (preservar/reconectar/purgar) y página dedicada. Implementado en v24.0.
- [x] Integración Drive mejorada: `scan_drive_folder` con tipos de error diferenciados, detección de `missing_base`, fix de bug de caché, creación automática de carpeta desde UI, alertas de archivos faltantes y validación de rutas en Ajustes. Implementado en v24.1.
- [x] Auditoría visual de consistencia COT/LDM con bundles (ítem 1): tabla de materiales esperados vs. LDM real con vistas "Por material" y "Por bundle"; alertas diferenciadas para bundles sin versión activa, componentes sin regla de comparación y componentes inválidos; panel de acciones sugeridas técnicas con prioridad; columna de acción sugerida por fila. Implementado en v25.0.
- [x] Confirmaciones destructivas estandarizadas (ítem 2): modal Bootstrap reutilizable `#modalConfirmDelete` con detalle de impacto antes de ejecutar. Cotización (tipo/fecha/partidas/total), LDM (proveedor/artículos/costo), entrega (versión/tipo/archivos + nota ZIP), ficha técnica (tipo/marca/modelo + proyectos vinculados), proveedor (categoría/contacto), miembro de equipo (rol/email), purge catálogo (lista de artículos), catálogo individual con fetch previo de referencias. Implementado en v25.1.
- [x] Exportación CSV explícita de LDM existente: botón **CSV** por lista en la pestaña Materiales, endpoint de descarga y prueba de ruta. Implementado en v26.0.
- [x] Sincronización parcial COT ↔ bundle ↔ LDM: primera versión para agregar faltantes técnicos calculados desde la COT activa y bundles, sin sobrescribir renglones ni precios existentes. Implementado en v26.0; el botón visible y las reglas COT/LDM fueron retirados en v29.0.
- [x] Mejora 4 — Limpieza residual de rutas/templates (primer corte): la pestaña Materiales ahora recibe `importable_csvs` y `ldm_rows` desde `project_view.py`, con conteos de artículos y catálogo eliminado fuera de Jinja; se retiró `tracker/projects.py`, copia residual no registrada. Implementado en v26.1.
- [x] Mejora 5 — Filtros y búsqueda adicionales (primer corte): proveedores ahora filtra por búsqueda libre y categoría; fichas técnicas filtra por texto, tipo y vinculación a proyectos, con lógica pura testeada en `admin_filters.py`. Implementado en v27.0.
- [x] Mejora 3 — Limpieza residual completa de rutas/templates: `project_view.py` prepara filas de alcances, cotizaciones, Drive y consistencia; `project_detail.html` deja de hacer conteos, matching técnico, mapas de estado y clases de UI críticas en Jinja. Implementado en v27.1.
- [x] Bundles reales iniciales: desarrollo de circuito sin tubería para iluminación, contactos y HVAC, derivados de cantidades explícitas en catálogo. Implementado en v28.2.
- [x] Simplificación COT vs LDM: la vista de detalle queda como resumen visual de cotización activa, extras, costo LDM, margen y avisos básicos, sin comparación técnica por bundles ni diagnósticos por artículo. Implementado en v29.0.
- [x] Bundles directos: se retira `comparison_rule_id` de componentes y la sincronización usa `catalog_item_id` como base directa COT → LDM. Implementado en v29.0.
- [x] Importación PDF de proveedor a LDM: upload, preview/mapeo a catálogo y creación de LDM desde PDF, con extractor específico Procables y payload temporal fuera de cookie de sesión. Implementado en v29.0.
- [x] Quote approval status: una cotización base activa por proyecto (General/Preliminar), Extraordinarias toggle independiente. Migración idempotente en startup, botón Aprobar/Toggle por fila en UI. Implementado en v30.0.
- [x] LDM PDF simplificado: solo nombre y marca del material (sin descripción técnica) para PDFs enviados a proveedores. Implementado en v30.0.
- [x] Importación PDF de proveedor a LDM con pre-fill de metadatos: extractor Procables detecta cot_number, fecha y proveedor; el formulario de mapeo los pre-puebla automáticamente. Implementado en v30.0.
- [x] ZIP de entrega mejorado: incluye PDFs LDM (`LDM-*.pdf`), ordena archivos por fecha de modificación (no alfabético), checkbox independiente para LDM PDFs en entrega parcial. Implementado en v30.0.
- [x] Detección de CSV COT desde Drive: `{CLAVE}-v*-i*-COT-*.csv` detectados en carpeta Drive con estado (pendiente/importado/desactualizado); dropdown en tab Cotización importa directo sin subir archivo; upload manual conservado como opción secundaria. Implementado en v30.0.
- [x] Filtros en detalle de proyecto para cotizaciones y LDMs: búsqueda local por texto/estado en el tab Cotización y filtro de LDMs en Materiales. Implementado en v30.0.
- [x] Sincronización asistida inicial al crear LDM nueva: botón "Sugerir desde bundles" precarga faltantes derivados de la COT activa y conserva origen/metadatos de sincronización al guardar. Implementado en v30.0.
- [x] Validador CSV contra catálogo: importaciones LDM y COT bloquean antes del preview si `description` no coincide con `catalogo.nombre` normalizado o si `unit` no coincide con `catalogo.unidad`; errores incluyen fila de origen. Implementado en v31.0.

---

## Pendientes vigentes

### Alta prioridad

#### 1. Probar bundles reales y ajustar componentes directos COT → LDM

Validar la sincronización parcial con proyectos existentes:
- Ampliar bundles de salidas: los 3 bundles iniciales ya expanden circuitos sin tubería; falta cubrir tubería, accesorios y compras mínimas por familia.
- Definir cómo los metros de tubería generan accesorios faltantes después de descontar lo incluido en salidas.
- Revisar que las cantidades agregadas por sincronización coincidan con compras reales por proveedor.
- Si se requieren conversiones o redondeos, agregarlos como campos propios del componente de bundle, no como tabla separada de reglas.
- Detectar si se requiere agrupar sugerencias por proveedor o disciplina antes de crear/actualizar LDMs.

#### 2. Siguiente fase de sincronización asistida

Primera versión ya implementada: una LDM nueva puede precargarse desde bundles con origen/metadatos de sincronización. Falta endurecer el flujo operativo:
- Asistente de selección de faltantes por proveedor/disciplina antes de agregar.
- Proponer faltantes en una LDM existente sin sobrescribir captura existente.
- Mostrar diff antes de agregar filas.
- Propagación visual de cambios de cantidad COT a faltantes sugeridos, sin modificar bundles base.

---

### Baja prioridad

#### 3. Filtros y búsqueda restantes

- El detalle de proyecto ya tiene filtros para cotizaciones y LDMs.
- Extender el patrón de filtros combinables a documentos y, si se reactivan, listas globales.
- Evaluar filtros por proyecto, proveedor, categoría, fecha y estado.
- Revisar si conviene extraer view-models para listas globales antes de agregar más filtros.

#### 4. Mejoras de UX general

- Pulir navegación entre tabs.
- Mejorar mensajes flash.
- Agregar indicadores de carga en acciones lentas.
- Mejorar experiencia móvil en tablas y modales.
- Extender importación PDF a otros proveedores sólo cuando haya formatos recurrentes claros; mantener Procables como extractor específico y fallback genérico.

#### 5. Exportaciones y reportes

- Revisar formato de Excel generado.
- Evaluar exportación de reportes de consistencia.
- Agregar resumen ejecutivo por proyecto.
- Evaluar reportes históricos por cliente/proveedor.

---

## Siguiente foco recomendado

Orden sugerido de trabajo:

1. **Ampliar bundles de salidas** con componentes y cantidades reales de tubería, accesorios y compras mínimas; los 3 bundles iniciales ya tienen componentes base para circuitos sin tubería.
2. **Probar bundles reales** en proyectos existentes y ajustar componentes directos COT → LDM con datos de producción.
3. **Siguiente fase de sincronización asistida** — convertir el auto-fill inicial en asistente con diff, selección parcial y agrupación por proveedor/disciplina.
4. **Mejorar corrección de CSVs rechazados** — mostrar una vista dedicada con sugerencias de catálogo cercanas y export de reporte de errores, si los flashes quedan cortos para operación diaria.
5. **Filtros restantes** — documentos y listas globales si vuelven a ser necesarias.


---

## Checklist al cerrar una mejora

Al cerrar cualquier cambio:

1. Actualizar `APP_VERSION` en `tracker/domain.py`.
2. Actualizar `## Versión actual` en `VERSIONES.md`.
3. Agregar entrada en `## Historial de cambios recientes`.
4. Actualizar este roadmap:
   - mover pendientes cerrados a completados,
   - agregar nuevos pendientes detectados,
   - ajustar prioridad si aplica.
5. Ejecutar pruebas:

```bash
python -m compileall app.py tracker tests
python -m unittest discover -s tests
