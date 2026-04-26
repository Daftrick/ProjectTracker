# Roadmap de mejoras

Este archivo guarda el backlog acordado para retomarlo en futuras conversaciones.

## En curso en esta conversación

### Riesgos técnicos
1. [x] Reducir el monolito de `app.py`.
2. [~] Reemplazar la persistencia y reglas mezcladas por módulos claros de dominio y servicios.
3. [x] Separar rutas por dominio para evitar acoplamiento.
4. [~] Sacar lógica crítica de vistas/formularios y preparar una base más fácil de probar.

### Log de avance

#### 2026-04-24
- `app.py` ya quedó como punto de entrada mínimo y delega la construcción en `tracker.create_app()`.
- Las rutas están separadas en `tracker/routes/projects.py`, `quotes.py`, `materials.py` y `admin.py`.
- La lógica común ya vive parcialmente en `tracker/domain.py`, `tracker/catalog.py`, `tracker/storage.py`, `tracker/drive.py` y `tracker/pdfs.py`.
- Se mantiene un puente de endpoints legacy para que los `url_for(...)` existentes en templates sigan funcionando después de mover rutas a blueprints.
- Verificación realizada: `python -m compileall app.py tracker` OK.
- Verificación realizada con cliente de pruebas Flask: dashboard, catálogo, proveedores, fichas, equipo, ajustes, detalle de los 4 proyectos, alta de cotización, alta de LDM, vistas de 2 cotizaciones y edición de 8 LDM responden 200.
- Datos actuales detectados: 4 proyectos, 30 tareas, 2 cotizaciones, 8 listas de materiales, 2 entregas, 458 artículos de catálogo y 4 proveedores.
- Mejora aplicada: se agregó `tracker/services.py` para concentrar creación de proyectos con tareas, sincronización de alcances y cambios de estado de tareas fuera de las vistas.
- Mejora aplicada: se agregó una suite `unittest` en `tests/test_services.py` para cubrir creación, sincronización de alcances, bloqueo por dependencias y generación de subtareas de observación.
- Verificación posterior: `python -m compileall app.py tracker tests` OK, `python -m unittest discover -s tests` OK, y las mismas rutas críticas siguen respondiendo 200.
- Mejora aplicada: se agregó `tracker/validators.py` con validadores reutilizables para proyecto, cotización y lista de materiales.
- Mejora aplicada: `project_new`, `quote_project_form` y `ldm_form` ya tienen validación de servidor para campos requeridos, fechas, alcances válidos, moneda, IVA y partidas/artículos con números válidos.
- Mejora aplicada: se agregó `tests/test_validators.py` para cubrir formularios vacíos, filas default vacías, números inválidos y casos válidos de cotización/LDM.
- Verificación posterior: `python -m compileall app.py tracker tests` OK, `python -m unittest discover -s tests` OK, POSTs inválidos no modifican `projects`, `tasks`, `quotes` ni `materiales`, y las rutas críticas siguen respondiendo 200.
- Pendiente técnico inmediato: hacer que los formularios muestren errores junto a cada campo y preserven valores capturados después de una validación fallida.

## Pendiente para otras conversaciones

### Formularios y UX
- [~] Validaciones más visibles en `project_new.html`, `quote_project_form.html` y `ldm_form.html`.
- Confirmaciones más finas en acciones destructivas.
- Filtros y búsqueda en catálogo y en formularios de cotización/LDM.

### Calidad de texto
- Mejoras de codificación/acentos para evitar textos raros.

### Negocio y consistencia
- Automatización de consistencia entre cotización y materiales.
- Mejor integración con Drive.

## Cómo retomarlo después

- En una nueva conversación, pide: `Abramos ROADMAP_MEJORAS.md y sigamos con <tema>`.
- Archivo de referencia: `H:\My Drive\Omniious\Claude Code\ProjectTracker\ROADMAP_MEJORAS.md`
- Si quieres seguir exactamente donde nos quedemos en la refactorización técnica, pide: `Continúa con los riesgos técnicos del roadmap`.
