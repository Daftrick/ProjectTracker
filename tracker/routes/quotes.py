import io
import os

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from ..catalog import catalog_maps, hydrate_quote, next_quote_number, quote_type_key, safe_float
from ..deletions import purge_deleted_catalog_items_from_record
from ..drive import active_drive_paths, folder_name, latest_dwg_stem, load_config
from ..form_models import quote_default_numbers, quote_from_form
from ..pdfs import build_quote_pdf
from ..storage import load, new_id, save, today
from ..validators import validate_quote_form

bp = Blueprint("quotes_bp", __name__)


def _render_quote_form(project, quote, quotes, field_errors=None, quote_id=None):
    return render_template(
        "quote_project_form.html",
        project=project,
        quote=quote,
        today=today(),
        field_errors=field_errors or {},
        **quote_default_numbers(project, quotes, quote_id=quote_id),
    )


@bp.route("/projects/<project_id>/quote/new", methods=["GET", "POST"], endpoint="new_quote")
def new_quote(project_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    quotes = load("quotes")
    if request.method == "POST":
        validation = validate_quote_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return _render_quote_form(
                project,
                quote_from_form(request.form),
                quotes,
                field_errors=validation["field_errors"],
            )
        quote_type = validation["quote_type"]
        date_str = validation["date"]
        quote_number = request.form.get("quote_number", "").strip() or next_quote_number(project, quotes, quote_type, date_str)
        quote = {
            "id": new_id(),
            "project_id": project_id,
            "quote_number": quote_number,
            "quote_type": quote_type,
            "version": validation["version"],
            "client": project.get("client", ""),
            "project_name": project.get("name", ""),
            "date": date_str,
            "valid_until": validation["valid_until"],
            "items": validation["items"],
            "subtotal": validation["subtotal"],
            "tax_rate": validation["tax_rate"],
            "tax": round(validation["subtotal"] * validation["tax_rate"] / 100, 2),
            "total": round(validation["subtotal"] + validation["subtotal"] * validation["tax_rate"] / 100, 2),
            "currency": validation["currency"],
            "notes": validation["notes"],
            "project_basis_note": validation["project_basis_note"] if quote_type == "Extraordinaria" else "",
            "created_at": today(),
        }
        quotes.append(quote)
        save("quotes", quotes)
        flash(f"Cotización {quote['quote_number']} creada.", "success")
        return redirect(url_for("quotes_bp.edit_quote", project_id=project_id, quote_id=quote["id"]))
    return _render_quote_form(project, None, quotes)


@bp.route("/projects/<project_id>/quote/<quote_id>/edit", methods=["GET", "POST"], endpoint="edit_quote")
def edit_quote(project_id, quote_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    quotes = load("quotes")
    quote = next((item for item in quotes if item["id"] == quote_id), None)
    if not project or not quote:
        return redirect(url_for("project_detail", project_id=project_id))
    if request.method == "POST":
        validation = validate_quote_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return _render_quote_form(
                project,
                quote_from_form(request.form, fallback_quote=quote),
                quotes,
                field_errors=validation["field_errors"],
                quote_id=quote_id,
            )
        quote.update({
            "quote_number": validation["quote_number"] or quote["quote_number"],
            "quote_type": validation["quote_type"],
            "version": validation["version"],
            "date": validation["date"],
            "valid_until": validation["valid_until"],
            "items": validation["items"],
            "subtotal": validation["subtotal"],
            "tax_rate": validation["tax_rate"],
            "tax": round(validation["subtotal"] * validation["tax_rate"] / 100, 2),
            "total": round(validation["subtotal"] + validation["subtotal"] * validation["tax_rate"] / 100, 2),
            "currency": validation["currency"],
            "notes": validation["notes"],
            "project_basis_note": validation["project_basis_note"] if validation["quote_type"] == "Extraordinaria" else "",
        })
        save("quotes", quotes)
        flash("Cotización actualizada.", "success")
        return redirect(url_for("quotes_bp.edit_quote", project_id=project_id, quote_id=quote_id))
    hydrated = hydrate_quote(quote, *catalog_maps())
    return _render_quote_form(project, hydrated, quotes, quote_id=quote_id)


@bp.route("/projects/<project_id>/quote/<quote_id>/view", endpoint="view_quote")
def view_quote(project_id, quote_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    quote = next((item for item in load("quotes") if item["id"] == quote_id), None)
    if not project or not quote or quote.get("project_id") != project_id:
        flash("Cotización no encontrada.", "danger")
        if project:
            return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")
        return redirect(url_for("dashboard"))
    hydrated = hydrate_quote(quote, *catalog_maps())
    return render_template("quote_project_detail.html", project=project, quote=hydrated)


@bp.route("/projects/<project_id>/quote/<quote_id>/delete", methods=["POST"], endpoint="delete_quote")
def delete_quote(project_id, quote_id):
    save("quotes", [item for item in load("quotes") if item["id"] != quote_id])
    flash("Cotización eliminada.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")


@bp.route(
    "/projects/<project_id>/quote/<quote_id>/purge-deleted-catalog",
    methods=["POST"],
    endpoint="purge_quote_deleted_catalog_items",
)
def purge_quote_deleted_catalog_items(project_id, quote_id):
    quotes = load("quotes")
    quote = next((item for item in quotes if item["id"] == quote_id and item["project_id"] == project_id), None)
    if not quote:
        flash("Cotización no encontrada.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")

    updated_quote, removed = purge_deleted_catalog_items_from_record(quote)
    subtotal = round(
        sum(safe_float(item.get("qty", 0)) * safe_float(item.get("price", 0)) for item in updated_quote.get("items", [])),
        2,
    )
    tax_rate = safe_float(updated_quote.get("tax_rate", 16), 16)
    updated_quote["subtotal"] = subtotal
    updated_quote["tax"] = round(subtotal * tax_rate / 100, 2)
    updated_quote["total"] = round(subtotal + updated_quote["tax"], 2)
    quote.update(updated_quote)
    save("quotes", quotes)
    flash(f"Se eliminaron {removed} partida(s) con catálogo eliminado de la cotización.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")


@bp.route("/projects/<project_id>/quote/<quote_id>/pdf", endpoint="quote_pdf")
def quote_pdf(project_id, quote_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    quote = next((item for item in load("quotes") if item["id"] == quote_id), None)
    if not project or not quote:
        flash("Cotización no encontrada.", "danger")
        return redirect(url_for("dashboard"))
    hydrated = hydrate_quote(quote, *catalog_maps())
    cfg = load_config()
    root = active_drive_paths(cfg)["projects"]
    drive_folder = folder_name(project)
    project_folder = os.path.join(root, drive_folder) if root else None
    if not project_folder or not os.path.isdir(project_folder):
        flash("Carpeta del proyecto no encontrada en Drive. Verifica Ajustes.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")
    pdf_name = f"{hydrated.get('quote_number', 'COT')}.pdf"
    pdf_path = os.path.join(project_folder, pdf_name)
    if quote_type_key(hydrated.get("quote_type")) == "General":
        hydrated["project_basis_source"] = latest_dwg_stem(project_folder)
    try:
        build_quote_pdf(project, hydrated, pdf_path)
        flash(f"PDF generado en Drive: {pdf_name}", "success")
    except Exception as exc:
        flash(f"Error al generar PDF: {exc}", "danger")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")


@bp.route("/projects/<project_id>/quote/<quote_id>/excel", endpoint="quote_excel")
def quote_excel(project_id, quote_id):
    """Genera y descarga la cotización como archivo Excel (.xlsx)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    project = next((item for item in load("projects") if item["id"] == project_id), None)
    quote = next((item for item in load("quotes") if item["id"] == quote_id), None)
    if not project or not quote:
        flash("Cotización no encontrada.", "danger")
        return redirect(url_for("dashboard"))
    hydrated = hydrate_quote(quote, *catalog_maps())
    sections = hydrated.get("sections", [])
    has_sections = any(section.get("name") for section in sections)

    wb = Workbook()
    ws = wb.active
    ws.title = "Cotización"

    # Ajustar anchos de columna
    ws.column_dimensions["A"].width = 5    # #
    if has_sections:
        ws.column_dimensions["B"].width = 24   # Sección
        ws.column_dimensions["C"].width = 40   # Nombre / Descripción
        ws.column_dimensions["D"].width = 10   # Unidad
        ws.column_dimensions["E"].width = 12   # Cantidad
        ws.column_dimensions["F"].width = 16   # Precio unitario
        ws.column_dimensions["G"].width = 16   # Total
    else:
        ws.column_dimensions["B"].width = 40   # Nombre / Descripción
        ws.column_dimensions["C"].width = 10   # Unidad
        ws.column_dimensions["D"].width = 12   # Cantidad
        ws.column_dimensions["E"].width = 16   # Precio unitario
        ws.column_dimensions["F"].width = 16   # Total

    # ── Encabezado informativo ──────────────────────────────────────────────
    ws.append(["Cotización:", hydrated.get("quote_number", "")])
    ws.append(["Cliente:", hydrated.get("client", "")])
    ws.append(["Proyecto:", hydrated.get("project_name", "")])
    ws.append(["Fecha:", hydrated.get("date", "")])
    ws.append(["Moneda:", hydrated.get("currency", "")])
    ws.append([])  # fila vacía

    # ── Cabecera de tabla ───────────────────────────────────────────────────
    header_row = (
        ["#", "Sección", "Nombre", "Unidad", "Cantidad", "Precio unitario", "Total"]
        if has_sections
        else ["#", "Nombre", "Unidad", "Cantidad", "Precio unitario", "Total"]
    )
    ws.append(header_row)
    hdr_idx = ws.max_row
    total_col = 7 if has_sections else 6
    price_col = 6 if has_sections else 5
    qty_col = 5 if has_sections else 4
    section_label_col = 3 if has_sections else 2
    subtotal_label_col = 6 if has_sections else 5
    for col in range(1, total_col + 1):
        cell = ws.cell(row=hdr_idx, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ── Artículos ───────────────────────────────────────────────────────────
    row_num = 0
    currency = hydrated.get("currency", "")
    for section in sections:
        if section.get("name"):
            section_row = [""] * total_col
            section_row[section_label_col - 1] = section["name"]
            ws.append(section_row)
            sect_cell = ws.cell(row=ws.max_row, column=section_label_col)
            sect_cell.font = Font(bold=True)

        for item in section.get("items", []):
            row_num += 1
            qty = item.get("qty", 0)
            price = item.get("price", 0)
            total = item.get("total", 0)
            if has_sections:
                ws.append([
                    row_num,
                    section.get("name", ""),
                    item.get("description", ""),
                    item.get("unit", ""),
                    qty,
                    price,
                    total,
                ])
            else:
                ws.append([
                    row_num,
                    item.get("description", ""),
                    item.get("unit", ""),
                    qty,
                    price,
                    total,
                ])
            # Alinear números
            r = ws.max_row
            ws.cell(row=r, column=qty_col).alignment = Alignment(horizontal="right")
            ws.cell(row=r, column=price_col).alignment = Alignment(horizontal="right")
            ws.cell(row=r, column=total_col).alignment = Alignment(horizontal="right")
            ws.cell(row=r, column=price_col).number_format = "#,##0.00"
            ws.cell(row=r, column=total_col).number_format = "#,##0.00"

        if section.get("name"):
            subtotal_row = [""] * total_col
            subtotal_row[section_label_col - 1] = f"Subtotal {section['name']}"
            subtotal_row[total_col - 1] = section.get("subtotal", 0)
            ws.append(subtotal_row)
            sr = ws.max_row
            ws.cell(row=sr, column=section_label_col).font = Font(bold=True)
            ws.cell(row=sr, column=total_col).number_format = "#,##0.00"
            ws.cell(row=sr, column=total_col).alignment = Alignment(horizontal="right")

    # ── Fila vacía de separación ────────────────────────────────────────────
    ws.append([])

    # ── Totales ─────────────────────────────────────────────────────────────
    subtotal = hydrated.get("subtotal", 0)
    tax_rate = hydrated.get("tax_rate", 0)
    tax = hydrated.get("tax", 0)
    total = hydrated.get("total", 0)

    for label, value in [
        ("Subtotal", subtotal),
        (f"IVA ({tax_rate}%)", tax),
        ("TOTAL", total),
    ]:
        total_row = [""] * total_col
        total_row[subtotal_label_col - 1] = label
        total_row[total_col - 1] = value
        ws.append(total_row)
        r = ws.max_row
        ws.cell(row=r, column=subtotal_label_col).font = Font(bold=True)
        ws.cell(row=r, column=subtotal_label_col).alignment = Alignment(horizontal="right")
        ws.cell(row=r, column=total_col).number_format = "#,##0.00"
        ws.cell(row=r, column=total_col).alignment = Alignment(horizontal="right")
        if label == "TOTAL":
            ws.cell(row=r, column=subtotal_label_col).font = Font(bold=True)
            ws.cell(row=r, column=total_col).font = Font(bold=True)

    # ── Serializar y enviar ─────────────────────────────────────────────────
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"{hydrated.get('quote_number', 'cotizacion')}.xlsx"
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )
