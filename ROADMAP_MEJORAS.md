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
- [x] Sincronización parcial COT ↔ bundle ↔ LDM: botón **Completar** por LDM existente para agregar sólo faltantes técnicos calculados desde la COT activa y bundles, respetando reglas COT/LDM, sin sobrescribir renglones ni precios existentes. Implementado en v26.0.
- [x] Mejora 4 — Limpieza residual de rutas/templates (primer corte): la pestaña Materiales ahora recibe `importable_csvs` y `ldm_rows` desde `project_view.py`, con conteos de artículos y catálogo eliminado fuera de Jinja; se retiró `tracker/projects.py`, copia residual no registrada. Implementado en v26.1.
- [x] Mejora 5 — Filtros y búsqueda adicionales (primer corte): proveedores ahora filtra por búsqueda libre y categoría; fichas técnicas filtra por texto, tipo y vinculación a proyectos, con lógica pura testeada en `admin_filters.py`. Implementado en v27.0.
- [x] Mejora 3 — Limpieza residual completa de rutas/templates: `project_view.py` prepara filas de alcances, cotizaciones, Drive y consistencia; `project_detail.html` deja de hacer conteos, matching técnico, mapas de estado y clases de UI críticas en Jinja. Implementado en v27.1.
- [x] Bundles reales iniciales: desarrollo de circuito sin tubería para iluminación, contactos y HVAC, derivados de cantidades explícitas en catálogo. Implementado en v28.2.

---

## Pendientes vigentes

### Alta prioridad

#### 1. Probar bundles reales y ajustar reglas de equivalencia COT/LDM

Validar la sincronización parcial con proyectos existentes:
- Completar bundles de salidas: las COT de salidas incluyen metros de cable, tubería y accesorios para LDM.
- Definir cómo los metros de tubería generan accesorios faltantes después de descontar lo incluido en salidas.
- Revisar que las cantidades agregadas por **Completar** coincidan con compras reales por proveedor.
- Ajustar reglas con conversión y redondeo cuando el material se compra en unidad distinta (tramo, rollo, paquete).
- Detectar si se requiere agrupar sugerencias por proveedor o disciplina antes de crear/actualizar LDMs.

#### 2. Siguiente fase de sincronización asistida

Evaluar después de pruebas reales:
- Auto-fill de LDM desde expansión de bundle al crear una LDM nueva.
- Asistente de selección de faltantes por proveedor/disciplina antes de agregar.
- Propagación visual de cambios de cantidad COT a faltantes sugeridos, sin modificar bundles base.

---

### Baja prioridad

#### 3. Filtros y búsqueda restantes

- Extender el patrón de filtros combinables ya aplicado en proveedores y fichas técnicas a:
  - cotizaciones,
  - LDMs,
  - documentos.
- Evaluar filtros por proyecto, proveedor, categoría, fecha y estado.
- Revisar si conviene extraer view-models para listas globales antes de agregar más filtros.

#### 4. Mejoras de UX general

- Pulir navegación entre tabs.
- Mejorar mensajes flash.
- Agregar indicadores de carga en acciones lentas.
- Mejorar experiencia móvil en tablas y modales.

#### 5. Exportaciones y reportes

- Revisar formato de Excel generado.
- Evaluar exportación de reportes de consistencia.
- Agregar resumen ejecutivo por proyecto.
- Evaluar reportes históricos por cliente/proveedor.

---

## Siguiente foco recomendado

Orden sugerido de trabajo:

1. **Completar bundles de salidas** con componentes y cantidades reales de cable, tubería y accesorios.
2. **Probar bundles reales** en proyectos existentes y ajustar reglas de equivalencia COT/LDM con datos de producción.
3. **Siguiente fase de sincronización asistida** — decidir si conviene auto-fill al crear LDM nueva o asistente por proveedor/disciplina.


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
