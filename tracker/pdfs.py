import os
import re
from datetime import date, datetime

from .catalog import catalog_description_lookup, catalog_name_key, quote_section_groups, quote_type_key
from .storage import BASE_DIR, today


# ── PDF colour palette (shared across all PDF builders) ──────────────────────
# Quote / LDM palette
_PDF_NAVY   = (24, 39, 70)
_PDF_NAVY_2 = (40, 63, 110)
_PDF_INK    = (37, 44, 58)
_PDF_MUTED  = (113, 126, 145)
_PDF_LINE   = (215, 221, 230)
_PDF_SOFT   = (244, 247, 251)
_PDF_GREEN  = (34, 139, 94)
# Progress-report palette
_PDF_DARK   = (30,  45,  90)
_PDF_LIGHT  = (240, 244, 252)
_PDF_BLACK  = (20,  25,  35)
_PDF_WHITE  = (255, 255, 255)
_PDF_MUTED2 = (110, 120, 140)   # slightly different shade used by progress PDF
_PDF_GREEN2 = (34,  130, 80)

# ── Stage-status display labels ───────────────────────────────────────────────
STAGE_STATUS_LABELS = {
    "done": "Completado",
    "in_progress": "En progreso",
    "pending": "Pendiente",
}


def _hex_to_rgb(hex_color, default=(0, 0, 0)):
    """Parse #RRGGBB hex string to (r, g, b) int tuple."""
    try:
        h = str(hex_color or "").lstrip("#")
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:
        pass
    return default


def _safe_text(text):
    """Convierte cualquier valor a str limpio, apto para fpdf2 con DejaVu (UTF-8).
    Solo normaliza espacios, guiones tipográficos y comillas. NO trunca ni reemplaza
    caracteres fuera de latin-1 — DejaVu los renderiza directamente."""
    s = str(text if text is not None else "")
    return (
        s
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2022", "-")
        .replace("\u00b7", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
    )


def _register_dejavu(pdf):
    """Registra las fuentes DejaVu en tracker/fonts/.
    Devuelve False si no estan disponibles para que el caller falle con un error claro."""
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    regular = os.path.join(font_dir, "DejaVuSans.ttf")
    bold = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    oblique = os.path.join(font_dir, "DejaVuSans-Oblique.ttf")
    if os.path.isfile(regular) and os.path.isfile(bold):
        pdf.add_font("DejaVu", "", regular, uni=True)
        pdf.add_font("DejaVu", "B", bold, uni=True)
        if os.path.isfile(oblique):
            pdf.add_font("DejaVu", "I", oblique, uni=True)
        return True
    return False  # caller debe caer en Helvetica como fallback



def format_date_long(value):
    if not value:
        return "-"
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        return _safe_text(value)
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]
    return f"{dt.day} de {months[dt.month - 1]} de {dt.year}"


def money_pdf(value, currency=None):
    try:
        amount = float(value or 0)
    except Exception:
        return _safe_text(value)
    money = f"${amount:,.2f}"
    return f"{_safe_text(currency)} {money}" if currency else money


def note_lines(text):
    if not text:
        return []
    raw = str(text).replace("\r", "\n")
    return [_safe_text(line.strip(" -•\t")) for line in raw.split("\n") if line.strip(" -•\t")]


def _load_company():
    """Return the company dict from company.json, or {} on any error."""
    try:
        import json
        company_file = os.path.join(BASE_DIR, "data", "company.json")
        if os.path.isfile(company_file):
            with open(company_file, "r", encoding="utf-8") as _f:
                data = json.load(_f)
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def quote_logo_path():
    company = _load_company()
    logo_rel = company.get("logo") or ""
    if logo_rel:
        # Primary: persistent volume (data/uploads/)
        logo_abs = os.path.join(BASE_DIR, "data", "uploads", os.path.basename(logo_rel))
        if os.path.isfile(logo_abs):
            return logo_abs
        # Legacy fallback: static/uploads/ (pre-migration)
        logo_abs = os.path.join(BASE_DIR, "static", logo_rel)
        if os.path.isfile(logo_abs):
            return logo_abs
    # Legacy fallback paths
    candidates = [
        r"H:\My Drive\Omniious\OmnniiousLog.jpg",
        os.path.join(BASE_DIR, ".codex_tmp", "casa_leonides_pdf_assets", "page_1_img_1_Im6.jpg"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _company_name():
    return _load_company().get("name") or "Project Tracker"


def quote_scope_paragraphs():
    return [
        "La presente cotización considera únicamente los conceptos, materiales, equipos y trabajos expresamente descritos en la propuesta económica.",
        "Cualquier concepto, actividad, suministro o servicio no indicado de forma expresa se considerará fuera del alcance de la presente cotización y deberá cotizarse por separado.",
    ]


def quote_terms():
    return [
        ("Vigencia.", "La presente cotización tendrá vigencia de 15 días naturales a partir de su fecha de emisión."),
        ("Precios.", "Todos los precios están expresados en pesos mexicanos (MXN) y no incluyen IVA, salvo indicación expresa."),
        ("Información base y ajustes.", "La cotización fue elaborada con base en la información disponible al momento de su emisión. En caso de no contar con proyecto ejecutivo definitivo, así como por cambios en planos, especificaciones, cantidades, trayectorias, capacidades, materiales, equipos o condiciones reales de obra, la cotización podrá ser revisada y actualizada en alcance, precio y plazo."),
        ("Condiciones de pago.", "El inicio, continuidad y entrega de los trabajos estarán sujetos al cumplimiento de las condiciones de pago pactadas entre las partes."),
        ("Plazos.", "Los tiempos de suministro y ejecución estarán sujetos a disponibilidad de materiales, liberación de frentes, coordinación con otras especialidades y condiciones reales de obra. No serán imputables al contratista los atrasos derivados de cambios de proyecto, falta de pago, falta de liberación de áreas, retrasos de terceros, caso fortuito o fuerza mayor."),
        ("Trabajos adicionales.", "Todo trabajo adicional, modificación, adecuación o concepto no contemplado originalmente deberá cotizarse y autorizarse por separado antes de su ejecución."),
        ("Exclusiones.", "Salvo que se indique expresamente, no se incluyen obra civil, resanes, ranurados, perforaciones especiales, trámites, gestorías, permisos, acometidas de la compañía suministradora, pruebas especializadas por terceros ni cualquier otro trabajo fuera del alcance descrito."),
        ("Garantía.", "Los trabajos ejecutados contarán con garantía por defectos atribuibles a la mano de obra, así como por defectos en materiales o equipos suministrados, siempre que la instalación no haya sido modificada, sobrecargada, mal operada o intervenida por terceros."),
        ("Aceptación.", "La aprobación de la cotización mediante firma, orden de compra, anticipo o confirmación escrita implicará la aceptación total de precios, alcances y presentes términos y condiciones."),
    ]


def quote_sequence_from_number(quote_number):
    match = re.search(r"-[GPOES](\d{2,})(?:-|$)", str(quote_number or ""))
    return match.group(1) if match else ""


def quote_cover_copy(quote):
    discipline = str(quote.get("cover_discipline") or "").strip() or "Instalaciones Eléctricas"
    quote_type = quote_type_key(quote.get("quote_type"))
    if quote_type == "Proyecto":
        return f"Cotización de Proyecto\n{discipline}", None
    if quote_type == "Obra":
        return f"Cotización de Obra\n{discipline}", None
    if quote_type == "Servicio":
        return f"Cotización de Servicio\n{discipline}", None
    if quote_type == "Preliminar":
        return f"Cotización Preliminar de\n{discipline}", None
    if quote_type == "Extraordinaria":
        sequence = quote_sequence_from_number(quote.get("quote_number"))
        subtitle = f"Número secuencial de cotización {sequence}" if sequence else "Número secuencial de cotización"
        return f"Cotización Extraordinaria de\n{discipline}", subtitle
    return f"Cotización de {discipline}", None


def quote_project_basis_note(quote):
    quote_type = quote_type_key(quote.get("quote_type"))
    if quote_type in ("Preliminar", "Obra", "Servicio"):
        return ""
    if quote_type in ("General", "Proyecto"):
        source = quote.get("project_basis_source")
    elif quote_type == "Extraordinaria":
        source = quote.get("project_basis_note")
    else:
        source = ""
    source = str(source or "").strip()
    if not source:
        return ""
    return f"Cotización realizada con base en el proyecto: {source}"


def quote_catalog_description(item, catalog_lookup):
    explicit = item.get("catalog_description") or item.get("description_secondary") or item.get("descripcion")
    if explicit:
        return _safe_text(explicit)
    return _safe_text(catalog_lookup.get(catalog_name_key(item.get("description", "")), ""))


def build_quote_pdf(project, quote, output_path=None):
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError("fpdf2 no instalado. Ejecuta: pip install fpdf2 --break-system-packages") from exc

    LATERAL_MARGIN = 5  # margen izq/der (mm) - mismo criterio que build_ldm_pdf

    class QuotePDF(FPDF):
        def __init__(self, project_name, quote_number, quote_date):
            super().__init__(orientation="P", unit="mm", format="A4")
            self.project_name = project_name
            self.quote_number = quote_number
            self.quote_date = quote_date
            self.set_auto_page_break(auto=True, margin=18)
            self.set_margins(LATERAL_MARGIN, 14, LATERAL_MARGIN)
            self.alias_nb_pages()

        def header(self):
            if self.page_no() == 1:
                return
            left = self.l_margin
            right = self.w - self.r_margin
            cw = right - left
            self.set_draw_color(*LINE)
            self.line(left, 13, right, 13)
            self.set_xy(left, 6)
            self.set_font(FONT, "B", 9)
            self.set_text_color(*NAVY)
            self.cell(cw * 0.62, 6, _safe_text(self.project_name))
            self.set_font(FONT, "", 8.5)
            self.set_text_color(*MUTED)
            self.cell(cw * 0.22, 6, _safe_text(self.quote_number), align="C")
            self.cell(cw * 0.16, 6, _safe_text(self.quote_date), align="R")
            self.ln(10)

        def footer(self):
            left = self.l_margin
            right = self.w - self.r_margin
            self.set_y(-13)
            self.set_draw_color(*LINE)
            self.line(left, self.get_y() - 1.5, right, self.get_y() - 1.5)
            self.set_font(FONT, "", 8)
            self.set_text_color(*MUTED)
            self.cell(0, 5, f"{_cached_company_name}  ·  Página {self.page_no()}/{{nb}}", align="C")

    NAVY   = _PDF_NAVY
    NAVY_2 = _PDF_NAVY_2
    INK    = _PDF_INK
    MUTED  = _PDF_MUTED
    LINE   = _PDF_LINE
    SOFT   = _PDF_SOFT
    GREEN  = _PDF_GREEN

    _company_data = _load_company()
    _cached_company_name = _safe_text(_company_data.get("name") or "Project Tracker")

    items = quote.get("items", [])
    currency = quote.get("currency") or "MXN"
    project_name = _safe_text(project.get("name", ""))
    client_name = _safe_text(quote.get("client") or project.get("client") or "Cliente")
    quote_number = _safe_text(quote.get("quote_number", "Cotización"))
    quote_date = format_date_long(quote.get("date"))
    cover_title, cover_subtitle = quote_cover_copy(quote)
    cover_basis_note = quote_project_basis_note(quote)
    logo_path = quote_logo_path()
    catalog_lookup = catalog_description_lookup()

    pdf = QuotePDF(project_name, quote_number, quote_date)
    if not _register_dejavu(pdf):
        raise RuntimeError("No se encontraron fuentes DejaVu para generar PDF con UTF-8.")
    FONT = "DejaVu"
    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    def normalize_wrap_text(text):
        text = _safe_text(text)
        text = re.sub(r"(\d+)\s*-\s*(\d+\s\[[^\]]+\])", r"\1-\2", text)
        text = re.sub(r"\s*\|\s*", " | ", text)
        return " ".join(text.split())

    def wrap_word_groups(text, width):
        words = normalize_wrap_text(text).split()
        if not words:
            return [""]

        groups = []
        index = 0
        while index < len(words):
            word = words[index]

            if index + 3 < len(words) and words[index].isdigit() and words[index + 1] == "-" and words[index + 2].isdigit() and words[index + 3].startswith("["):
                groups.append(f"{words[index]} - {words[index + 2]} {words[index + 3]}")
                index += 4
                continue

            if index + 1 < len(words) and words[index].isdigit() and words[index + 1].startswith("["):
                groups.append(f"{words[index]} {words[index + 1]}")
                index += 2
                continue

            if index + 1 < len(words) and re.search(r"\d-\d", words[index]) and words[index + 1].startswith("["):
                groups.append(f"{words[index]} {words[index + 1]}")
                index += 2
                continue

            if index + 1 < len(words) and words[index].startswith("[") and (words[index + 1].startswith("(") or words[index + 1].startswith('"')):
                groups.append(f"{words[index]} {words[index + 1]}")
                index += 2
                continue

            if index + 1 < len(words) and words[index] in {"-", "/"}:
                groups.append(f"{words[index]} {words[index + 1]}")
                index += 2
                continue

            if index + 1 < len(words) and word.lower() in {"a", "al", "con", "de", "del", "e", "en", "o", "por", "u", "y"}:
                groups.append(f"{word} {words[index + 1]}")
                index += 2
                continue

            groups.append(word)
            index += 1

        lines = []
        current = groups[0]
        for group in groups[1:]:
            trial = f"{current} {group}"
            if pdf.get_string_width(trial) <= width:
                current = trial
            else:
                lines.append(current)
                current = group
        lines.append(current)
        return lines

    def wrap_text(text, width):
        text = normalize_wrap_text(text)
        if not text:
            return [""]
        if "|" in text:
            parts = [part.strip() for part in text.split("|") if part.strip()]
            if len(parts) > 1:
                lines = []
                current = parts[0]
                for part in parts[1:]:
                    trial = f"{current} | {part}"
                    if pdf.get_string_width(trial) <= width:
                        current = trial
                    else:
                        lines.append(current)
                        current = part
                lines.append(current)
                final_lines = []
                for line in lines:
                    if pdf.get_string_width(line) <= width:
                        final_lines.append(line)
                    else:
                        final_lines.extend(wrap_word_groups(line, width))
                return final_lines
        return wrap_word_groups(text, width)

    def split_secondary_lines(text, width):
        text = normalize_wrap_text(text)
        if not text:
            return [], []
        parts = [part.strip() for part in text.split("|") if part.strip()]
        if not parts:
            return [], []
        brand_lines = wrap_word_groups(parts[0], width)
        detail_text = " | ".join(parts[1:]).strip()
        detail_lines = wrap_text(detail_text, width) if detail_text else []
        return brand_lines, detail_lines

    def _smart_groups(text):
        """Convierte words a grupos atomicos respetando conectores y unidades."""
        words = text.split()
        if not words:
            return []
        groups = []
        i = 0
        while i < len(words):
            word = words[i]
            # "3F - 4H" - configuracion de fases/hilos no debe dejar "-" solo.
            if (
                i + 2 < len(words)
                and re.match(r"^\d+[A-Za-z]+$", word)
                and words[i+1] == "-"
                and re.match(r"^\d+[A-Za-z]+$", words[i+2])
            ):
                groups.append(f"{word} - {words[i+2]}")
                i += 3
                continue
            # "16 [mm]", "120/240 [V]", "240-600 [V]" y opcional
            # equivalencia entre parentesis: "35 [mm] (1 1/4\")".
            if i + 1 < len(words) and re.match(r"^\d+(?:[./-]\d+)*$", word) and words[i+1].startswith("["):
                group_parts = [word, words[i+1]]
                j = i + 2
                if j < len(words) and words[j].startswith("("):
                    while j < len(words):
                        group_parts.append(words[j])
                        j += 1
                        if group_parts[-1].endswith(")") or ")" in group_parts[-1]:
                            break
                groups.append(" ".join(group_parts))
                i = j
                continue
            # "[mm] (1\")" - bracket + parentesis/comillas
            if i + 1 < len(words) and word.startswith("[") and (words[i+1].startswith("(") or words[i+1].startswith('"')):
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            # "- 4H" / "/ 240" - separador + siguiente
            if i + 1 < len(words) and word in {"-", "/"}:
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            # "de Tubería" - conector + siguiente
            if i + 1 < len(words) and word.lower() in {"a", "al", "con", "de", "del", "e", "en", "o", "por", "u", "y"}:
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            groups.append(word)
            i += 1
        return groups

    NBSP = chr(0xA0)  # non-breaking space - fpdf2 NO parte aqui

    def smart_render_text(text, width=None):
        """Devuelve text listo para multi_cell con secciones (separadas por '|')
        con unidades/conectores protegidos internamente. El separador queda con
        espacios normales para no crear bloques largos que partan palabras."""
        if not text:
            return ""
        text = normalize_wrap_text(text)
        if not text:
            return ""
        sections = text.split(" | ")
        rendered_sections = [
            [group.replace(" ", NBSP) for group in _smart_groups(sec)]
            for sec in sections
        ]
        if width is None:
            return " | ".join(" ".join(groups) for groups in rendered_sections)

        def join_units(units):
            return " ".join(units)

        def fits(units):
            return pdf.get_string_width(join_units(units)) <= width

        lines = []
        current = []

        def commit():
            nonlocal current
            if current:
                lines.append(join_units(current))
                current = []

        def append_group(group):
            nonlocal current
            trial = current + [group]
            if not current or fits(trial):
                current = trial
                return
            commit()
            current = [group]

        for sec_index, groups in enumerate(rendered_sections):
            if not groups:
                continue
            if sec_index == 0:
                for group in groups:
                    append_group(group)
                continue

            first = groups[0]
            if current and fits(current + ["|", first]):
                current = current + ["|", first]
            elif current:
                previous = current.pop()
                commit()
                combo = [previous, "|", first]
                current = combo if fits(combo) else [previous, "|", first]
            else:
                current = ["|", first]

            for group in groups[1:]:
                append_group(group)

        commit()
        return "\n".join(lines)

    def split_secondary_render(text, width=None):
        """Como split_secondary_lines pero devuelve (brand_text, detail_text) listos
        para multi_cell (con \xa0 internos)."""
        if not text:
            return "", ""
        text = normalize_wrap_text(text)
        parts = [p.strip() for p in text.split("|") if p.strip()]
        if not parts:
            return "", ""
        brand_text = smart_render_text(parts[0], width)
        detail_raw = " | ".join(parts[1:]).strip()
        detail_text = smart_render_text(detail_raw, width) if detail_raw else ""
        return brand_text, detail_text

    def wrapped_height(text, width, line_h):
        return len(wrap_text(text, width)) * line_h

    def section_title(title, subtitle=None):
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(*INK)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(content_width, 7, _safe_text(title), ln=True)
        if subtitle:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("DejaVu", "", 9)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(content_width, 4.5, _safe_text(subtitle))
        pdf.ln(2)

    def add_signature_section():
        block_h = 28
        top = max(pdf.get_y() + 8, pdf.h - pdf.b_margin - block_h)
        if top + block_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            top = pdf.h - pdf.b_margin - block_h

        line_y = top + 10
        left_x = 24
        right_x = 116
        line_w = 70

        pdf.set_draw_color(*LINE)
        pdf.line(left_x, line_y, left_x + line_w, line_y)
        pdf.line(right_x, line_y, right_x + line_w, line_y)

        pdf.set_text_color(*MUTED)
        pdf.set_font("DejaVu", "", 8.6)
        pdf.set_xy(left_x, line_y + 2.5)
        pdf.cell(line_w, 4.5, "Cliente / Aceptación", align="C")
        pdf.set_xy(right_x, line_y + 2.5)
        pdf.cell(line_w, 4.5, _cached_company_name, align="C")

        pdf.set_font("DejaVu", "", 7.8)
        pdf.set_xy(left_x, line_y + 7.2)
        pdf.cell(line_w, 4, "Nombre, firma y fecha", align="C")
        pdf.set_xy(right_x, line_y + 7.2)
        pdf.cell(line_w, 4, "Representante autorizado", align="C")

        pdf.set_y(top + block_h)

    # Columnas de tabla: UNIDAD/CANT. comparten ancho y P.UNIT/IMPORTE comparten ancho.
    # Descripcion absorbe el resto para que la suma == content_width.
    NUM_W = 8
    UNIT_QTY_W = 14   # compacto para dar mas aire a DESCRIPCION
    PRICE_W = 28      # P.UNIT e IMPORTE - suficiente para montos comunes en 10pt
    DESC_W = content_width - (NUM_W + UNIT_QTY_W * 2 + PRICE_W * 2)
    QUOTE_COLS = [NUM_W, DESC_W, UNIT_QTY_W, UNIT_QTY_W, PRICE_W, PRICE_W]

    def table_header():
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("DejaVu", "B", 8)
        heads = ["#", "DESCRIPCIÓN", "UNIDAD", "CANT.", "P. UNIT.", "IMPORTE"]
        aligns = ["C", "L", "C", "C", "C", "C"]
        for width, text, align in zip(QUOTE_COLS, heads, aligns):
            pdf.cell(width, 7, text, fill=True, align=align)
        pdf.ln()
        return list(QUOTE_COLS)

    def ensure_space(height, with_table_header=False):
        if pdf.get_y() + height <= (pdf.h - pdf.b_margin):
            return
        pdf.add_page()
        if with_table_header:
            table_header()

    _specs = quote.get("specs") or {}
    _portada_spacing = max(8, min(88, int(str(_specs.get("portada_spacing") or "40") or "40")))
    _spacing_delta = (_portada_spacing - 40) * 0.45

    _portada_fill = _hex_to_rgb(_company_data.get("portada_color"), default=(0, 0, 0))

    pdf.add_page()
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(*_portada_fill)
    pdf.rect(0, 0, 210, 112, style="F")
    if logo_path:
        pdf.image(logo_path, x=55, y=20, w=100)
    else:
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(16, 28)
        pdf.set_font("DejaVu", "B", 18)
        pdf.cell(0, 8, _cached_company_name)
    pdf.set_draw_color(*LINE)
    _caddr = str(_company_data.get("address") or "").strip()
    _crut = str(_company_data.get("rut") or "").strip()
    _cinfo = "  ·  ".join(p for p in [_caddr, _crut] if p)
    if _cinfo:
        pdf.set_text_color(*MUTED)
        pdf.set_font("DejaVu", "", 8)
        pdf.set_xy(16, 115)
        pdf.cell(178, 4.5, _safe_text(_cinfo), align="R")
    pdf.line(16, 128, 194, 128)
    pdf.set_xy(16, 138)
    pdf.set_text_color(*NAVY)
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(0, 5, "PROPUESTA ECONÓMICA")
    pdf.set_xy(16, 148)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 18)
    pdf.multi_cell(158, 8, _safe_text(cover_title))
    if cover_basis_note:
        pdf.ln(1)
        pdf.set_x(16)
        pdf.set_text_color(*NAVY_2)
        pdf.set_font("DejaVu", "", 10.5)
        pdf.multi_cell(170, 5.3, _safe_text(cover_basis_note))
    if cover_subtitle:
        pdf.ln(1)
        pdf.set_x(16)
        pdf.set_text_color(*NAVY_2)
        pdf.set_font("DejaVu", "B", 10.5)
        pdf.cell(0, 5.5, _safe_text(cover_subtitle), ln=True)
    proposal_y = max(168 + _spacing_delta, pdf.get_y() + 7)
    pdf.set_xy(16, proposal_y)
    pdf.set_text_color(*MUTED)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, "Propuesta para")
    pdf.set_xy(16, proposal_y + 9)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 15)
    pdf.multi_cell(112, 7, client_name)
    summary_x = 16
    summary_y = max(215, min(250, round(221 + _spacing_delta)))
    summary_w = 178
    summary_h = 53
    pdf.set_xy(summary_x, summary_y)
    pdf.set_fill_color(*SOFT)
    pdf.rect(summary_x, summary_y, summary_w, summary_h, style="F")

    totals_box_x = 100
    totals_box_w = 88
    totals_box_h = 34
    totals_box_y = summary_y + (summary_h - totals_box_h) / 2
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*LINE)
    pdf.rect(totals_box_x, totals_box_y, totals_box_w, totals_box_h, style="DF")

    left_x = 22
    left_w = totals_box_x - left_x - 8
    label_h = 3.8
    value_h = 5.8

    def info_label(text, width=None, ln=False, size=8):
        pdf.set_text_color(*MUTED)
        pdf.set_font("DejaVu", "B", size)
        pdf.cell(width if width is not None else left_w, label_h, text, ln=ln)

    def info_value(text, width=None, ln=False, size=9.8):
        pdf.set_text_color(*INK)
        pdf.set_font("DejaVu", "", size)
        pdf.cell(width if width is not None else left_w, value_h, text, ln=ln)

    # Renglón 1: Proyecto
    pdf.set_xy(left_x, summary_y + 5)
    info_label("PROYECTO", ln=True)
    pdf.set_x(left_x)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "", 9.8)
    _pname_safe = _safe_text(project_name)
    _l1, _l2 = [], []
    _filling = _l1
    for _tok in _pname_safe.split():
        _test = " ".join(_filling + [_tok])
        if pdf.get_string_width(_test) <= left_w:
            _filling.append(_tok)
        else:
            if _filling is _l1:
                _filling = _l2
                _filling.append(_tok)
            else:
                break
    for _pline in (_l1, _l2):
        if _pline:
            pdf.set_x(left_x)
            pdf.cell(left_w, value_h, " ".join(_pline), ln=True)

    # Renglón 2: Cotización
    pdf.set_xy(left_x, summary_y + 24)
    info_label("COTIZACIÓN", ln=True)
    pdf.set_x(left_x)
    info_value(quote_number, ln=True)

    # Renglón 3: Moneda / Fecha / Versión (mismo ritmo que los anteriores)
    # Anchos calibrados con metricas reales de Helvetica:
    #   labels @7pt:    MONEDA ~11 mm, FECHA ~9 mm, VERSIÓN ~11 mm
    #   values @10.2pt: "MXN" ~8 mm, "30 de septiembre de 2026" ~42 mm, "Rev.10" ~11 mm
    moneda_w = 18
    fecha_w = 39
    version_w = 12
    moneda_x = left_x
    fecha_x = moneda_x + moneda_w
    version_x = fecha_x + fecha_w

    label_y = summary_y + 43
    label_size = 7
    pdf.set_xy(moneda_x, label_y)
    info_label("MONEDA", width=moneda_w, size=label_size)
    pdf.set_x(fecha_x)
    info_label("FECHA", width=fecha_w, size=label_size)
    pdf.set_x(version_x)
    info_label("VERSIÓN", width=version_w, size=label_size, ln=True)

    pdf.set_xy(moneda_x, label_y + label_h)
    info_value(_safe_text(currency), width=moneda_w)
    pdf.set_x(fecha_x)
    info_value(quote_date, width=fecha_w)
    pdf.set_x(version_x)
    info_value(_safe_text(quote.get("version") or project.get("version") or "V1"), width=version_w, ln=True)

    # --- Caja de totales (más espaciada y con jerarquía clara) ---
    label_x = totals_box_x + 8
    inner_right = totals_box_x + totals_box_w - 8
    label_w = 30
    value_w = inner_right - label_x - label_w
    row_h = 6.6

    # Subtotal (moneda omitida: ya esta en el campo MONEDA)
    pdf.set_xy(label_x, totals_box_y + 5.5)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 10.8)
    pdf.cell(label_w, row_h, "Subtotal")
    pdf.cell(value_w, row_h, money_pdf(quote.get("subtotal", 0)), align="R", ln=True)

    # IVA
    pdf.set_xy(label_x, totals_box_y + 13.7)
    pdf.cell(label_w, row_h, f"IVA ({quote.get('tax_rate', 16)}%)")
    pdf.cell(value_w, row_h, money_pdf(quote.get("tax", 0)), align="R", ln=True)

    # Divisor
    pdf.set_draw_color(*LINE)
    pdf.line(label_x, totals_box_y + 21.8, inner_right, totals_box_y + 21.8)

    # TOTAL
    pdf.set_xy(label_x, totals_box_y + 24.5)
    pdf.set_font("DejaVu", "B", 13.2)
    pdf.cell(label_w, 7.5, "TOTAL")
    pdf.set_text_color(*GREEN)
    pdf.cell(value_w, 7.5, money_pdf(quote.get("total", 0)), align="R", ln=True)

    pdf.add_page()
    pdf.set_y(22)

    # 1. Bloque de Alcance (va antes que el titulo "Detalle de partidas")
    pdf.set_fill_color(*SOFT)
    pdf.set_draw_color(*LINE)
    scope_inner_pad = 6
    scope_inner_left = pdf.l_margin + scope_inner_pad
    scope_inner_w = content_width - scope_inner_pad * 2
    scope_paragraphs = quote_scope_paragraphs()
    scope_text_h = sum(wrapped_height(paragraph, scope_inner_w, 4.3) for paragraph in scope_paragraphs)
    scope_h = 10 + scope_text_h + (len(scope_paragraphs) - 1) * 1.4 + 6
    scope_y = pdf.get_y()
    pdf.rect(pdf.l_margin, scope_y, content_width, scope_h, style="DF")
    pdf.set_xy(scope_inner_left, scope_y + 5)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 5, "Alcance", ln=True)
    pdf.set_x(scope_inner_left)
    pdf.set_font("DejaVu", "", 8.8)
    for index, paragraph in enumerate(scope_paragraphs):
        pdf.multi_cell(scope_inner_w, 4.3, _safe_text(paragraph))
        if index != len(scope_paragraphs) - 1:
            pdf.ln(1.4)
            pdf.set_x(scope_inner_left)
    pdf.set_y(scope_y + scope_h + 6)

    # 2. Titulo "Detalle de partidas"
    section_title("Detalle de partidas", "Desglose económico de conceptos incluidos en la propuesta.")
    cols = table_header()
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "", 8.6)
    item_index = 0

    for section in quote_section_groups(items):
        section_name = _safe_text(section.get("name", ""))
        if section_name:
            ensure_space(10, with_table_header=True)
            pdf.set_fill_color(*INK)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("DejaVu", "B", 8.8)
            pdf.cell(sum(cols), 7, section_name.upper(), fill=True)
            pdf.ln()
            pdf.set_text_color(*INK)
            pdf.set_font("DejaVu", "", 8.6)

        for item in section.get("items", []):
            item_index += 1
            # 1. Smart render text con NBSP (atomos no-breakeables; fpdf2 solo
            #    parte en los espacios entre grupos / entre secciones de "|").
            catalog_desc = quote_catalog_description(item, catalog_lookup)

            # 2. Medir alturas reales con dry_run (fpdf2 puede repartir distinto a mi pre-wrap;
            #    asi tengo el conteo exacto de lineas que realmente va a renderizar).
            pdf.set_font("DejaVu", "B", 10)
            desc_text = smart_render_text(item.get("description", ""), cols[1] - 4)
            title_lines = pdf.multi_cell(cols[1] - 4, 5.0, desc_text, align="L",
                                         dry_run=True, output="LINES") if desc_text else []
            pdf.set_font("DejaVu", "", 7.5)
            brand_text, detail_text = split_secondary_render(catalog_desc, cols[1] - 4)
            brand_lines = pdf.multi_cell(cols[1] - 4, 3.7, brand_text, align="L",
                                         dry_run=True, output="LINES") if brand_text else []
            detail_lines = pdf.multi_cell(cols[1] - 4, 3.7, detail_text, align="L",
                                          dry_run=True, output="LINES") if detail_text else []
            title_h = 5.0 * len(title_lines)
            brand_h = 3.7 * len(brand_lines)
            detail_h = 3.7 * len(detail_lines)
            text_h = 1.6 + title_h
            if brand_lines:
                text_h += 0.7 + brand_h
            if detail_lines:
                text_h += 0.3 + detail_h
            row_h = max(14, text_h + 1.8)
            ensure_space(row_h, with_table_header=True)
            row_y = pdf.get_y()
            fill = (245, 247, 250) if item_index % 2 else (255, 255, 255)
            pdf.set_fill_color(*fill)
            pdf.set_draw_color(*LINE)
            pdf.rect(pdf.l_margin, row_y, sum(cols), row_h, style="FD")

            number_x = pdf.l_margin
            x = number_x + cols[0]

            desc_x = x + 2
            desc_y = row_y + 1.3
            # 3. Renderizar con align="L" (sin justify) y avanzar usando pdf.get_y()
            #    para garantizar que el cursor coincide con el render real.
            pdf.set_xy(desc_x, desc_y)
            pdf.set_font("DejaVu", "B", 10)
            pdf.set_text_color(*INK)
            if desc_text:
                pdf.multi_cell(cols[1] - 4, 5.0, desc_text, align="L")
            if brand_text:
                pdf.set_xy(desc_x, pdf.get_y() + 0.7)
                pdf.set_font("DejaVu", "", 7.5)
                pdf.set_text_color(*NAVY_2)
                pdf.multi_cell(cols[1] - 4, 3.7, brand_text, align="L")
            if detail_text:
                pdf.set_xy(desc_x, pdf.get_y() + 0.3)
                pdf.set_font("DejaVu", "", 7.5)
                pdf.set_text_color(*MUTED)
                pdf.multi_cell(cols[1] - 4, 3.7, detail_text, align="L")
            x += cols[1]

            pdf.set_xy(x, row_y)
            pdf.set_font("DejaVu", "", 10)  # datos numericos
            pdf.set_text_color(*INK)
            pdf.cell(cols[2], row_h, _safe_text(item.get("unit", "")), align="C")
            x += cols[2]

            pdf.set_xy(x, row_y)
            pdf.cell(cols[3], row_h, f"{float(item.get('qty', 0)):,.2f}", align="C")
            x += cols[3]

            pdf.set_xy(x, row_y)
            pdf.cell(cols[4], row_h, money_pdf(item.get("price", 0)), align="C")
            x += cols[4]

            pdf.set_xy(x, row_y)
            pdf.set_font("DejaVu", "B", 10)  # importe (bold)
            pdf.cell(cols[5], row_h, money_pdf(item.get("total", 0)), align="C")
            pdf.set_xy(number_x, row_y + max((row_h - 5.5) / 2, 1))
            pdf.set_font("DejaVu", "B", 10)  # numero de fila
            pdf.set_text_color(*INK)
            pdf.cell(cols[0], 5.5, str(item_index), align="C")
            pdf.set_font("DejaVu", "", 8.6)
            pdf.set_y(row_y + row_h)

        if section_name:
            ensure_space(7, with_table_header=True)
            label_width = sum(cols[:-1])
            value_width = cols[-1]
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(*LINE)
            pdf.set_text_color(*INK)
            pdf.set_font("DejaVu", "B", 8)
            pdf.cell(label_width, 6.6, f"{section_name.upper()} TOTAL", border="T", align="R")
            pdf.cell(value_width, 6.6, money_pdf(section.get("subtotal", 0)), border="T", align="C", ln=True)
            pdf.set_font("DejaVu", "", 8.6)

    _nota_precio = str(_specs.get("nota_precio") or "").strip()
    if _nota_precio:
        ensure_space(8)
        pdf.ln(2)
        pdf.set_text_color(*MUTED)
        pdf.set_font("DejaVu", "", 8.2)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(content_width, 4.5, _safe_text(_nota_precio), align="R")
        pdf.ln(1)

    pdf.add_page()
    pdf.set_y(22)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 17)
    _CONDICION_FIELDS = ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto")
    _has_specs = any(str(_specs.get(f) or "").strip() for f in _CONDICION_FIELDS)
    if _has_specs:
        pdf.cell(content_width, 8, "Condiciones y especificaciones", ln=True)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("DejaVu", "", 9.4)
        pdf.set_text_color(*INK)
        pdf.ln(1)
        _SPECS_LABELS = [
            ("condiciones_pago", "Condiciones de pago."),
            ("exclusiones", "Exclusiones."),
            ("validez", "Vigencia."),
            ("forma_entrega", "Forma de entrega."),
            ("contacto", "Contacto."),
        ]
        for _field, _label in _SPECS_LABELS:
            _val = str(_specs.get(_field) or "").strip()
            if not _val:
                continue
            pdf.set_x(pdf.l_margin)
            pdf.set_font("DejaVu", "B", 9.2)
            pdf.multi_cell(content_width, 5, _safe_text(_label))
            pdf.set_x(pdf.l_margin)
            pdf.set_font("DejaVu", "", 9.2)
            pdf.multi_cell(content_width, 5, _safe_text(_val))
            pdf.ln(1.2)
    else:
        pdf.cell(content_width, 8, "Términos y condiciones", ln=True)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("DejaVu", "", 9.4)
        pdf.set_text_color(*INK)
        pdf.ln(1)
        for title, body in quote_terms():
            pdf.set_x(pdf.l_margin)
            pdf.set_font("DejaVu", "B", 9.2)
            pdf.multi_cell(content_width, 5, _safe_text(title))
            pdf.set_x(pdf.l_margin)
            pdf.set_font("DejaVu", "", 9.2)
            pdf.multi_cell(content_width, 5, _safe_text(body))
            pdf.ln(1.2)

    notes = note_lines(quote.get("notes"))
    if notes:
        pdf.ln(2)
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(content_width, 6, "Notas", ln=True)
        pdf.set_font("DejaVu", "", 9.2)
        for line in notes:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(content_width, 5, _safe_text(f"- {line}"))

    add_signature_section()

    if output_path:
        pdf.output(output_path)
    else:
        return bytes(pdf.output())


def build_ldm_pdf(project, ldm, output_path=None):
    """Genera el PDF de una Lista de Materiales con la estética del PDF de
    cotizaciones (banner negro + logo, paleta navy/ink/muted, tabla de partidas)
    pero en una version simplificada: solo encabezado con proyecto/proveedor/fecha
    y tabla de items. Sin alcance, sin terminos, sin firma.
    """
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError("fpdf2 no instalado. Ejecuta: pip install fpdf2 --break-system-packages") from exc

    NAVY   = _PDF_NAVY
    NAVY_2 = _PDF_NAVY_2
    INK    = _PDF_INK
    MUTED  = _PDF_MUTED
    LINE   = _PDF_LINE
    SOFT   = _PDF_SOFT
    GREEN  = _PDF_GREEN

    _ldm_company_data = _load_company()
    _cached_company_name = _safe_text(_ldm_company_data.get("name") or "Project Tracker")

    items = ldm.get("items", [])
    project_name = _safe_text(project.get("name", ""))
    proveedor_name = _safe_text(ldm.get("proveedor", "") or "Proveedor")
    ldm_number = _safe_text(ldm.get("ldm_number", "Lista de Materiales"))
    ldm_date = format_date_long(ldm.get("fecha"))
    logo_path = quote_logo_path()
    catalog_lookup = catalog_description_lookup()
    with_prices = any(float(item.get("precio_cot", 0) or 0) for item in items)

    LATERAL_MARGIN = 5  # margen izq/der (mm) - facil de tunear en un solo lugar

    class LDMPDF(FPDF):
        def __init__(self, project_name, ldm_number, ldm_date):
            super().__init__(orientation="P", unit="mm", format="A4")
            self.project_name = project_name
            self.ldm_number = ldm_number
            self.ldm_date = ldm_date
            self.set_auto_page_break(auto=True, margin=18)
            self.set_margins(LATERAL_MARGIN, 14, LATERAL_MARGIN)
            self.alias_nb_pages()

        def header(self):
            if self.page_no() == 1:
                return
            left = self.l_margin
            right = self.w - self.r_margin
            cw = right - left  # content width
            self.set_draw_color(*LINE)
            self.line(left, 13, right, 13)
            self.set_xy(left, 6)
            self.set_font("DejaVu", "B", 11)
            self.set_text_color(*NAVY)
            self.cell(cw * 0.57, 6, _safe_text(self.project_name))
            self.set_font("DejaVu", "", 8.5)
            self.set_text_color(*MUTED)
            self.cell(cw * 0.23, 6, _safe_text(self.ldm_number), align="C")
            self.cell(cw * 0.20, 6, _safe_text(self.ldm_date), align="R")
            self.ln(10)

        def footer(self):
            left = self.l_margin
            right = self.w - self.r_margin
            self.set_y(-13)
            self.set_draw_color(*LINE)
            self.line(left, self.get_y() - 1.5, right, self.get_y() - 1.5)
            self.set_font("DejaVu", "", 8)
            self.set_text_color(*MUTED)
            self.cell(0, 5, f"{_cached_company_name}  ·  Página {self.page_no()}/{{nb}}", align="C")

    pdf = LDMPDF(project_name, ldm_number, ldm_date)
    if not _register_dejavu(pdf):
        raise RuntimeError("No se encontraron fuentes DejaVu para generar PDF con UTF-8.")
    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    # ----------------------------------------------------------- helpers
    def normalize_wrap_text(text):
        text = _safe_text(text)
        text = re.sub(r"(\d+)\s*-\s*(\d+\s\[[^\]]+\])", r"\1-\2", text)
        text = re.sub(r"\s*\|\s*", " | ", text)
        return " ".join(text.split())

    def wrap_word_groups(text, width):
        words = normalize_wrap_text(text).split()
        if not words:
            return [""]
        groups = []
        index = 0
        while index < len(words):
            word = words[index]
            if index + 1 < len(words) and word.lower() in {"a", "al", "con", "de", "del", "e", "en", "o", "por", "u", "y"}:
                groups.append(f"{word} {words[index + 1]}")
                index += 2
                continue
            groups.append(word)
            index += 1
        lines = []
        current = groups[0]
        for group in groups[1:]:
            trial = f"{current} {group}"
            if pdf.get_string_width(trial) <= width:
                current = trial
            else:
                lines.append(current)
                current = group
        lines.append(current)
        return lines

    def wrap_text(text, width):
        text = normalize_wrap_text(text)
        if not text:
            return [""]
        return wrap_word_groups(text, width)

    def split_secondary_lines(text, width):
        text = normalize_wrap_text(text)
        if not text:
            return [], []
        parts = [part.strip() for part in text.split("|") if part.strip()]
        if not parts:
            return [], []
        brand_lines = wrap_word_groups(parts[0], width)
        detail_text = " | ".join(parts[1:]).strip()
        detail_lines = wrap_text(detail_text, width) if detail_text else []
        return brand_lines, detail_lines

    NBSP = chr(0xA0)  # non-breaking space - fpdf2 NO parte aqui

    def _smart_groups(text):
        """Convierte words a grupos atomicos respetando conectores y unidades."""
        words = text.split()
        if not words:
            return []
        groups = []
        i = 0
        while i < len(words):
            word = words[i]
            if (
                i + 2 < len(words)
                and re.match(r"^\d+[A-Za-z]+$", word)
                and words[i+1] == "-"
                and re.match(r"^\d+[A-Za-z]+$", words[i+2])
            ):
                groups.append(f"{word} - {words[i+2]}")
                i += 3
                continue
            if i + 1 < len(words) and re.match(r"^\d+(?:[./-]\d+)*$", word) and words[i+1].startswith("["):
                group_parts = [word, words[i+1]]
                j = i + 2
                if j < len(words) and words[j].startswith("("):
                    while j < len(words):
                        group_parts.append(words[j])
                        j += 1
                        if group_parts[-1].endswith(")") or ")" in group_parts[-1]:
                            break
                groups.append(" ".join(group_parts))
                i = j
                continue
            if i + 1 < len(words) and word.startswith("[") and (words[i+1].startswith("(") or words[i+1].startswith('"')):
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            if i + 1 < len(words) and word in {"-", "/"}:
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            if i + 1 < len(words) and word.lower() in {"a", "al", "con", "de", "del", "e", "en", "o", "por", "u", "y"}:
                groups.append(f"{word} {words[i+1]}")
                i += 2
                continue
            groups.append(word)
            i += 1
        return groups

    def smart_render_text(text, width=None):
        """Devuelve text listo para multi_cell. Secciones (separadas por '|')
        con unidades/conectores protegidos internamente. El separador queda con
        espacios normales para no crear bloques largos que partan palabras."""
        if not text:
            return ""
        text = normalize_wrap_text(text)
        if not text:
            return ""
        sections = text.split(" | ")
        rendered_sections = [
            [group.replace(" ", NBSP) for group in _smart_groups(sec)]
            for sec in sections
        ]
        if width is None:
            return " | ".join(" ".join(groups) for groups in rendered_sections)

        def join_units(units):
            return " ".join(units)

        def fits(units):
            return pdf.get_string_width(join_units(units)) <= width

        lines = []
        current = []

        def commit():
            nonlocal current
            if current:
                lines.append(join_units(current))
                current = []

        def append_group(group):
            nonlocal current
            trial = current + [group]
            if not current or fits(trial):
                current = trial
                return
            commit()
            current = [group]

        for sec_index, groups in enumerate(rendered_sections):
            if not groups:
                continue
            if sec_index == 0:
                for group in groups:
                    append_group(group)
                continue

            first = groups[0]
            if current and fits(current + ["|", first]):
                current = current + ["|", first]
            elif current:
                previous = current.pop()
                commit()
                combo = [previous, "|", first]
                current = combo if fits(combo) else [previous, "|", first]
            else:
                current = ["|", first]

            for group in groups[1:]:
                append_group(group)

        commit()
        return "\n".join(lines)

    def split_secondary_render(text, width=None):
        if not text:
            return "", ""
        text = normalize_wrap_text(text)
        parts = [p.strip() for p in text.split("|") if p.strip()]
        if not parts:
            return "", ""
        brand_text = smart_render_text(parts[0], width)
        detail_raw = " | ".join(parts[1:]).strip()
        detail_text = smart_render_text(detail_raw, width) if detail_raw else ""
        return brand_text, detail_text

    def catalog_secondary(item):
        explicit = item.get("catalog_description") or item.get("description_secondary") or item.get("descripcion")
        if explicit:
            return _safe_text(explicit)
        return _safe_text(catalog_lookup.get(catalog_name_key(item.get("description", "")), ""))

    # Columnas calibradas para llenar todo el ancho de contenido (suma == content_width).
    # UNIDAD y CANT. siempre quedan con el mismo ancho y texto centrado, asi se reparten
    # el espacio restante despues de la columna de descripcion.
    NUM_W = 8
    UNIT_QTY_W = 15  # ancho compartido por UNIDAD y CANT.; compacto para ampliar DESCRIPCION
    PRICE_W = 28     # ancho de P.UNIT/IMPORTE - suficiente para montos comunes en 10pt
    if with_prices:
        desc_w = content_width - (NUM_W + UNIT_QTY_W * 2 + PRICE_W * 2)
        cols = [NUM_W, desc_w, UNIT_QTY_W, UNIT_QTY_W, PRICE_W, PRICE_W]
        heads = ["#", "DESCRIPCIÓN", "UNIDAD", "CANT.", "P. UNIT.", "IMPORTE"]
        aligns = ["C", "L", "C", "C", "C", "C"]
    else:
        desc_w = content_width - (NUM_W + UNIT_QTY_W * 2)
        cols = [NUM_W, desc_w, UNIT_QTY_W, UNIT_QTY_W]
        heads = ["#", "DESCRIPCIÓN", "UNIDAD", "CANT."]
        aligns = ["C", "L", "C", "C"]

    def table_header():
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("DejaVu", "B", 8)
        for width, text, align in zip(cols, heads, aligns):
            pdf.cell(width, 7, text, fill=True, align=align)
        pdf.ln()

    def ensure_space(height, with_table_header=False):
        if pdf.get_y() + height <= (pdf.h - pdf.b_margin):
            return
        pdf.add_page()
        if with_table_header:
            table_header()

    # ----------------------------------------------------------- pagina 1
    # Layout unico: banner con logo + bloque de info + Detalle de partidas + tabla.
    # Las paginas siguientes usan el header estandar (project / numero / fecha).
    pdf.add_page()

    # Banner de portada (alto suficiente para que el logo quede centrado)
    BANNER_H = 56
    LOGO_W = 60
    LOGO_H = 40  # alto explicito para centrar verticalmente sin depender del ratio
    _ldm_portada_fill = _hex_to_rgb(_ldm_company_data.get("portada_color"), default=(0, 0, 0))
    pdf.set_fill_color(*_ldm_portada_fill)
    pdf.rect(0, 0, 210, BANNER_H, style="F")
    if logo_path:
        logo_x = (210 - LOGO_W) / 2
        logo_y = (BANNER_H - LOGO_H) / 2
        pdf.image(logo_path, x=logo_x, y=logo_y, w=LOGO_W, h=LOGO_H)
    else:
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(16, (BANNER_H - 8) / 2)
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(0, 8, _cached_company_name)

    # Bloque de info: PROYECTO / PROVEEDOR / FECHA (3 columnas, fondo SOFT)
    info_y = BANNER_H + 8
    pdf.set_fill_color(*SOFT)
    pdf.rect(pdf.l_margin, info_y, content_width, 20, style="F")

    # Padding interno y distribucion de columnas dentro del bloque
    inner_pad = 6
    inner_left = pdf.l_margin + inner_pad
    inner_right = pdf.l_margin + content_width - inner_pad
    inner_w = inner_right - inner_left
    col_w = [inner_w * 0.42, inner_w * 0.42, inner_w * 0.16]
    col_x = [inner_left, inner_left + col_w[0], inner_left + col_w[0] + col_w[1]]

    pdf.set_xy(col_x[0], info_y + 4)
    pdf.set_text_color(*MUTED)
    pdf.set_font("DejaVu", "B", 8)
    pdf.cell(col_w[0], 4, "PROYECTO")
    pdf.set_x(col_x[1])
    pdf.cell(col_w[1], 4, "PROVEEDOR")
    pdf.set_x(col_x[2])
    pdf.cell(col_w[2], 4, "FECHA")

    pdf.set_xy(col_x[0], info_y + 9)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "", 10.4)
    pdf.cell(col_w[0], 7, project_name)
    pdf.set_x(col_x[1])
    pdf.cell(col_w[1], 7, proveedor_name)
    pdf.set_x(col_x[2])
    pdf.cell(col_w[2], 7, ldm_date)

    # ----------------------------------------------------------- detalle
    pdf.set_xy(pdf.l_margin, info_y + 28)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 15)
    pdf.cell(content_width, 7, "Detalle de partidas", ln=True)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*MUTED)
    subtitle = f"{ldm_number} - " + ("Conceptos cotizados por el proveedor." if with_prices else "Conceptos solicitados al proveedor.")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(content_width, 4.5, subtitle)
    pdf.ln(2)

    table_header()
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "", 8.6)

    for item_index, item in enumerate(items, start=1):
        # 1. Smart render text con NBSP (atomos no-breakeables; fpdf2 solo
        #    parte en los espacios entre grupos / entre secciones de "|").
        secondary = catalog_secondary(item)

        # 2. Medir alturas reales con dry_run (fpdf2 puede repartir distinto a mi pre-wrap;
        #    asi tengo el conteo exacto de lineas que realmente va a renderizar).
        pdf.set_font("DejaVu", "B", 10)
        desc_text = smart_render_text(item.get("description", ""), cols[1] - 4)
        title_lines = pdf.multi_cell(cols[1] - 4, 5.0, desc_text, align="L",
                                     dry_run=True, output="LINES") if desc_text else []
        pdf.set_font("DejaVu", "", 7.5)
        brand_text, detail_text = split_secondary_render(secondary, cols[1] - 4)
        brand_lines = pdf.multi_cell(cols[1] - 4, 3.7, brand_text, align="L",
                                     dry_run=True, output="LINES") if brand_text else []
        title_h = 5.0 * len(title_lines)
        brand_h = 3.7 * len(brand_lines)
        text_h = 1.6 + title_h
        if brand_lines:
            text_h += 0.7 + brand_h
        row_h = max(14, text_h + 1.8)
        ensure_space(row_h, with_table_header=True)
        row_y = pdf.get_y()
        fill = (245, 247, 250) if item_index % 2 else (255, 255, 255)
        pdf.set_fill_color(*fill)
        pdf.set_draw_color(*LINE)
        pdf.rect(pdf.l_margin, row_y, sum(cols), row_h, style="FD")

        x = pdf.l_margin + cols[0]

        # Descripcion (titulo + marca + detalles) - render con align="L" y cursor real
        desc_x = x + 2
        desc_y = row_y + 1.3
        pdf.set_xy(desc_x, desc_y)
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(*INK)
        if desc_text:
            pdf.multi_cell(cols[1] - 4, 5.0, desc_text, align="L")
        if brand_text:
            pdf.set_xy(desc_x, pdf.get_y() + 0.7)
            pdf.set_font("DejaVu", "", 7.5)
            pdf.set_text_color(*NAVY_2)
            pdf.multi_cell(cols[1] - 4, 3.7, brand_text, align="L")
        x += cols[1]

        # Unidad
        pdf.set_xy(x, row_y)
        pdf.set_font("DejaVu", "", 10)  # datos numericos
        pdf.set_text_color(*INK)
        pdf.cell(cols[2], row_h, _safe_text(item.get("unit", "")), align="C")
        x += cols[2]

        # Cantidad (centrada para emparejar con UNIDAD)
        pdf.set_xy(x, row_y)
        try:
            qty_text = f"{float(item.get('qty', 0)):,.2f}"
        except Exception:
            qty_text = _safe_text(item.get("qty", ""))
        pdf.cell(cols[3], row_h, qty_text, align="C")
        x += cols[3]

        if with_prices:
            pdf.set_xy(x, row_y)
            pdf.cell(cols[4], row_h, money_pdf(item.get("precio_cot", 0)), align="C")
            x += cols[4]
            pdf.set_xy(x, row_y)
            pdf.set_font("DejaVu", "B", 10)  # importe (bold)
            pdf.cell(cols[5], row_h, money_pdf(item.get("total_cot", 0)), align="C")

        # Numero de fila centrado
        pdf.set_xy(pdf.l_margin, row_y + max((row_h - 5.5) / 2, 1))
        pdf.set_font("DejaVu", "B", 10)  # numero de fila
        pdf.set_text_color(*INK)
        pdf.cell(cols[0], 5.5, str(item_index), align="C")
        pdf.set_font("DejaVu", "", 8.6)
        pdf.set_y(row_y + row_h)

    # Subtotal cotizado (solo cuando hay precios)
    if with_prices:
        ensure_space(10)
        pdf.ln(2)
        label_width = sum(cols[:-1])
        value_width = cols[-1]
        pdf.set_draw_color(*LINE)
        pdf.set_text_color(*INK)
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(label_width, 7.5, "SUBTOTAL COTIZADO", border="T", align="R")
        pdf.set_text_color(*GREEN)
        pdf.cell(value_width, 7.5, money_pdf(ldm.get("subtotal_cot", 0)), border="T", align="R", ln=True)

    # Notas (opcional)
    notes = note_lines(ldm.get("notes"))
    if notes:
        ensure_space(8 + 5 * len(notes))
        pdf.ln(4)
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(*INK)
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(content_width, 6, "Notas", ln=True)
        pdf.set_font("DejaVu", "", 9.2)
        for line in notes:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(content_width, 5, _safe_text(f"- {line}"))

    if output_path:
        pdf.output(output_path)
    else:
        return bytes(pdf.output())


def build_progress_pdf(project, tmpl, output_path=None):
    """PDF de avance de obra: etapas con estado/presupuesto + checklist de documentos."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError("fpdf2 no instalado.") from exc

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 14, 15)
    pdf.add_page()

    has_fonts = _register_dejavu(pdf)
    font = "DejaVu" if has_fonts else "Helvetica"

    DARK  = _PDF_DARK
    LIGHT = _PDF_LIGHT
    MUTED = _PDF_MUTED2
    BLACK = _PDF_BLACK
    WHITE = _PDF_WHITE
    GREEN = _PDF_GREEN2

    # ── Encabezado ────────────────────────────────────────────────────────────
    logo = quote_logo_path()
    company = _company_name()
    cursor_y = 14
    logo_w = 0

    if logo:
        try:
            pdf.image(logo, x=15, y=cursor_y, h=14)
            logo_w = 36
        except Exception:
            logo_w = 0

    pdf.set_xy(15 + logo_w, cursor_y)
    pdf.set_font(font, "B", 13)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 7, _safe_text(company), ln=True)
    pdf.set_x(15 + logo_w)
    pdf.set_font(font, "", 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, "Reporte de Avance de Obra", ln=True)
    pdf.set_text_color(*BLACK)
    pdf.ln(5)

    # ── Datos del proyecto ────────────────────────────────────────────────────
    pdf.set_font(font, "B", 11)
    pdf.cell(0, 6, _safe_text(project.get("name", "")), ln=True)
    pdf.set_font(font, "", 8.5)
    pdf.set_text_color(*MUTED)
    meta = []
    if project.get("client"):
        meta.append(f"Cliente: {project['client']}")
    if project.get("clave"):
        meta.append(f"Clave: {project['clave']} {project.get('version', '')}".strip())
    if project.get("deadline"):
        meta.append(f"Deadline: {format_date_long(project['deadline'])}")
    meta.append(f"Reporte: {format_date_long(today())}")
    pdf.cell(0, 5, "   ".join(meta), ln=True)
    pdf.set_text_color(*BLACK)
    pdf.ln(6)

    # ── Etapas ────────────────────────────────────────────────────────────────
    if tmpl:
        stage_status = project.get("stage_status") or {}
        stage_budget = project.get("stage_budget") or {}

        pdf.set_fill_color(*DARK)
        pdf.set_text_color(*WHITE)
        pdf.set_font(font, "B", 9)
        pdf.cell(0, 7, "  Etapas del Proyecto", fill=True, ln=True)
        pdf.set_text_color(*BLACK)
        pdf.ln(1)

        col = [58, 34, 34, 32, 32]
        pdf.set_font(font, "B", 7.5)
        pdf.set_fill_color(*LIGHT)
        for w, h in zip(col, ["Etapa", "Estado", "Fecha", "Planeado", "Ejercido"]):
            pdf.cell(w, 6, h, border=1, fill=True)
        pdf.ln()

        total_planned = total_actual = 0.0
        pdf.set_font(font, "", 8)
        for i, stage in enumerate(tmpl["stages"]):
            row_fill = (248, 251, 255) if i % 2 == 0 else WHITE
            pdf.set_fill_color(*row_fill)
            st   = stage_status.get(stage, {})
            slbl = STAGE_STATUS_LABELS.get(st.get("status", "pending"), "Pendiente")
            sdt  = format_date_long(st.get("date")) if st.get("date") else "-"
            bdg  = stage_budget.get(stage, {})
            pln  = float(bdg.get("planned", 0) or 0)
            act  = float(bdg.get("actual",  0) or 0)
            total_planned += pln
            total_actual  += act
            pdf.cell(col[0], 5.5, _safe_text(stage),              border=1, fill=True)
            pdf.cell(col[1], 5.5, slbl,                            border=1, fill=True)
            pdf.cell(col[2], 5.5, sdt,                             border=1, fill=True)
            pdf.cell(col[3], 5.5, f"${pln:,.0f}" if pln else "-",  border=1, fill=True)
            pdf.cell(col[4], 5.5, f"${act:,.0f}" if act else "-",  border=1, fill=True)
            pdf.ln()

        if total_planned or total_actual:
            pdf.set_fill_color(*LIGHT)
            pdf.set_font(font, "B", 8)
            pdf.cell(col[0]+col[1]+col[2], 6, "Total", border=1, fill=True)
            pdf.cell(col[3], 6, f"${total_planned:,.0f}", border=1, fill=True)
            pdf.cell(col[4], 6, f"${total_actual:,.0f}",  border=1, fill=True)
            pdf.ln()

        pdf.ln(6)

    # ── Documentos requeridos ─────────────────────────────────────────────────
    docs = project.get("docs_checklist") or []
    if docs:
        pdf.set_fill_color(*DARK)
        pdf.set_text_color(*WHITE)
        pdf.set_font(font, "B", 9)
        pdf.cell(0, 7, "  Documentos Requeridos", fill=True, ln=True)
        pdf.set_text_color(*BLACK)
        pdf.ln(2)

        done_count = sum(1 for d in docs if d.get("done"))
        pdf.set_font(font, "", 8.5)
        for doc in docs:
            mark = "[X]" if doc.get("done") else "[ ]"
            pdf.set_text_color(*(GREEN if doc.get("done") else MUTED))
            pdf.cell(0, 5.5, f"  {mark}  {_safe_text(doc.get('name', ''))}", ln=True)
        pdf.set_text_color(*MUTED)
        pdf.set_font(font, "I", 8)
        pdf.ln(1)
        pdf.cell(0, 5, f"Progreso: {done_count}/{len(docs)} documentos entregados", ln=True)
        pdf.set_text_color(*BLACK)

    if output_path:
        pdf.output(output_path)
    else:
        return bytes(pdf.output())
