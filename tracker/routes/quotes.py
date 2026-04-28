import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..catalog import catalog_maps, hydrate_quote, next_quote_number, quote_type_key, safe_float
from ..deletions import purge_deleted_catalog_items_from_record
from ..drive import folder_name, latest_dwg_stem, load_config
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
    root = cfg.get("drive_projects_path", "")
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
