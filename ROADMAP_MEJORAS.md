# Roadmap de mejoras — ProjectTracker

Este archivo guarda el backlog vigente para retomar mejoras en futuras conversaciones.

---

## Estado general actualizado

### Ya completado

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
- [x] Mejorar auditoría visual COT/LDM con margen bajo por artículo, cobertura de catálogo, filtro y acciones sugeridas.

---

## Pendientes vigentes

### Alta prioridad

#### 1. Consistencia COT/LDM — fase siguiente

- Evaluar si conviene permitir sincronización parcial entre COT y LDM.
- Agregar flujo guiado para reconectar partidas sin catálogo.
- Evaluar exportación del reporte de consistencia a Excel/PDF.
- Revisar si los umbrales de margen deben configurarse por categoría.

#### 2. Revisión de datos históricos con catálogo eliminado

- Auditar cotizaciones y LDMs con partidas marcadas como catálogo eliminado.
- Mejorar los badges o alertas visuales.
- Definir flujo claro para:
  - conservar partida histórica,
  - reconectar a nuevo artículo de catálogo,
  - purgar partida definitivamente.

#### 3. Confirmaciones destructivas pendientes

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

#### 4. Mejoras de codificación, acentos y textos

- Revisar textos raros por codificación.
- Corregir acentos en vistas, PDFs y mensajes flash.
- Normalizar textos de botones, títulos y mensajes del sistema.
- Verificar compatibilidad con caracteres especiales en PDF.

#### 5. Integración Drive avanzada

- Crear automáticamente carpeta de proyecto si no existe.
- Validar rutas configuradas con mensajes más claros.
- Detectar mejor archivos esperados por proyecto.
- Mejorar clasificación de documentos en la pestaña Drive.
- Agregar alertas cuando falten archivos base del proyecto.

#### 6. Limpieza residual de rutas/templates

- Revisar si aún existe lógica crítica en templates.
- Mover cálculos repetidos a view-models o servicios.
- Mantener rutas enfocadas en HTTP y no en lógica de negocio.
- Seguir aumentando cobertura de tests cuando se extraiga lógica.

---

### Baja prioridad

#### 7. Filtros y búsqueda adicionales

- Mejorar filtros en vistas con muchos datos.
- Agregar búsqueda más específica en:
  - cotizaciones,
  - LDMs,
  - documentos,
  - proveedores,
  - fichas técnicas.
- Evaluar filtros por proyecto, proveedor, categoría, fecha y estado.

#### 8. Mejoras de UX general

- Pulir navegación entre tabs.
- Mejorar mensajes flash.
- Agregar indicadores de carga en acciones lentas.
- Mejorar experiencia móvil en tablas y modales.

#### 9. Exportaciones y reportes

- Revisar formato de Excel generado.
- Evaluar exportación de reportes de consistencia.
- Agregar resumen ejecutivo por proyecto.
- Evaluar reportes históricos por cliente/proveedor.

---

## Siguiente foco recomendado

Orden sugerido de trabajo:

1. Auditoría visual y corrección guiada de consistencia COT/LDM.
2. Confirmaciones destructivas restantes.
3. Revisión de partidas históricas con catálogo eliminado.
4. Creación automática de carpetas Drive.
5. Corrección de acentos/codificación en vistas y PDFs.

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