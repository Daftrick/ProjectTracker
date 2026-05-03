import os
import re
from datetime import date, datetime

from .catalog import catalog_description_lookup, catalog_name_key, quote_section_groups, quote_type_key
from .storage import BASE_DIR


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
    """Registra las fuentes DejaVu guardadas en .codex_tmp/fonts/ del proyecto.
    Devuelve False si no estan disponibles para que el caller falle con un error claro."""
    font_dir = os.path.join(BASE_DIR, ".codex_tmp", "fonts")
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


def quote_logo_path():
    candidates = [
        r"H:\My Drive\Omniious\OmnniiousLog.jpg",
        os.path.join(BASE_DIR, ".codex_tmp", "casa_leonides_pdf_assets", "page_1_img_1_Im6.jpg"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


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
    match = re.search(r"-[GPE](\d{2,})(?:-|$)", str(quote_number or ""))
    return match.group(1) if match else ""


def quote_cover_copy(quote):
    quote_type = quote_type_key(quote.get("quote_type"))
    if quote_type == "Preliminar":
        return "Cotización Preliminar de\nInstalaciones Eléctricas", None
    if quote_type == "Extraordinaria":
        sequence = quote_sequence_from_number(quote.get("quote_number"))
        subtitle = f"Número secuencial de cotización {sequence}" if sequence else "Número secuencial de cotización"
        return "Cotización Extraordinaria de\nInstalaciones Eléctricas", subtitle
    return "Cotización de Instalaciones\nEléctricas", None


def quote_project_basis_note(quote):
    quote_type = quote_type_key(quote.get("quote_type"))
    if quote_type == "Preliminar":
        return ""
    if quote_type == "General":
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


def build_quote_pdf(project, quote, output_path):
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
            self.set_font(FONT, "B", 11)
            self.set_text_color(*NAVY)
            self.cell(cw * 0.57, 6, _safe_text(self.project_name))
            self.set_font(FONT, "", 8.5)
            self.set_text_color(*MUTED)
            self.cell(cw * 0.23, 6, _safe_text(self.quote_number), align="C")
            self.cell(cw * 0.20, 6, _safe_text(self.quote_date), align="R")
            self.ln(10)

        def footer(self):
            left = self.l_margin
            right = self.w - self.r_margin
            self.set_y(-13)
            self.set_draw_color(*LINE)
            self.line(left, self.get_y() - 1.5, right, self.get_y() - 1.5)
            self.set_font(FONT, "", 8)
            self.set_text_color(*MUTED)
            self.cell(0, 5, _safe_text(f"Project Tracker - Página {self.page_no()}/{{nb}}"), align="C")

    NAVY = (24, 39, 70)
    NAVY_2 = (40, 63, 110)
    INK = (37, 44, 58)
    MUTED = (113, 126, 145)
    LINE = (215, 221, 230)
    SOFT = (244, 247, 251)
    GREEN = (34, 139, 94)

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
        pdf.set_font("DejaVu", "B", 15)
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
        pdf.cell(line_w, 4.5, "Omniious Technologies", align="C")

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

    pdf.add_page()
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(0, 0, 210, 112, style="F")
    if logo_path:
        pdf.image(logo_path, x=48, y=12, w=114)
    else:
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(16, 28)
        pdf.set_font("DejaVu", "B", 18)
        pdf.cell(0, 8, "OMNIIOUS TECHNOLOGIES")
    pdf.set_draw_color(*LINE)
    pdf.line(16, 128, 194, 128)
    pdf.set_xy(16, 138)
    pdf.set_text_color(*NAVY)
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(0, 5, "PROPUESTA ECONÓMICA")
    pdf.set_xy(16, 148)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 23)
    pdf.multi_cell(158, 9.5, _safe_text(cover_title))
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
    proposal_y = max(178, pdf.get_y() + 7)
    pdf.set_xy(16, proposal_y)
    pdf.set_text_color(*MUTED)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, "Propuesta para")
    pdf.set_xy(16, proposal_y + 9)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 19)
    pdf.multi_cell(112, 8.5, client_name)
    summary_x = 16
    summary_y = 221
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
    info_value(project_name, ln=True)

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

    pdf.add_page()
    pdf.set_y(22)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 17)
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

    pdf.output(output_path)


def build_ldm_pdf(project, ldm, output_path):
    """Genera el PDF de una Lista de Materiales con la estética del PDF de
    cotizaciones (banner negro + logo, paleta navy/ink/muted, tabla de partidas)
    pero en una version simplificada: solo encabezado con proyecto/proveedor/fecha
    y tabla de items. Sin alcance, sin terminos, sin firma.
    """
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError("fpdf2 no instalado. Ejecuta: pip install fpdf2 --break-system-packages") from exc

    NAVY = (24, 39, 70)
    NAVY_2 = (40, 63, 110)
    INK = (37, 44, 58)
    MUTED = (113, 126, 145)
    LINE = (215, 221, 230)
    SOFT = (244, 247, 251)
    GREEN = (34, 139, 94)

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
            self.cell(0, 5, _safe_text(f"Project Tracker - Página {self.page_no()}/{{nb}}"), align="C")

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

    # Banner negro con logo (alto suficiente para que el logo quede centrado)
    BANNER_H = 56
    LOGO_W = 60
    LOGO_H = 40  # alto explicito para centrar verticalmente sin depender del ratio
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(0, 0, 210, BANNER_H, style="F")
    if logo_path:
        logo_x = (210 - LOGO_W) / 2
        logo_y = (BANNER_H - LOGO_H) / 2
        pdf.image(logo_path, x=logo_x, y=logo_y, w=LOGO_W, h=LOGO_H)
    else:
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(16, (BANNER_H - 8) / 2)
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(0, 8, "OMNIIOUS TECHNOLOGIES")

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
        if detail_text:
            pdf.set_xy(desc_x, pdf.get_y() + 0.3)
            pdf.set_font("DejaVu", "", 7.5)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(cols[1] - 4, 3.7, detail_text, align="L")
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

    pdf.output(output_path)
