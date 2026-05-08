# Roadmap exclusivo — Integracion LISP CSVs ↔ App

Este documento concentra el plan de trabajo para conectar las cuantificaciones
generadas desde AutoCAD/LISP con ProjectTracker mediante CSVs, catalogo,
cotizaciones, LDMs, bundles y comparaciones COT/LDM.

El objetivo no es solo importar filas: el flujo debe permitir que una misma
cuantificacion tecnica produzca conceptos comerciales para cotizacion y
materiales de compra para LDM, aunque los articulos no sean los mismos.

---

## Principios de la integracion

1. **Separar COT y LDM desde el origen.**
   - COT representa conceptos comerciales vendidos al cliente.
   - LDM representa materiales fisicos solicitados/cotizados por proveedor.
   - Un mismo tramo, salida o circuito puede generar filas diferentes en cada tabla.

2. **El catalogo es la fuente comun de nombres.**
   - El LISP debe exportar `description` con nombres exactos del catalogo cuando el articulo exista.
   - La app debe intentar vincular por `catalog_item_id` cuando pueda y por nombre normalizado como respaldo.

3. **La equivalencia vive en bundles y reglas.**
   - Un articulo COT puede expandirse a varios componentes LDM mediante bundles.
   - Una regla COT/LDM convierte unidades cuando compra y venta no usan la misma unidad.
   - Ejemplo: COT = metro lineal de tuberia; LDM = tubos por pieza, abrazaderas, pijas, soportes, coples, conectores.

4. **Los CSVs deben ser auditables.**
   - Deben incluir contratos simples y repetibles.
   - La app debe mostrar origen, fecha, proyecto, proveedor/tipo y diferencias detectadas.

5. **Las comparaciones oficiales viven en la app.**
   - LISP extrae hechos del dibujo: salidas, dispositivos, longitudes, atributos, layers y contexto.
   - ProjectTracker interpreta esos hechos con catalogo, bundles, reglas COT/LDM y tolerancias.
   - Cualquier comparativo generado en AutoCAD queda como diagnostico local, no como fuente oficial.

---

## Estado actual

### Ya disponible en ProjectTracker

- Importacion LDM desde CSV detectado en carpeta de proyecto.
- Exportacion CSV de LDM existente.
- Catalogo con articulos comerciales y tecnicos.
- Bundles versionados: articulo COT → componentes tecnicos esperados.
- Reglas de comparacion COT/LDM para convertir unidades.
- Vista de consistencia comercial y tecnica en detalle de proyecto.
- Sincronizacion parcial para completar faltantes tecnicos en una LDM existente.

### Ya disponible en `CedulaRecTables.lsp`

- Lectura de bloques tipo `CEDULAREC` y `SUBIRBAJAR`.
- Tabla/CSV LDM con cableado, tuberia y soporteria/accesorios.
- Exportacion ProjectTracker LDM con contrato `description,unit,qty`.
- Primera salida COT para tuberia por metro lineal.
- Tabla comparativa simple COT/LDM para tuberia como diagnostico local.
- Exportacion COT inicial con contrato `description,unit,qty,price`.
- Exportacion TAKEOFF/facts con contrato tecnico general para que la app interprete COT/LDM.

### Huecos principales

- La app ya tiene un primer flujo de importacion de CSV COT desde UI: carga archivo,
  parser, vista previa editable y guardado como cotizacion.
- Falta una matriz formal de mapeo bloque/atributo → concepto COT → bundle → materiales LDM.
- Falta leer bloques adicionales para salidas de iluminacion, contactos y HVAC.
- Faltan bundles reales completos para todos los conceptos comerciales recurrentes.
- Falta una validacion automatica de CSVs LISP antes de importarlos.

---

## Contratos CSV objetivo

### CSV LDM

Uso: materiales para proveedor.

Columnas minimas:

```csv
description,unit,qty
```

Columnas/metadatos opcionales:

```csv
#proyecto_clave,CLAVE,,
#proveedor,NOMBRE_PROVEEDOR,,
#fecha,YYYY-MM-DD,,
#source,lisp_cedularec,,
#drawing,DWGNAME,,
```

Criterios:

- No incluir `precio_cot` ni `total_cot`.
- La app captura o importa despues el costo proveedor.
- Cada fila debe intentar coincidir con catalogo.

### CSV COT

Uso: conceptos comerciales para cotizacion al cliente.

Columnas minimas:

```csv
description,unit,qty,price
```

Metadatos sugeridos:

```csv
#proyecto_clave,CLAVE,,,
#quote_type,General,,,
#fecha,YYYY-MM-DD,,,
#source,lisp_cedularec,,,
#drawing,DWGNAME,,,
```

Criterios:

- `price` puede salir en `0.00` para captura manual.
- La app calcula `total`, subtotal, IVA y total final.
- La app asigna `quote_number`, cliente, proyecto y fecha final.

### CSV TAKEOFF / facts

Uso: hechos tecnicos observados en AutoCAD para que la app genere o valide COT/LDM
con bundles, reglas y tolerancias.

Columnas:

```csv
record_type,source_id,family,measurement_kind,description_hint,unit,qty,run_length_m,block_name,block_class,layer,cedula,conduit_type,diameter,cable_count,phase,ground,support_group,drawing
```

Metadatos sugeridos:

```csv
#csv_type,takeoff
#proyecto_clave,CLAVE
#version,N
#consecutivo,N
#fecha,YYYYMMDD
#source,lisp_cedularec
#drawing,DWGNAME
```

Criterios:

- No contiene comparaciones COT/LDM.
- No contiene reglas comerciales, redondeos de compra ni tolerancias.
- `source_id` debe permitir rastrear el origen CAD; en CEDULAREC se usa `BLOCKCLASS:HANDLE:fact`.
- `family` inicial: `conduit`, `wire`; despues `device`, `outlet`, `equipment` cuando se lean bloques no-CEDULAREC.
- `measurement_kind` inicial: `length`, `phase_length`, `ground_length`; despues `count`, `device_count`, etc.

### CSV Comparativo Simple

Uso: diagnostico local temporal. No es fuente oficial de comparacion.

Columnas sugeridas:

```csv
cot_description,cot_unit,cot_qty,ldm_description,ldm_unit,ldm_qty,factor,delta
```

Criterios:

- No se importa como entidad final.
- No debe duplicar reglas/bundles de ProjectTracker.
- Sirve solo para revisar visualmente en AutoCAD durante transicion.

---

## Roadmap por fases

### Fase 0 — Congelar contratos y nomenclatura

Objetivo: dejar cerrada la base de intercambio LISP/App.

- [x] Actualizar `REFERENCIA_ESTRUCTURAS_CSV.txt` con contratos LDM, COT, TAKEOFF y comparativo diagnostico.
- [ ] Definir convencion de nombres de archivos:
  - LDM: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-{YYYYMMDD}.csv`
  - COT: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-COT-{YYYYMMDD}.csv`
  - TAKEOFF: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-TAKEOFF-{YYYYMMDD}.csv`
  - Comparativo diagnostico: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-CMP-{YYYYMMDD}.csv`
- [ ] Definir metadatos aceptados por tipo de CSV.
- [ ] Documentar columnas obligatorias, opcionales y tolerancias.
- [ ] Definir como se resuelve proyecto cuando el CSV solo trae `proyecto_clave`.

Criterio de aceptacion:

- Un CSV generado por LISP puede identificarse como LDM, COT o comparativo sin depender del nombre del archivo solamente.

---

### Fase 1 — Importador COT CSV en la app

Objetivo: que ProjectTracker pueda crear una cotizacion desde CSV LISP.

- [x] Crear parser `tracker/quote_csv_import.py`.
- [x] Aceptar `description,unit,qty,price`.
- [x] Aceptar encabezados en ingles y variantes razonables en espanol.
- [x] Aceptar `price` faltante y tratarlo como `0.00`.
- [x] Leer metadatos `#proyecto_clave`, `#quote_type`, `#fecha`, `#source`, `#drawing`.
- [x] Vincular filas al catalogo por nombre normalizado.
- [x] Crear cotizacion General o Extraordinaria segun metadata/UI.
- [x] Mostrar vista previa antes de guardar:
  - filas vinculadas al catalogo,
  - filas sin catalogo,
  - totales,
  - advertencias de duplicados.
- [x] Agregar pruebas unitarias de parser y ruta.

Criterio de aceptacion:

- Un CSV COT exportado por `CEDULARECEXPORTCOT` crea una cotizacion editable y visible en PDF/Excel.

---

### Fase 2 — LISP: salida COT estable por tuberia

Objetivo: madurar la primera familia comercial ya iniciada.

- [ ] Validar en AutoCAD `CEDULARECEXPORTCOT` con planos reales.
- [ ] Validar `CEDULARECEXPORTTAKEOFF` con varios diametros y tipos de tuberia.
- [ ] Mantener `CEDULARECCOMPARATABLE` solo como diagnostico local si aporta valor operativo.
- [ ] Confirmar nombres comerciales contra catalogo:
  - `Metro Lineal de Tuberia Conduit ...`
  - variantes PD, PG, PVC, PAD, flexible galvanizada, licuatite.
- [ ] Definir si la COT tuberia debe incluir solo metro lineal o tambien partidas de instalacion adicionales.
- [ ] Revisar redondeo: COT conserva metros reales; LDM compra piezas/tramos.

Criterio de aceptacion:

- Para un conjunto de cedulas, TAKEOFF describe los hechos tecnicos suficientes para que la app explique COT, LDM esperada y diferencias.

---

### Fase 3 — Matriz de bloques y conceptos comerciales

Objetivo: decidir como se leeran salidas de iluminacion, contactos y HVAC.

- [ ] Inventariar bloques reales del DWG:
  - nombre efectivo,
  - atributos,
  - layer,
  - familia,
  - cantidad esperada.
- [ ] Crear matriz `bloque/atributos/layer → concepto COT`.
- [ ] Definir familias iniciales:
  - Salida Electrica para Luminaria.
  - Salida Electrica para Contacto.
  - Salida Electrica para Equipo de HVAC.
  - Contacto Duplex / Decora / GFCI / USB cuando aplique.
  - Desarrollo de Circuito Electrico para Iluminacion/Contactos/HVAC.
- [ ] Definir reglas por layer:
  - `Piso`,
  - `Plafon`,
  - `Muro`,
  - otras convenciones existentes.
- [ ] Definir si el conteo sale de bloques, atributos, longitud o combinacion.

Criterio de aceptacion:

- Cada bloque nuevo queda clasificado como COT, LDM, ambos o ignorado, con una regla explicita.

---

### Fase 4 — LISP: lector extensible de bloques no-CEDULAREC

Objetivo: ampliar la lectura sin romper el analisis actual de cedulas.

- [ ] Crear colector separado para bloques de salidas/dispositivos.
- [ ] Mantener el colector CEDULAREC actual como fuente de tuberia/cable/soporteria.
- [ ] Agregar configuracion de nombres de bloque por familia.
- [ ] Agregar lectura robusta de atributos por familia.
- [ ] Agregar diagnositico tipo `TESTBLOQUECOT` para inspeccionar bloque seleccionado.
- [ ] Evitar que bloques desconocidos generen filas silenciosas.
- [ ] Mantener rendimiento: prefiltrar por INSERT, nombre y atributos antes de usar VLA.

Criterio de aceptacion:

- El usuario puede seleccionar un area del plano y obtener conteos COT de salidas sin afectar LDM existente.

---

### Fase 5 — Bundles reales por familias comerciales

Objetivo: que la app pueda explicar tecnicamente cada partida COT.

- [ ] Crear bundles para metro lineal de tuberia por tipo/diametro.
- [ ] Crear bundles para salida de luminaria.
- [ ] Crear bundles para salida de contacto.
- [ ] Crear bundles para salida HVAC.
- [ ] Crear bundles para desarrollo de circuito sin tuberia, si aplica.
- [ ] Validar componentes:
  - tuberia,
  - cable,
  - conectores,
  - monitores,
  - coples,
  - codos,
  - abrazaderas,
  - pijas,
  - soportes.
- [ ] Versionar bundles cuando cambie el criterio de cuantificacion.
- [ ] Agregar notas por bundle que expliquen supuestos tecnicos.

Criterio de aceptacion:

- Una COT importada desde LISP genera materiales esperados por bundle y los compara contra la LDM del mismo dibujo.

---

### Fase 6 — Reglas COT/LDM y tolerancias

Objetivo: resolver diferencias de unidad y compra.

- [ ] Regla metro lineal COT ↔ pieza/tramo LDM para tuberia rigida.
- [ ] Regla metro lineal COT ↔ rollo/tramo LDM para flexible/PAD.
- [ ] Reglas para cable por metro, con redondeo por familia.
- [ ] Reglas para soporteria cuando se compra por pieza, tramo o paquete.
- [ ] Tolerancias por familia:
  - tuberia,
  - cableado,
  - accesorios,
  - soporteria.
- [ ] Decidir donde se redondea:
  - LISP para compra practica,
  - app para comparacion tecnica,
  - ambos, solo si queda documentado.

Criterio de aceptacion:

- La vista de consistencia tecnica diferencia correctamente faltante real, excedente por compra minima y diferencia aceptable.

---

### Fase 7 — UI de importacion y revision asistida

Objetivo: que la operacion sea usable dentro del proyecto.

- [ ] Detectar CSVs COT y LDM en carpeta Drive del proyecto.
- [ ] Mostrar acciones separadas:
  - Importar COT desde CSV.
  - Importar LDM desde CSV.
  - Ver comparativo CSV.
- [ ] Vista previa antes de importar:
  - tipo de CSV detectado,
  - metadatos,
  - filas,
  - catalogo vinculado,
  - advertencias.
- [ ] Evitar duplicados por `source`, `drawing`, `fecha`, `consecutivo`.
- [ ] Permitir reimportar como nueva version, no sobrescribir sin confirmacion.
- [ ] Mostrar resumen despues de importar.

Criterio de aceptacion:

- Desde el detalle de proyecto se puede pasar de CSV detectado a COT/LDM creada sin abrir formularios manuales fila por fila.

---

### Fase 8 — Comparacion operativa COT ↔ LDM

Objetivo: convertir las comparaciones en una herramienta de revision diaria.

- [ ] Mostrar comparacion comercial:
  - COT vendida vs LDM costeada.
- [ ] Mostrar comparacion tecnica:
  - COT expandida por bundles vs LDM real.
- [ ] Separar diferencias por causa:
  - sin bundle,
  - sin regla,
  - sin catalogo,
  - faltante,
  - excedente,
  - tolerancia aceptada,
  - compra minima.
- [ ] Agregar accion sugerida por fila.
- [ ] Permitir ignorar articulos no atribuibles al cliente por alcance.
- [ ] Exportar reporte de comparacion si se requiere para revision interna.

Criterio de aceptacion:

- Un proyecto importado desde LISP puede revisarse y corregirse desde una sola vista de consistencia.

---

### Fase 9 — Sincronizacion asistida

Objetivo: ayudar a corregir LDMs sin destruir captura existente.

- [ ] Completar faltantes desde bundles al crear una LDM nueva.
- [ ] Completar faltantes en una LDM existente por proveedor/disciplina.
- [ ] Nunca sobrescribir precios proveedor ya capturados.
- [ ] Mostrar diff antes de agregar filas.
- [ ] Permitir seleccionar subset de faltantes.
- [ ] Registrar origen de filas agregadas automaticamente.

Criterio de aceptacion:

- La app puede proponer materiales faltantes derivados de COT y el usuario decide que agregar.

---

### Fase 10 — Validacion, pruebas y control de regresiones

Objetivo: cerrar el circuito con confianza.

- [ ] Fixtures CSV LDM reales.
- [ ] Fixtures CSV COT reales.
- [ ] Pruebas para parsers COT/LDM.
- [ ] Pruebas para vinculacion con catalogo.
- [ ] Pruebas para bundles y reglas de comparacion.
- [ ] Pruebas para duplicados y reimportaciones.
- [ ] Checklist manual AutoCAD:
  - cargar LISP,
  - seleccionar bloques,
  - generar LDM,
  - generar COT,
  - generar comparativo,
  - importar en app,
  - revisar consistencia.

Criterio de aceptacion:

- Cada cambio en LISP o app puede validarse con un set minimo de CSVs y pruebas automatizadas.

---

## Orden recomendado de ejecucion

1. Cerrar Fase 0 con contratos definitivos.
2. Implementar Fase 1 para importar COT CSV en la app.
3. Probar Fase 2 en AutoCAD con tuberia real.
4. Levantar matriz de bloques reales para Fase 3.
5. Implementar lector extensible de salidas en Fase 4.
6. Crear bundles reales de Fase 5 y reglas de Fase 6.
7. Pulir UI de importacion/revision en Fases 7 y 8.
8. Automatizar sincronizacion asistida en Fase 9.
9. Consolidar pruebas y fixtures en Fase 10.

---

## Primer entregable recomendado

**Importador COT CSV en ProjectTracker.**

Razon: el LISP ya puede emitir un primer CSV COT para tuberia, pero la app aun
necesita un flujo claro para convertir ese CSV en una cotizacion real. Sin ese
paso, no hay forma practica de validar bundles y comparaciones contra la COT
activa del proyecto.

Archivos probables:

- `tracker/quote_csv_import.py`
- `tracker/routes/quotes.py`
- `tracker/project_view.py`
- `templates/project_detail.html`
- `tests/test_quote_csv_import.py`
- `tests/test_quote_csv_import_route.py`

Comandos de verificacion esperados:

```bash
python -m compileall app.py tracker tests
python -m unittest discover -s tests
```

---

## Riesgos y decisiones pendientes

- Definir si los precios COT vienen siempre en cero desde LISP o si habra una tabla local de precios.
- Definir si los bundles se crean manualmente en app o si parte de la matriz LISP puede proponerlos.
- Definir como tratar excedentes por compra minima para que no parezcan errores.
- Definir si el comparativo CSV queda como herramienta temporal o se importa como evidencia.
- Definir si cada familia electrica tendra proveedor/disciplina por default.
- Confirmar en AutoCAD los nombres efectivos reales de bloques de iluminacion, contactos y HVAC.

---

## Glosario operativo

- **COT:** Cotizacion al cliente; conceptos comerciales, precio de venta e IVA.
- **LDM:** Lista de materiales para proveedor; articulos fisicos y costo proveedor.
- **Bundle:** Receta tecnica que expande un articulo COT a materiales LDM esperados.
- **Regla COT/LDM:** Conversion de unidad/cantidad entre venta y compra.
- **Comparativo simple:** Tabla temporal para validar equivalencias antes de configurar bundles completos.
- **Catalogo:** Fuente comun de articulos; debe mantener nombres exactos y unidades consistentes.
