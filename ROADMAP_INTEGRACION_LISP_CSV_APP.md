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
<!-- Última revisión: 2026-05-23 — verificado contra código fuente -->

### Ya disponible en ProjectTracker

- **Importacion LDM desde CSV** — ruta `GET/POST /projects/<id>/ldm/import/<filename>` operativa.
  - Detecta CSVs en carpeta Drive del proyecto con patrón `{CLAVE}-v{VER}-i{CONSEC}-{YYYYMMDD}.csv` (case-insensitive).
  - Llama a `parse_ldm_csv` con catálogo; muestra preview editable con proveedor/fecha pre-poblados desde metadatos `#`.
  - Detecta reimportaciones duplicadas por nombre de archivo.
- **Importacion COT desde CSV** — ruta `POST /projects/<id>/quote/import` operativa.
  - Acepta upload directo desde browser (multipart); usa `tempfile` y lo borra después de parsear.
  - Llama a `parse_quote_csv`; muestra preview con campo `price` editable (acepta `price` vacío sin error).
  - Advierte partidas duplicadas y sin catálogo sin bloquear la importación.
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
- Separador decimal garantizado con punto: `omm-repl-coma-punto` en Utils.lsp normaliza
  cualquier coma decimal antes de escribir al CSV (la app también tiene su propio `replace(",",".")`
  como segunda capa de protección).
- **COT simbología completa** (`crt-cot-sym-collect-from-ss`): genera conceptos comerciales con
  descripciones fijas del catálogo. SMB01/VAR/PZ → `Salida Eléctrica para Luminaria` + `Instalación de Luminaria`;
  SMB02 TAG∈A → `Salida Eléctrica para Apagador`, TAG∈C → `Salida Eléctrica para Contacto`;
  SMB03 LED → `Salida Eléctrica para Luminaria` + `Instalación de Metro Lineal de Tira LED` (ML);
  SMB03 no-LED → igual que SMB01. Bloques CONTACTO/APAGADOR dedicados mapeados a la misma clave fija.
- **Nombres de cable COT** idénticos al catálogo LDM (unidad `m`); auto-vinculación en importación.
- **Catálogo** (494 artículos): cables desnudo 14–6 AWG, tubería conduit todos los tipos/diámetros,
  accesorios PAD/Flexible 35/41/63 mm, corrección de unidad Metálico Flexible 35mm.
- `CEDULARECEXPORTTAKEOFF` queda fuera del flujo activo: el CSV TAKEOFF fue eliminado y no debe usarse como criterio de aceptación.

### Huecos principales

- Falta una matriz formal de mapeo bloque/atributo → concepto COT → bundle → materiales LDM.
- Falta leer bloques adicionales para salidas de iluminacion, contactos y HVAC.
- Faltan bundles reales completos para todos los conceptos comerciales recurrentes.
- Falta una validacion automatica de CSVs LISP antes de importarlos.
- El LISP aun no incluye metadatos `#proyecto_clave`, `#proveedor`, etc. en el CSV LDM;
  agregarlos permitiria que la app pre-pueble proyecto/proveedor en el preview.

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

### CSV TAKEOFF / facts — retirado

Estado: retirado del flujo activo. El CSV TAKEOFF fue eliminado; no debe usarse como
contrato vigente ni como requisito para cerrar la integración LISP/App.

Criterio actual:

- La explicación COT → LDM vive en ProjectTracker mediante catálogo, bundles y reglas COT/LDM.
- AutoCAD/LISP sólo debe emitir COT/LDM y, si aporta valor operativo, comparativos diagnósticos temporales.

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

- [x] Actualizar `REFERENCIA_ESTRUCTURAS_CSV.txt` con contratos LDM, COT y comparativo diagnostico.
- [x] Definir convencion de nombres de archivos (compatible con detección automática de la app, case-insensitive):
  - LDM: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-{YYYYMMDD}.csv`
  - COT: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-COT-{YYYYMMDD}.csv`
  - Comparativo diagnostico: `{CLAVE}-V{VERSION}-I{CONSECUTIVO}-CMP-{YYYYMMDD}.csv`
- [x] Definir metadatos aceptados por tipo de CSV (ver REFERENCIA_ESTRUCTURAS_CSV.txt).
- [x] Documentar columnas obligatorias, opcionales y tolerancias.
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

### Fase 2 — LISP: salida COT estable por tuberia y simbología

Objetivo: madurar las familias comerciales de tubería, cable y simbología.

- [ ] Validar en AutoCAD `CEDULARECEXPORTCOT` con planos reales.
- [x] Retirar `CEDULARECEXPORTTAKEOFF` del flujo activo; el CSV fue eliminado y no sirve como contrato vigente. ✅ 2026-05-23
- [ ] Mantener `CEDULARECCOMPARATABLE` solo como diagnostico local si aporta valor operativo.
- [x] Confirmar nombres comerciales de tubería contra catalogo (todas las variantes PD, PG, PVC, PAD, flexible galvanizada, licuatite). ✅ 2026-05-23
- [x] Confirmar nombres de cable COT contra catálogo; `crt-cable-commercial-description` delegada a `crt-cable-description`, unidad `m`. ✅ 2026-05-23
- [x] Catálogo actualizado con tubería, accesorios, desnudo 14–6 AWG (494 artículos). ✅ 2026-05-23
- [x] COT simbología (`crt-cot-sym-collect-from-ss`) con descripciones fijas del catálogo para luminarias, apagadores, contactos y tiras LED. ✅ 2026-05-23
- [x] Fixtures tests tubería LDM/COT (29 tests, 153/153 total pasan). ✅ 2026-05-23
- [ ] Revisar redondeo operativo cuando existan bundles/reglas reales: COT conserva metros reales; LDM compra piezas/tramos/rollos/paquetes.
- [x] Definir alcance COT de salidas: incluye metros de cable, tubería y accesorios para LDM; la generación correcta queda pendiente de bundles. ✅ 2026-05-23

Criterio de aceptacion:

- Para un conjunto de cedulas, `CEDULARECEXPORTCOT` genera COT importable y ProjectTracker explica COT → LDM esperada mediante bundles y reglas.

---

### Fase 3 — Matriz de bloques y conceptos comerciales

Objetivo: decidir como se leeran salidas de iluminacion, contactos y HVAC.

- [x] Confirmar nombres ya soportados por `CEDULARECEXPORTCOT`: SMB01, SMB02, SMB03, VAR, PZ, CONTACTO y APAGADOR. ✅ 2026-05-23
- [ ] Inventariar bloques reales pendientes del DWG:
  - nombre efectivo,
  - atributos,
  - layer,
  - familia,
  - cantidad esperada.
- [ ] Crear matriz `bloque/atributos/layer → concepto COT`.
- [ ] Definir familias iniciales:
  - Especiales de salidas/dispositivos.
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
- [x] Crear bundles iniciales para desarrollo de circuito sin tubería: iluminación, contactos y HVAC, con componentes tomados de la descripción del catálogo. ✅ 2026-05-23
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

1. Mantener pendiente la validación de `CEDULARECEXPORTCOT` con planos reales.
2. Cerrar matriz pendiente sólo para bloques especiales y HVAC.
3. Crear bundles reales de salidas y tubería/accesorios.
4. Ajustar reglas COT/LDM y redondeos con esos bundles reales.
5. Pulir UI de importacion/revision en Fases 7 y 8.
6. Automatizar sincronizacion asistida en Fase 9.
7. Consolidar pruebas y fixtures en Fase 10.

---

## Primer entregable recomendado

~~**Importador COT CSV en ProjectTracker.**~~ ✅ **Completado** (2026-05-23)

Las rutas de importación LDM (`/projects/<id>/ldm/import/<filename>`) y COT
(`/projects/<id>/quote/import`) están implementadas y operativas. Los parsers
`csv_import.py` y `quote_csv_import.py` están integrados y cubiertos con tests.

**Siguiente entregable recomendado: completar bundles reales de salidas.**

La validación de AutoCAD queda pendiente. El siguiente avance dentro de ProjectTracker
es definir los componentes LDM de las COT de salidas: metros de cable, tubería y
accesorios incluidos por salida. Después se ajusta el redondeo operativo de tubería
y accesorios con reglas COT/LDM reales.

Archivos involucrados:

- `data/bundles.json` — bundles activos por artículo COT.
- `data/comparison_rules.json` — reglas de conversión y redondeo cuando la LDM compre en tramo/rollo/paquete.
- `tests/test_bundles.py` y `tests/test_ldm_sync.py` — regresión de expansión COT → LDM.

Comandos de verificacion:

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
- Confirmar en AutoCAD los nombres efectivos reales de bloques especiales y HVAC.

---

## Glosario operativo

- **COT:** Cotizacion al cliente; conceptos comerciales, precio de venta e IVA.
- **LDM:** Lista de materiales para proveedor; articulos fisicos y costo proveedor.
- **Bundle:** Receta tecnica que expande un articulo COT a materiales LDM esperados.
- **Regla COT/LDM:** Conversion de unidad/cantidad entre venta y compra.
- **Comparativo simple:** Tabla temporal para validar equivalencias antes de configurar bundles completos.
- **Catalogo:** Fuente comun de articulos; debe mantener nombres exactos y unidades consistentes.
