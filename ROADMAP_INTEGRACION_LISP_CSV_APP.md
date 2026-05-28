# Roadmap exclusivo — Integracion LISP CSVs ↔ App

Este documento concentra el plan de trabajo para conectar las cuantificaciones
generadas desde AutoCAD/LISP con ProjectTracker mediante CSVs, catalogo,
cotizaciones, LDMs, bundles y revision COT/LDM.

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

3. **La equivalencia vive en bundles directos.**
   - Un articulo COT puede expandirse a varios componentes LDM mediante bundles.
   - Si compra y venta no usan la misma unidad, la conversion debe quedar como campo del componente de bundle, no como tabla separada de reglas.
   - Ejemplo: COT = metro lineal de tuberia; LDM = tubos por pieza, abrazaderas, pijas, soportes, coples, conectores.

4. **Los CSVs deben ser auditables.**
   - Deben incluir contratos simples y repetibles.
   - La app debe mostrar origen, fecha, proyecto, proveedor/tipo y diferencias detectadas.

5. **Las comparaciones oficiales viven en la app.**
   - LISP extrae hechos del dibujo: salidas, dispositivos, longitudes, atributos, layers y contexto.
   - ProjectTracker interpreta esos hechos con catalogo, bundles directos y tolerancias simples cuando existan.
   - Cualquier comparativo generado en AutoCAD queda como diagnostico local, no como fuente oficial.

---

## Estado actual
<!-- Última revisión: 2026-05-28 v30.0 — verificado contra código fuente -->

### Ya disponible en ProjectTracker

- **Importacion LDM desde CSV** — ruta `GET/POST /projects/<id>/ldm/import/<filename>` operativa.
  - Detecta CSVs en carpeta Drive del proyecto con patrón `{CLAVE}-v{VER}-i{CONSEC}-{YYYYMMDD}.csv` (case-insensitive).
  - Llama a `parse_ldm_csv` con catálogo; muestra preview editable con proveedor/fecha pre-poblados desde metadatos `#`.
  - Detecta reimportaciones duplicadas por nombre de archivo.
- **Importacion COT desde CSV** — ruta `POST /projects/<id>/quote/import` (upload manual) y `GET /projects/<id>/quote/import-drive/<filename>` (desde Drive) operativas.
  - CSV COT detectados automáticamente en carpeta Drive con patrón `{CLAVE}-v*-i*-COT-*.csv`.
  - Dropdown en tab Cotización muestra estado por archivo (pendiente/importado/desactualizado).
  - Acepta upload directo desde browser (multipart); usa `tempfile` y lo borra después de parsear.
  - Llama a `parse_quote_csv`; muestra preview con campo `price` editable (acepta `price` vacío sin error).
  - Advierte partidas duplicadas y sin catálogo sin bloquear la importación.
- **Importacion PDF de proveedor a LDM** — rutas `POST /projects/<id>/ldm/import-pdf`, `GET /projects/<id>/ldm/import-pdf/map` y `POST /projects/<id>/ldm/import-pdf/create` operativas.
  - Usa extractor PDF con `pdfplumber`; Procables detecta partidas, proveedor, fecha y numero de cotizacion cuando el formato coincide.
  - Guarda la extraccion temporalmente del lado servidor y usa token en sesion para evitar cookies grandes.
- Exportacion CSV de LDM existente.
- Catalogo con articulos comerciales y tecnicos.
- Bundles versionados: articulo COT → componentes tecnicos esperados.
- Reglas COT/LDM retiradas del flujo operativo; los datos historicos pueden permanecer inactivos.
- Vista de consistencia visual simple COT vs LDM en detalle de proyecto.
- Sincronizacion parcial para completar faltantes tecnicos en una LDM existente usando bundles directos.

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
- Falta definir si conversiones/redondeos se agregan como campos propios del componente de bundle.
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

- La explicación COT → LDM vive en ProjectTracker mediante catálogo y bundles directos.
- AutoCAD/LISP sólo debe emitir COT/LDM y, si aporta valor operativo, comparativos diagnósticos temporales.

### CSV Comparativo Simple

Uso: diagnostico local temporal. No es fuente oficial de comparacion.

Columnas sugeridas:

```csv
cot_description,cot_unit,cot_qty,ldm_description,ldm_unit,ldm_qty,factor,delta
```

Criterios:

- No se importa como entidad final.
- No debe duplicar bundles ni criterios de expansion de ProjectTracker.
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
- [ ] Revisar redondeo operativo cuando existan bundles directos reales: COT conserva metros reales; LDM compra piezas/tramos/rollos/paquetes.
- [x] Definir alcance COT de salidas: incluye metros de cable, tubería y accesorios para LDM; la generación correcta queda pendiente de bundles. ✅ 2026-05-23

Criterio de aceptacion:

- Para un conjunto de cedulas, `CEDULARECEXPORTCOT` genera COT importable y ProjectTracker explica COT → LDM esperada mediante bundles directos.

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

### Fase 6 — Conversiones de bundle y tolerancias

Objetivo: resolver diferencias de unidad y compra.

- [ ] Campos de conversion metro lineal COT ↔ pieza/tramo LDM para tuberia rigida dentro del componente de bundle.
- [ ] Campos de conversion metro lineal COT ↔ rollo/tramo LDM para flexible/PAD dentro del componente de bundle.
- [ ] Redondeo de cable por metro, por familia, como atributo propio del componente.
- [ ] Redondeo de soporteria cuando se compra por pieza, tramo o paquete.
- [ ] Tolerancias por familia:
  - tuberia,
  - cableado,
  - accesorios,
  - soporteria.
- [ ] Decidir donde se redondea:
  - LISP para compra practica,
  - app para sincronizacion y revision visual,
  - ambos, solo si queda documentado.

Criterio de aceptacion:

- La sincronizacion y la revision visual diferencian faltante real, excedente por compra minima y diferencia aceptable sin reactivar una tabla separada de reglas.

---

### Fase 7 — UI de importacion y revision asistida

Objetivo: que la operacion sea usable dentro del proyecto.

- [x] Detectar CSVs COT (`{CLAVE}-v*-i*-COT-*.csv`) en carpeta Drive del proyecto con estado (pendiente/importado/desactualizado). ✅ 2026-05-28
- [x] Mostrar acciones separadas en UI: dropdown "Importar CSV Drive" en tab Cotización + dropdown "Importar CSV" en tab Materiales. ✅ 2026-05-28
- [x] Importar COT desde Drive sin subir archivo (ruta directa). ✅ 2026-05-28
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

### Fase 8 — Revision visual COT ↔ LDM

Objetivo: mantener una revision diaria entendible sin reactivar diagnosticos tecnicos complejos.

- [x] Mostrar comparacion comercial:
  - COT vendida vs LDM costeada.
- [x] Mostrar cobertura basica:
  - cotizacion base activa,
  - extras activas,
  - LDMs consideradas,
  - renglones sin catalogo,
  - margen absoluto y porcentaje.
- [x] Agregar avisos simples cuando falte cotizacion base, LDM o catalogo.
- [x] Exportar resumen visual si se requiere para revision interna. Resuelto como impresion del resumen visual desde navegador.

Criterio de aceptacion:

- Un proyecto importado desde LISP puede revisarse desde una sola vista simple de COT vs LDM.

Estado: completado en ProjectTracker el 2026-05-28. La vista muestra base financiera, cobertura de catalogo, cotizaciones/LDM consideradas y avisos informativos sin reactivar comparacion tecnica por articulo.

---

### Fase 9 — Sincronizacion asistida

Objetivo: ayudar a corregir LDMs sin destruir captura existente.

- [x] Proponer faltantes desde bundles al crear una LDM nueva. ✅ 2026-05-28
- [ ] Proponer faltantes en una LDM existente por proveedor/disciplina.
- [x] Nunca sobrescribir precios proveedor ya capturados en la propuesta inicial; las filas sugeridas se precargan como renglones nuevos. ✅ 2026-05-28
- [ ] Mostrar diff antes de agregar filas.
- [ ] Permitir seleccionar subset de faltantes.
- [x] Registrar origen de filas agregadas automaticamente (`origen` y metadatos `sync_expected_*`). ✅ 2026-05-28

Estado: parcial. Ya existe el flujo de LDM nueva con sugerencias desde bundles directos; falta convertirlo en asistente para LDM existente con diff, selección parcial y agrupación por proveedor/disciplina.

Criterio de aceptacion:

- La app puede proponer materiales faltantes derivados de COT y el usuario decide que agregar.

---

### Fase 10 — Validacion, pruebas y control de regresiones

Objetivo: cerrar el circuito con confianza.

- [ ] Fixtures CSV LDM reales.
- [ ] Fixtures CSV COT reales.
- [x] Pruebas para parsers COT/LDM.
- [x] Pruebas para vinculacion con catalogo.
- [x] Pruebas para bundles directos y resumen visual COT/LDM.
- [ ] Pruebas para conversiones/redondeos de componente cuando existan esos campos propios de bundle.
- [ ] Pruebas para duplicados y reimportaciones.
- [ ] Checklist manual AutoCAD:
  - cargar LISP,
  - seleccionar bloques,
  - generar LDM,
  - generar COT,
  - importar en app,
  - revisar resumen visual COT vs LDM,
  - revisar sugerencias desde bundles.

Criterio de aceptacion:

- Cada cambio en LISP o app puede validarse con un set minimo de CSVs y pruebas automatizadas.

---

## Orden recomendado de ejecucion

1. Mantener pendiente la validación de `CEDULARECEXPORTCOT` con planos reales.
2. Cerrar matriz pendiente sólo para bloques especiales y HVAC.
3. Crear bundles reales de salidas y tubería/accesorios.
4. Ajustar componentes de bundle, conversiones y redondeos con esos bundles reales.
5. Pulir UI de importacion en Fase 7.
6. Completar sincronizacion asistida en Fase 9 con diff, selección parcial y agrupación por proveedor/disciplina.
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
y accesorios con campos de conversion/redondeo en componentes de bundle si hacen falta.

Archivos involucrados:

- `data/bundles.json` — bundles activos por artículo COT.
- `data/comparison_rules.json` — histórico inactivo; no debe usarse para nuevos flujos.
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
