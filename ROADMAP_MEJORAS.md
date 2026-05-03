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

---

## Pendientes vigentes

### Alta prioridad

#### 1. Auditoría visual de consistencia COT/LDM

- Mejorar la lectura visual de diferencias entre cotización y LDM en la nueva capa técnica de bundles.
- Mostrar en el detalle del proyecto una tabla específica de materiales esperados por bundle contra LDM real.
- Destacar:
  - faltantes en LDM,
  - excedentes en LDM,
  - diferencias de cantidad,
  - bundles sin versión activa,
  - componentes sin regla de comparación cuando aplique conversión COT/LDM.
- Agregar acciones sugeridas para corregir inconsistencias.
- Evaluar si conviene permitir sincronización parcial entre COT, bundle y LDM.

#### 2. Auditoría visual de consistencia COT/LDM

- Mejorar la lectura visual de diferencias entre cotización y LDM en la nueva capa técnica de bundles.
- Mostrar en el detalle del proyecto una tabla específica de materiales esperados por bundle contra LDM real.
- Destacar:
  - faltantes en LDM,
  - excedentes en LDM,
  - diferencias de cantidad,
  - bundles sin versión activa,
  - componentes sin regla de comparación cuando aplique conversión COT/LDM.
- Agregar acciones sugeridas para corregir inconsistencias.
- Evaluar si conviene permitir sincronización parcial entre COT, bundle y LDM.

#### 2. Confirmaciones destructivas pendientes

Estandarizar confirmaciones para acciones críticas:

- Eliminar cotización.
- Eliminar LDM.
- Eliminar entrega.
- Eliminar ficha técnica.
- Eliminar proveedor.
- Eliminar miembro de equipo.
- Purgar partidas de catálogo eliminado.
- Eliminar artículos del catálogo con referencias existentes.

Las confirmaciones deben mostrar impacto antes de ejecutar la acción.

---

### Media prioridad

#### 4. Integración Drive avanzada

- Crear automáticamente carpeta de proyecto si no existe.
- Validar rutas configuradas con mensajes más claros.
- Detectar mejor archivos esperados por proyecto.
- Mejorar clasificación de documentos en la pestaña Drive.
- Agregar alertas cuando falten archivos base del proyecto.

#### 5. Limpieza residual de rutas/templates

- Revisar si aún existe lógica crítica en templates.
- Mover cálculos repetidos a view-models o servicios.
- Mantener rutas enfocadas en HTTP y no en lógica de negocio.
- Seguir aumentando cobertura de tests cuando se extraiga lógica.

---

### Baja prioridad

#### 6. Filtros y búsqueda adicionales

- Mejorar filtros en vistas con muchos datos.
- Agregar búsqueda más específica en:
  - cotizaciones,
  - LDMs,
  - documentos,
  - proveedores,
  - fichas técnicas.
- Evaluar filtros por proyecto, proveedor, categoría, fecha y estado.

#### 7. Mejoras de UX general

- Pulir navegación entre tabs.
- Mejorar mensajes flash.
- Agregar indicadores de carga en acciones lentas.
- Mejorar experiencia móvil en tablas y modales.

#### 8. Exportaciones y reportes

- Revisar formato de Excel generado.
- Evaluar exportación de reportes de consistencia.
- Agregar resumen ejecutivo por proyecto.
- Evaluar reportes históricos por cliente/proveedor.

---

## Siguiente foco recomendado

Orden sugerido de trabajo:

1. Probar artículos ignorados en comparación COT/LDM con proyectos reales.
2. Mejorar navegación desde un issue técnico hacia el bundle, regla o artículo ignorado que lo genera.
3. Evaluar reportes/exportación de consistencia comercial y técnica.


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