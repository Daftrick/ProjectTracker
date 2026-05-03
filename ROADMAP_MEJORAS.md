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

---

## Pendientes vigentes

### Alta prioridad

#### 1. Evaluación de sincronización parcial COT ↔ bundle ↔ LDM (diseño pendiente)

Pregunta de diseño derivada de la mejora de auditoría visual (v25.0): ¿conviene permitir que el sistema auto-rellene cantidades en la LDM a partir de la expansión del bundle, o que propague cambios de cantidad COT a los multiplicadores del bundle?

Casos a evaluar:
- Auto-fill de LDM desde expansión de bundle al crear o actualizar una LDM.
- Propagación de cambios de cantidad en COT a cantidades esperadas sin requerir re-configurar el bundle.
- Sincronización parcial (sólo materiales faltantes, sin sobrescribir existentes).

Decisión requerida antes de implementar: esta es una pregunta de arquitectura de datos, no sólo de UI.

---

### Media prioridad

#### 4. Limpieza residual de rutas/templates

- Revisar si aún existe lógica crítica en templates.
- Mover cálculos repetidos a view-models o servicios.
- Mantener rutas enfocadas en HTTP y no en lógica de negocio.
- Seguir aumentando cobertura de tests cuando se extraiga lógica.

---

### Baja prioridad

#### 5. Filtros y búsqueda adicionales

- Mejorar filtros en vistas con muchos datos.
- Agregar búsqueda más específica en:
  - cotizaciones,
  - LDMs,
  - documentos,
  - proveedores,
  - fichas técnicas.
- Evaluar filtros por proyecto, proveedor, categoría, fecha y estado.

#### 6. Mejoras de UX general

- Pulir navegación entre tabs.
- Mejorar mensajes flash.
- Agregar indicadores de carga en acciones lentas.
- Mejorar experiencia móvil en tablas y modales.

#### 7. Exportaciones y reportes

- Revisar formato de Excel generado.
- Evaluar exportación de reportes de consistencia.
- Agregar resumen ejecutivo por proyecto.
- Evaluar reportes históricos por cliente/proveedor.

---

## Siguiente foco recomendado

Orden sugerido de trabajo:

1. **Sincronización parcial COT ↔ bundle ↔ LDM** — decidir si el sistema debe poder auto-rellenar o propagar cantidades (ítem 1, pregunta de diseño pendiente).
2. **Probar bundles reales** en proyectos existentes y ajustar reglas de equivalencia COT/LDM con datos de producción.


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