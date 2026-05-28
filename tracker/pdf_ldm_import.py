"""Extracción de ítems desde PDFs de cotización de proveedores.

Estrategia en cascada:
1. Detección de formato conocido (Procables) → extractor por coordenadas de columna.
2. Tablas estructuradas de pdfplumber → extractor genérico de tablas.
3. Heurística de texto línea por línea → fallback general.

El resultado es una lista de dicts con los campos que se pudieron leer;
el mapeo al catálogo lo hace el usuario en la UI.
"""

from __future__ import annotations

import re
from typing import Any

# ── Helpers numéricos ─────────────────────────────────────────────────────────

def _to_float(text: str) -> float | None:
    if not text:
        return None
    t = str(text).strip().lstrip("$").strip()
    if re.search(r"\d\.\d{3},", t):   # formato europeo: 1.234,56
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", "")         # formato americano: 1,234.56
    try:
        return float(t)
    except ValueError:
        return None


def _clean(text: str) -> str:
    return " ".join(str(text or "").split())


# ── Extractor Procables (por coordenadas de columna) ─────────────────────────
#
# Formato Procables:
#   Encabezado: CANT. | DESCRIPCION | MARCA/MODELO | U.M. | PRECIOU. | TOTAL
#   Ítems:      cada fila tiene las palabras distribuidas en franjas x fijas.
#   Los ítems están ENTRE la fila de encabezado de columnas y la línea de SUB-TOTAL.

_PROCABLES_SIGNALS = {"PROCABLES", "PROCABLESDEMEXICO", "PROCABLES DE MEXICO"}


def _is_procables(page) -> bool:
    words = page.extract_words(x_tolerance=4, y_tolerance=4)
    for w in words[:20]:           # solo header del PDF
        t = w["text"].upper().replace(" ", "")
        if any(sig in t for sig in _PROCABLES_SIGNALS):
            return True
    return False


def _extract_procables(pdf) -> list[dict]:
    """Extrae ítems de cotización Procables usando franjas de columna por coordenada x."""
    items: list[dict] = []

    # Rangos de columna (x0) calibrados para el formato Procables (puntos PDF ~595 ancho).
    # Tolerancia amplia para cubrir variaciones de fuente/margen entre sucursales.
    COL_CANT  = (40,  84)    # cantidad
    COL_DESC  = (85,  294)   # descripción del material
    COL_MARCA = (294, 396)   # marca/modelo
    COL_UM    = (396, 458)   # unidad de medida
    COL_PRICE = (458, 529)   # precio unitario
    COL_TOTAL = (529, 600)   # total

    def in_col(x0, x1, col):
        cx0, cx1 = col
        # La palabra cae en la columna si su centro está dentro del rango
        cx = (x0 + x1) / 2
        return cx0 <= cx <= cx1

    for page in pdf.pages:
        words = page.extract_words(x_tolerance=3, y_tolerance=3)
        if not words:
            continue

        # Encontrar la fila del encabezado (CANT./DESCRIPCION) y la de totales (SUB-TOTAL)
        header_top = None
        subtotal_top = None
        for w in words:
            txt_up = w["text"].upper()
            if txt_up in ("CANT.", "CANT") and header_top is None:
                header_top = w["top"]
            if "SUB-TOTAL" in txt_up or "SUBTOTAL" in txt_up:
                subtotal_top = w["top"]

        if header_top is None:
            continue   # página sin tabla de ítems

        # Agrupar palabras por fila (top con tolerancia ±4 pt)
        ROW_TOL = 5
        rows_map: dict[int, list[dict]] = {}
        for w in words:
            t = w["top"]
            # Solo ítems: debajo del encabezado y encima de totales
            if t <= header_top + ROW_TOL:
                continue
            if subtotal_top is not None and t >= subtotal_top - ROW_TOL:
                continue
            # Agrupar por top redondeado
            key = round(t / ROW_TOL) * ROW_TOL
            rows_map.setdefault(key, []).append(w)

        # Por cada fila, asignar palabras a columnas
        for key in sorted(rows_map):
            row_words = rows_map[key]

            def col_text(col):
                parts = [w["text"] for w in row_words if in_col(w["x0"], w["x1"], col)]
                return _clean(" ".join(parts))

            cant_text  = col_text(COL_CANT)
            desc_text  = col_text(COL_DESC)
            marca_text = col_text(COL_MARCA)
            um_text    = col_text(COL_UM)
            price_text = col_text(COL_PRICE)
            total_text = col_text(COL_TOTAL)

            # Filtrar filas sin cantidad numérica (notas, observaciones, etc.)
            qty = _to_float(cant_text)
            if not qty:
                continue
            if not desc_text or len(desc_text) < 3:
                continue

            price = _to_float(price_text) or 0.0
            total = _to_float(total_text) or round(qty * price, 2)
            unit  = um_text or "pza"

            # Descripción enriquecida: nombre + marca (separados por |)
            full_desc = desc_text
            if marca_text:
                full_desc = f"{desc_text} | {marca_text}"

            raw_parts = [p for p in [cant_text, desc_text, marca_text, um_text, price_text, total_text] if p]
            items.append({
                "description": full_desc,
                "qty": qty,
                "unit": unit,
                "precio_unit": price,
                "total": total,
                "raw_line": "  ".join(raw_parts),
            })

    # Metadatos extra del PDF de Procables
    return items


def _extract_procables_meta(pdf) -> dict:
    """Extrae número de cotización, fecha y proveedor del header de Procables."""
    meta = {"cot_number": "", "fecha": "", "proveedor": "Procables de México"}
    words = []
    for page in pdf.pages[:1]:
        words = page.extract_words(x_tolerance=4, y_tolerance=4)
        break
    full_text = " ".join(w["text"] for w in words)
    # Número de cotización
    m = re.search(r"COTIZACION\s*(\d+)", full_text, re.IGNORECASE)
    if m:
        meta["cot_number"] = m.group(1)
    # Fecha dd/mm/yyyy
    m = re.search(r"FECHA[:\s]+(\d{2}/\d{2}/\d{4})", full_text, re.IGNORECASE)
    if m:
        try:
            from datetime import datetime
            meta["fecha"] = datetime.strptime(m.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return meta


# ── Extractor genérico: tablas pdfplumber ─────────────────────────────────────

_QTY_HEADERS   = {"cant", "cantidad", "qty", "pcs", "piezas", "pza", "unidades", "u"}
_UNIT_HEADERS  = {"unidad", "unit", "um", "u/m", "u.m.", "u.m"}
_PRICE_HEADERS = {"precio", "p.u.", "p/u", "unitario", "unit price", "price", "costo", "preciou."}
_TOTAL_HEADERS = {"total", "importe", "subtotal", "monto", "amount"}
_DESC_HEADERS  = {"descripcion", "descripción", "description", "concepto", "material",
                  "articulo", "artículo", "partida", "item", "producto"}


def _header_map(row: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for i, cell in enumerate(row):
        key = _clean(str(cell or "")).lower().rstrip(".")
        if key in _DESC_HEADERS and "desc" not in mapping:
            mapping["desc"] = i
        elif key in _QTY_HEADERS and "qty" not in mapping:
            mapping["qty"] = i
        elif key in _UNIT_HEADERS and "unit" not in mapping:
            mapping["unit"] = i
        elif key in _PRICE_HEADERS and "price" not in mapping:
            mapping["price"] = i
        elif key in _TOTAL_HEADERS and "total" not in mapping:
            mapping["total"] = i
    return mapping


def _extract_from_tables(pdf) -> list[dict]:
    items: list[dict] = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            header_row = next((r for r in table if any(c for c in r)), None)
            if not header_row:
                continue
            hmap = _header_map([str(c or "") for c in header_row])
            skip_first = "desc" in hmap
            for row in (table[1:] if skip_first else table):
                if not row or not any(row):
                    continue
                cells = [str(c or "").strip() for c in row]
                if "desc" not in hmap and len(cells) < 2:
                    continue
                desc = _clean(cells[hmap["desc"]] if "desc" in hmap else cells[0])
                if not desc or len(desc) < 2:
                    continue
                if desc.lower().rstrip(".") in _DESC_HEADERS:
                    continue
                qty   = _to_float(cells[hmap["qty"]]   if "qty"   in hmap else (cells[1] if len(cells)>1 else ""))
                unit  = _clean(cells[hmap["unit"]]  if "unit"  in hmap else "")
                price = _to_float(cells[hmap["price"]] if "price" in hmap else (cells[2] if len(cells)>2 else ""))
                total = _to_float(cells[hmap["total"]] if "total" in hmap else (cells[3] if len(cells)>3 else ""))
                items.append({
                    "description": desc,
                    "qty": qty or 1.0,
                    "unit": unit or "pza",
                    "precio_unit": price or 0.0,
                    "total": total or (qty or 1.0) * (price or 0.0),
                    "raw_line": " | ".join(c for c in cells if c),
                })
    return items


# ── Extractor heurístico de texto plano ──────────────────────────────────────

_NUM = r"[\d]+(?:[.,]\d+)*"
_LINE_ITEM_RE = re.compile(
    r"^(?:\d{1,3}[\.\)]\s*)?"
    r"(?P<desc>[A-Za-záéíóúüñÁÉÍÓÚÜÑ][^\t]{8,}?)"
    r"\s+(?P<qty>" + _NUM + r")"
    r"(?:\s+(?P<unit>[A-Za-z]{1,5}))?"
    r"(?:\s+\$?\s*(?P<price>" + _NUM + r"))?"
    r"(?:\s+\$?\s*(?P<total>" + _NUM + r"))?"
    r"\s*$",
    re.IGNORECASE,
)
_IGNORE_LINE_RE = re.compile(
    r"^\s*(total|subtotal|iva|impuesto|folio|fecha|proveedor|cliente|"
    r"proyecto|cotizaci[oó]n|lista|p[aá]gina|page|\d+\s*/\s*\d+|"
    r"descripci[oó]n|cantidad|precio|importe|observaci[oó]n)\b",
    re.IGNORECASE,
)


def _extract_from_text(pdf) -> list[dict]:
    items: list[dict] = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 10 or _IGNORE_LINE_RE.match(line):
                continue
            m = _LINE_ITEM_RE.match(line)
            if not m:
                continue
            desc  = _clean(m.group("desc"))
            if not desc or len(desc) < 5:
                continue
            qty   = _to_float(m.group("qty")) or 1.0
            unit  = m.group("unit") or "pza"
            price = _to_float(m.group("price")) or 0.0
            total = _to_float(m.group("total")) or qty * price
            items.append({
                "description": desc,
                "qty": qty,
                "unit": unit,
                "precio_unit": price,
                "total": total,
                "raw_line": line,
            })
    return items


# ── API pública ───────────────────────────────────────────────────────────────

def extract_items_from_pdf(path: str) -> dict[str, Any]:
    """Lee un PDF de cotización de proveedor y extrae los ítems.

    Devuelve:
        {
            "items":      [{"description", "qty", "unit", "precio_unit", "total", "raw_line"}, ...],
            "method":     "procables" | "table" | "text" | "empty",
            "page_count": int,
            "meta":       {"cot_number", "fecha", "proveedor"},  # cuando se detecta
            "error":      str | None,
        }
    """
    try:
        import pdfplumber
    except ImportError:
        return {"items": [], "method": "empty", "page_count": 0, "meta": {},
                "error": "pdfplumber no instalado. Ejecuta: pip install pdfplumber --break-system-packages"}

    try:
        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            meta = {}

            # 1. Procables (extractor por coordenadas)
            if pdf.pages and _is_procables(pdf.pages[0]):
                items = _extract_procables(pdf)
                meta  = _extract_procables_meta(pdf)
                if items:
                    return {"items": items, "method": "procables",
                            "page_count": page_count, "meta": meta, "error": None}

            # 2. Tablas estructuradas genéricas
            items = _extract_from_tables(pdf)
            if items:
                return {"items": items, "method": "table",
                        "page_count": page_count, "meta": meta, "error": None}

            # 3. Heurística de texto
            items = _extract_from_text(pdf)
            if items:
                return {"items": items, "method": "text",
                        "page_count": page_count, "meta": meta, "error": None}

            return {"items": [], "method": "empty",
                    "page_count": page_count, "meta": meta, "error": None}

    except Exception as exc:  # noqa: BLE001
        return {"items": [], "method": "empty", "page_count": 0,
                "meta": {}, "error": str(exc)}
