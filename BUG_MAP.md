# Mapeo de bugs de ProjectTracker

Fecha: 11 de octubre de 2026. Código investigado: `bcab0c5` en `main`.

Estado: **13 bugs corregidos y verificados (BUG-01 a BUG-13)**.
Método: `investigate`, con navegación por Graphify, revisión de cambios,
hipótesis, reproducciones aisladas y comprobaciones de navegador con `browse`.
El diagnóstico inicial corresponde a `bcab0c5`. La corrección posterior modifica
la aplicación y convierte las trece reproducciones en comprobaciones del
comportamiento correcto. Las causas y evidencias iniciales se conservan abajo
como registro del diagnóstico.

## Correcciones de los siete prioritarios

- **BUG-01:** Flask sirve `static/` de la raíz. El JavaScript devuelve HTTP 200
  y los dos editores cargan los controles de términos.
- **BUG-02:** eliminar un proyecto exige administrador, aunque el cotizador
  tenga todos los permisos individuales habilitados.
- **BUG-03:** los seis permisos se comprueban en el servidor. Leer cotizaciones
  exige `view_quotes`; editarlas (incluidos PDF, móvil y LDM), además,
  `edit_quotes`. Exportar exige `download_files`; importar, `upload_files`.
  Editar proyectos y gestionar avances/checklists usan sus respectivos permisos.
  Los resúmenes de proyectos tampoco exponen cotizaciones o pagos cuando falta
  el permiso de lectura. Los administradores conservan acceso completo.
- **BUG-04:** todas las rutas de documentos con proyecto y cotización/LDM en la
  URL comprueban esa relación antes de consultar, exportar o modificar datos.
- **BUG-05:** cada petición mantiene un bloqueo reentrante durante el ciclo
  completo de lectura/modificación/guardado, compartido entre hilos y procesos.
  Los guardados se preparan y se descartan si la petición falla; se publican al
  terminar correctamente. Las migraciones también usan este contexto.
  Los scripts que modifican datos deben usar `with storage.transaction():`
  alrededor de todo el ciclo; `load()` y `save()` aislados no forman una
  transacción conjunta. No resuelve formularios antiguos que envían el mismo
  campo completo con valores distintos ni sustituye un historial de versiones.
  El bloqueo serializa peticiones con datos: una generación PDF larga puede
  hacer esperar a otra petición. Los cambios entre varios archivos no son una
  transacción duradera frente a una caída del sistema durante la publicación.
- **BUG-06:** sin contraseña configurada se genera un secreto aleatorio de
  24 bytes. Las cuentas existentes conservan su contraseña; quien todavía use
  la inicial anterior debe cambiarla en Usuarios. El restablecimiento por
  variables de entorno sigue requiriendo `PROJECT_TRACKER_ADMIN_RESET=1`.
- **BUG-07:** formularios y CSV rechazan números no finitos; pagos validan fecha
  real con formato AAAA-MM-DD; las API de precios/costos y cantidades móviles
  rechazan entradas inválidas. La capa JSON impide guardar NaN o infinito y
  conserva los archivos previos ante un error.

Los cotizadores con permisos sin marcar ahora tienen ese acceso deshabilitado.
Revisar sus casillas en **Usuarios** antes de distribuir esta actualización.
El bloqueo entre procesos se verificó en macOS; incluye una implementación para
Windows, cuya ejecución no se probó en esta máquina.

Verificación automatizada: `tests/test_priority_bugs.py`, con bases temporales,
pruebas concurrentes entre peticiones y procesos, denegaciones sin mutación,
operaciones autorizadas y validación financiera. Las regresiones nuevas fallan
al ejecutarlas contra el código anterior (`2eb1b61`).

Verificación de esta primera etapa: **529 pruebas, OK, 2 omitidas** (las omisiones ya existían),
23 rutas principales con HTTP 200 y diagnóstico aislado con 7 P1 resueltos y
6 P2 reproducidos. En navegador, con CSRF activo, funcionan agregar, aplicar
plantilla, eliminar e incluir términos; los cambios guardados desde cada editor
aparecen en el otro y en el PDF generado. El cotizador no puede borrar el
proyecto. El nombre de portada conserva los 24 pt solicitados.

## Correcciones de los seis restantes

- **BUG-08:** se impide borrar una cotización o proyecto con pagos registrados.
  Se conserva el historial financiero; una cotización puede marcarse obsoleta
  y un proyecto cerrarse. El borrado sin pagos sigue disponible. No se eliminan
  ni se reparan automáticamente pagos huérfanos que ya existieran.
- **BUG-09:** una comprobación compartida exige reabrir el proyecto antes de
  cambiar sus documentos, datos, avances o vínculos con fichas técnicas.
  Cubre los editores principal/PDF/LDM, importaciones, API de costo y móvil,
  incluido el reinicio de borrador mediante `nueva=1`. Consultar, exportar y
  gestionar pagos sigue disponible después del cierre.
- **BUG-10:** tablero y detalle comparten el criterio de cotización activa y
  calculan sus totales con los mismos datos actualizados. Excluyen borradores,
  obsoletas y borradores técnicos móviles; los registros antiguos sin estado
  de aprobación mantienen su tratamiento como activos.
- **BUG-11:** el texto de portada se distribuye en líneas y páginas antes del
  resumen económico. El nombre completo mantiene 24 pt en portada normal y
  18 pt en reducida. Los nombres muy largos pueden añadir páginas de
  continuación; los cortos conservan la distribución anterior.
- **BUG-12:** el tamaño de compra acepta coma decimal y exige un número finito
  mayor a cero, o vacío cuando es opcional. Crear y editar muestran un error
  sin modificar el catálogo. El formulario de alta conserva la selección
  fraccionable y muestra el campo y su error para poder corregirlo.
- **BUG-13:** `next` admite únicamente rutas locales sin sintaxis ambigua.
  El inicio de sesión conserva la ruta y los parámetros originales. Los
  formularios de pagos y de estado de cotización usan la misma validación.

Verificación final: **541 pruebas, OK, 2 omitidas**; 12 regresiones nuevas en
`tests/test_remaining_bugs.py`, con almacenamiento y usuarios temporales. Las
regresiones de los seis bugs fallan contra `02d432f`, antes de estos cambios.
El diagnóstico aislado verifica **13 resueltos y 0 pendientes**, además de
23 rutas principales con HTTP 200. En navegador, con CSRF activo, se verificó
el error visible del tamaño de compra y el guardado después de corregirlo,
el bloqueo de borrado con pagos y el rechazo de cambios PDF/móviles tras cerrar
el proyecto. Sin errores de consola durante estas comprobaciones.

La comprobación PDF extrae el texto completo y sus coordenadas para nombres
cortos, de 731 y de 2924 caracteres, en portada normal y reducida. También se
renderizaron e inspeccionaron las portadas y páginas de continuación, sin
superposición con el resumen económico.

## Resultado y prioridades

P1 = alta: pérdida de datos, controles de acceso que no se cumplen o funcionalidad
principal rota. P2 = media: incoherencia financiera, error de validación o
presentación. Las prioridades indican el orden propuesto de corrección, no una
afirmación sobre incidentes ocurridos en producción.

| ID | Prioridad | Área | Fallo confirmado |
| --- | --- | --- | --- |
| BUG-01 | P1 | Términos / archivos estáticos | El JavaScript del editor devuelve 404; los botones no funcionan. |
| BUG-02 | P1 | Proyectos / roles | Un cotizador puede eliminar un proyecto y sus documentos. |
| BUG-03 | P1 | Permisos individuales | Desactivar permisos de lectura y edición no impide leer ni editar cotizaciones. |
| BUG-04 | P1 | Cotizaciones / LDM | Algunas rutas aceptan documentos de un proyecto distinto al indicado en la URL. |
| BUG-05 | P1 | Almacenamiento | Dos lecturas seguidas de guardados pueden perder cambios del primer editor. |
| BUG-06 | P1 | Alta inicial de administrador | Sin configuración se crea un administrador con contraseña fija incluida en el código. |
| BUG-07 | P1 | Validación financiera | Se aceptan `NaN` en pagos y cantidades de cotizaciones; las fechas de pago tampoco se validan. |
| BUG-08 | P2 | Pagos / borrados | Al borrar cotizaciones o proyectos quedan pagos huérfanos. |
| BUG-09 | P2 | Proyectos cerrados | El editor PDF y el flujo móvil permiten cambios sin reabrir el proyecto. |
| BUG-10 | P2 | Tablero / finanzas | El tablero suma cotizaciones borrador y obsoletas; el detalle suma las activas. |
| BUG-11 | P2 | Portada PDF | Un nombre largo invade el recuadro fijo de datos y totales. |
| BUG-12 | P2 | Catálogo | Un tamaño de compra con coma decimal provoca una excepción sin validación. |
| BUG-13 | P2 | Inicio de sesión | El parámetro `next` acepta redirigir a un sitio externo. |

## Reproducción segura y repetible

```bash
mise exec -- python tools/investigate_bug_map.py
```

El programa usa registros sintéticos, archivos JSON y SQLite temporales.
Redirige `storage.FILES`, los directorios de inicialización y `AUTH_DB` antes de
crear la aplicación. No modifica los datos reales ni llama a servicios externos.
Produce `findings.json`, `smoke.json` y `long-title.pdf` en el directorio temporal
`projecttracker-investigate`. Se puede elegir otro destino con `--output-dir`.

Las aserciones verifican las trece correcciones.
El resultado esperado es «Verified fixes: 13» y «Pending findings: 0».
Cada entrada de `findings.json` incluye el estado `resolved`.
No se agrega este programa a la suite normal ni a CI.

Para comprobar el navegador con datos temporales:

```bash
mise exec -- python tools/investigate_bug_map.py --serve
```

Abre únicamente `127.0.0.1:5099`; la sesión de prueba usa el usuario `audit-user`
y la contraseña sintética `Synthetic-User-Password-Only`. El modo navegador activa
CSRF. Al detener el programa se descartan los datos temporales. Estos usuarios y
contraseñas pertenecen exclusivamente a la instancia sintética.

## Evidencia y causas del diagnóstico inicial

### BUG-01: JavaScript de términos inaccesible

- Síntoma: «Agregar término» no hace nada en el editor principal ni en el PDF.
- Causa: [create_app](tracker/__init__.py#L54) configura la carpeta de plantillas,
  pero deja la carpeta estática predeterminada en `tracker/static`.
  [_quote_terms_editor.html](templates/_quote_terms_editor.html#L40) pide
  `/static/quote_terms_editor.js`, que existe en `static/` de la raíz.
- Evidencia: respuesta HTTP 404 pese a existir el archivo. En navegador, abrir el
  panel y pulsar «Agregar término» mantiene el número de filas en 0, en ambos
  editores. La consola y el servidor registran el 404. Aplicar plantilla, eliminar
  y sincronizar «Incluir en PDF» también dependen de este archivo.
- Origen: la incorporación del editor compartido en `ff8e484` añadió esta
  dependencia sin una comprobación de carga real del recurso.
- Corrección propuesta: alinear la carpeta estática de Flask con los archivos
  del proyecto y probar la descarga del script y una interacción de navegador.

### BUG-02: eliminación de proyectos sin control de administrador

- Causa: [delete_project](tracker/routes/projects.py#L222) carece de
  `@admin_required`. La regla global solamente exige autenticación.
- Evidencia: sesión real de cotizador, `POST /projects/P1/delete`, respuesta 302 y
  proyecto eliminado. Se confirmó también en navegador con CSRF activo, borrando
  el proyecto sintético P2. Como control, `/usuarios` sí rechaza al cotizador.
- Contradicción documental: `VERSIONES.md`, v45.6, declara que eliminar proyectos
  requiere administrador. El código actual no implementa esa protección.
- Corrección propuesta: validar el rol en la ruta y cubrir la denegación sin
  cambios en proyectos ni registros relacionados.

### BUG-03: permisos individuales sin efecto

- Causa: [permission_required](tracker/auth.py#L234) existe pero ninguna ruta lo
  utiliza. La UI de usuarios promete permisos para leer y editar cotizaciones,
  editar proyectos, gestionar tareas y transferir archivos.
- Evidencia: cotizador con `permissions={}` obtiene HTTP 200 en `/cotizaciones`
  y guarda un nombre distinto desde el editor PDF. Este último guardado también
  se verificó en navegador con CSRF activo.
- Alcance confirmado: lectura de cotizaciones y escritura del editor PDF.
  El resto de permisos comparte la ausencia de integración; requiere una matriz
  explícita de autorización al corregir, respetando las acciones que sí deben
  seguir disponibles a cotizadores.
- Corrección propuesta: definir y aplicar los permisos por operación en el
  servidor; ocultar botones por sí solo no hace cumplir los permisos.

### BUG-04: relación proyecto-documento sin validar en algunas rutas

- Causa: [edit_quote](tracker/routes/quotes.py#L320) y
  [delete_quote](tracker/routes/quotes.py#L468) buscan por ID de cotización sin
  comprobar su proyecto. Lo mismo ocurre en las rutas de edición, editor PDF y
  borrado de [materiales](tracker/routes/materials.py#L380).
- Evidencia: Q1 pertenece a P1, pero `/projects/P2/quote/Q1/edit` devuelve 200 y
  `POST /projects/P2/quote/Q1/delete` elimina Q1. L1 pertenece a P1, pero el editor
  de P2 permite cambiar su nombre y la ruta de borrado de P2 elimina L1.
- Control: el editor PDF de cotizaciones sí rechaza la combinación P2/Q1 con 302.
- Corrección propuesta: resolver cada documento con su ID y `project_id` juntos
  antes de leerlo, modificarlo o borrarlo; probar combinaciones incompatibles.

### BUG-05: pérdida de cambios entre dos editores

- Causa: [storage](tracker/storage.py#L40) bloquea cada `load` y `save`, pero no el
  ciclo completo de lectura, modificación y escritura. Guardar reemplaza toda la
  colección. La escritura atómica evita archivos incompletos, pero no este caso.
- Evidencia: A y B leen la misma cotización; A cambia el nombre y guarda; B cambia
  una nota y guarda su copia anterior. La nota de B persiste y el nombre de A se
  pierde. La reproducción es determinista, sin depender de carreras difíciles.
- Conocido: el comentario de `storage.py` reconoce esta limitación. No requiere
  dos máquinas trabajando a la vez; pueden ser dos solicitudes o pestañas.
- Corrección propuesta: detectar versiones desactualizadas o realizar las
  actualizaciones dentro de una transacción; valorar persistencia transaccional.

### BUG-06: contraseña administrativa inicial fija

- Causa: [_default_admin_config](tracker/auth.py#L56) tiene una contraseña
  predeterminada fija. Por ello la generación aleatoria de `_ensure_default_admin`
  no se alcanza cuando falta la variable de entorno.
- Evidencia: en una base temporal nueva, sin variables de configuración, el
  administrador acepta la contraseña predeterminada del código. El programa no
  imprime ni guarda esa contraseña en el informe.
- Alcance: instalaciones nuevas sin configurar
  `PROJECT_TRACKER_ADMIN_PASSWORD`. No se comprobó la configuración del servidor
  de producción ni se afirma que use ese valor.
- Corrección propuesta: exigir configuración explícita o generar una credencial
  única de inicialización; revisar el estado de instalaciones existentes.

### BUG-07: números no finitos y fechas inválidas

- Causa: [parse_form_float](tracker/utils.py#L10) y
  [_clean_payment_form](tracker/routes/quotes.py#L402) convierten con `float` sin
  exigir un número finito. Comparar `NaN <= 0` no lo rechaza. El pago solamente
  exige que la fecha no esté vacía.
- Evidencia: `amount=NaN`, `date=not-a-date` guarda un pago. Una cotización con
  `item_qty[]=NaN` pasa `validate_quote_form` con `ok=True` y subtotal `NaN`.
- Impacto: montos inválidos se propagan a saldos y datos JSON.
- Corrección propuesta: validar finitud y rangos en todos los caminos de entrada,
  y validar fechas de pago como fechas ISO reales antes de guardar.

### BUG-08: pagos huérfanos después del borrado

- Causa: `delete_quote` elimina cotizaciones y `delete_project` limpia varias
  colecciones, pero ambas omiten `payments`.
- Evidencia: al borrar Q1 permanece PAY1; al borrar P1 también permanece PAY1.
  La vista global de pagos incluye esos registros aunque ya no encuentre sus
  documentos asociados.
- Corrección propuesta: definir una política de historial financiero. Según esa
  decisión, impedir el borrado con pagos, archivar documentos o desvincularlos
  conservando una referencia histórica explícita. No borrar pagos silenciosamente.

### BUG-09: cierre de proyecto aplicado de forma inconsistente

- Causa: el editor PDF de cotizaciones y `mobile_add_item` no comprueban
  `closed_at`. Las rutas de importación de cotizaciones/LDM sí exigen reabrir.
- Evidencia: con P1 cerrado, el editor PDF cambia el nombre de Q1 y el móvil crea
  un nuevo borrador al enviar un artículo.
- Corrección propuesta: centralizar qué operaciones permite el cierre y aplicar
  esa regla también a las rutas de escritura, con pruebas de cada flujo.

### BUG-10: totales diferentes para el mismo proyecto

- Causa: [dashboard](tracker/routes/projects.py#L36) descarta el borrador técnico
  móvil (`status=draft`), pero ignora `approval_status`. El detalle del proyecto
  suma solamente cotizaciones activas en `project_view.py`.
- Evidencia: activa de $100, borrador de $200 y obsoleta de $300 producen «Total
  cotizado» de $600 en el tablero y «Cotizado cliente» de $100 en el detalle.
- Corrección propuesta: compartir el criterio financiero o etiquetar claramente
  las cifras si se decide que representan conceptos distintos.

### BUG-11: nombre largo encimado en portada normal

- Causa: el nombre usa `multi_cell` y crece hacia abajo; el resumen sigue fijo en
  [221 mm](tracker/pdfs.py#L794). El cliente baja después del texto sin comprobar
  el espacio restante. No hace falta habilitar tamaños nuevos para reproducirlo.
- Evidencia: nombre de 731 caracteres a los 24 pt actuales termina a 281.84 mm,
  dentro y debajo del recuadro que empieza a 221 mm. Se renderizó `long-title.pdf`
  y se confirmó visualmente texto tapado y el cliente fuera del área útil.
- Corrección propuesta: medir la altura antes de dibujar y elegir una política de
  distribución para nombres largos. El futuro control de tamaño debe ajustar
  también interlineado y espacio disponible.

### BUG-12: coma decimal en tamaño de compra genera excepción

- Causa: [_catalog_form](tracker/routes/admin.py#L47) convierte `buy_unit_size`
  mediante `float` directamente, sin el manejo de errores ni la normalización de
  coma que sí existen para el precio.
- Evidencia: `POST /catalogo` con `buy_unit_size=2,5` provoca `ValueError` en modo
  de prueba; en el servidor normal se traduce en error 500 en vez de un mensaje
  de validación. Un cliente puede enviar este valor aunque un navegador limite
  el campo numérico.
- Corrección propuesta: validar y normalizar el tamaño de compra, incluyendo cero,
  negativos y valores no finitos, antes de construir el artículo.

### BUG-13: redirección externa después de iniciar sesión

- Causa: [login](tracker/routes/auth_routes.py#L31) usa el parámetro `next`
  directamente en `redirect` sin validar su destino.
- Evidencia: login válido con `next=https://example.invalid/audit` devuelve 302
  con esa URL externa en `Location`. No se visitó el destino externo.
- Corrección propuesta: aceptar rutas locales o destinos del mismo origen y usar
  el tablero como alternativa.

## Controles comprobados y límites del diagnóstico inicial

- Suite existente: **514 pruebas, OK, 2 omitidas**, antes del mapeo. Las dos
  omisiones corresponden a datos locales de bundles ausentes.
- Smoke de 23 rutas principales: HTTP 200 en proyectos, kanban, cotizaciones,
  pagos, catálogos, bundles, proveedores, equipo, fichas, plantillas, móvil, LDM y
  exportaciones PDF/Excel/CSV. Una respuesta 200 no prueba sus casos límite.
- Sesión real de cotizador. Las reproducciones HTTP aíslan la lógica de negocio
  con CSRF desactivado; las comprobaciones de navegador lo activan.
- Navegador: login, acceso al editor PDF, guardado del nombre y su reflejo en el
  editor principal, menú oculto solo en el editor PDF, botones de términos sin
  efecto y eliminación indebida de un proyecto sintético con CSRF activo.
- Sospecha descartada: desactivar un usuario bloquea su sesión ya existente y
  rechaza un nuevo login. `/usuarios` también aplica correctamente el rol admin.
- No se probaron credenciales, volúmenes ni integraciones de producción. La suite
  cubre importadores y cálculos con fixtures; este mapeo no es una certificación
  exhaustiva de todos los archivos de entrada o resoluciones de pantalla.
- Graphify conserva algunas rutas antiguas `Documents/ProjectTracker`; se
  contrastaron sus relaciones con los archivos del checkout actual.
- El alcance es toda la aplicación, por lo que no se activó un bloqueo de edición
  a un único módulo. No se aplicaron correcciones de producto en esta pasada.

## Correcciones pendientes

1. Acordar política de pagos e inmovilización de proyectos cerrados (BUG-08/09).
2. Unificar totales, resolver el límite de portada y completar validaciones
   (BUG-10 a BUG-13).

Cada corrección necesita una prueba que falle en la versión investigada, pase con
la solución y cubra el flujo original. El editor de tamaños de letra queda como
funcionalidad futura; BUG-11 debe resolverse antes de ampliarlo.
