import os

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..catalog import catalog_maps, hydrate_quote, next_quote_number, quote_type_key
from ..drive import folder_name, load_config
from ..pdfs import build_quote_pdf
from ..storage import load, new_id, save, today
from ..validators import validate_quote_form

bp = Blueprint("quotes_bp", __name__)


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
            return redirect(url_for("quotes_bp.new_quote", project_id=project_id))
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
            "created_at": today(),
        }
        quotes.append(quote)
        save("quotes", quotes)
        flash(f"Cotización {quote['quote_number']} creada.", "success")
        return redirect(url_for("quotes_bp.edit_quote", project_id=project_id, quote_id=quote["id"]))
    general_quotes = [quote for quote in quotes if quote["project_id"] == project_id and quote_type_key(quote.get("quote_type")) == "General"]
    preliminary_quotes = [quote for quote in quotes if quote["project_id"] == project_id and quote_type_key(quote.get("quote_type")) == "Preliminar"]
    extraordinary_quotes = [quote for quote in quotes if quote["project_id"] == project_id and quote_type_key(quote.get("quote_type")) == "Extraordinaria"]
    today_str = today()
    date_token = today_str.replace("-", "")
    default_num_g = f"COT-{project['clave']}-G{len(general_quotes) + 1:02d}-{date_token}"
    default_num_p = f"COT-{project['clave']}-P{len(preliminary_quotes) + 1:02d}-{date_token}"
    default_num_e = f"COT-{project['clave']}-E{len(extraordinary_quotes) + 1:02d}-{date_token}"
    return render_template(
        "quote_project_form.html",
        project=project,
        quote=None,
        today=today_str,
        default_num_g=default_num_g,
        default_num_p=default_num_p,
        default_num_e=default_num_e,
    )


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
            return redirect(url_for("quotes_bp.edit_quote", project_id=project_id, quote_id=quote_id))
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
        })
        save("quotes", quotes)
        flash("Cotización actualizada.", "success")
        return redirect(url_for("quotes_bp.edit_quote", project_id=project_id, quote_id=quote_id))
    other_quotes = [item for item in quotes if item["id"] != quote_id]
    general_quotes = [item for item in other_quotes if item["project_id"] == project_id and quote_type_key(item.get("quote_type")) == "General"]
    preliminary_quotes = [item for item in other_quotes if item["project_id"] == project_id and quote_type_key(item.get("quote_type")) == "Preliminar"]
    extraordinary_quotes = [item for item in other_quotes if item["project_id"] == project_id and quote_type_key(item.get("quote_type")) == "Extraordinaria"]
    date_token = today().replace("-", "")
    default_num_g = f"COT-{project['clave']}-G{len(general_quotes) + 1:02d}-{date_token}"
    default_num_p = f"COT-{project['clave']}-P{len(preliminary_quotes) + 1:02d}-{date_token}"
    default_num_e = f"COT-{project['clave']}-E{len(extraordinary_quotes) + 1:02d}-{date_token}"
    hydrated = hydrate_quote(quote, *catalog_maps())
    return render_template(
        "quote_project_form.html",
        project=project,
        quote=hydrated,
        today=today(),
        default_num_g=default_num_g,
        default_num_p=default_num_p,
        default_num_e=default_num_e,
    )


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
    try:
        build_quote_pdf(project, hydrated, pdf_path)
        flash(f"PDF generado en Drive: {pdf_name}", "success")
    except Exception as exc:
        flash(f"Error al generar PDF: {exc}", "danger")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-quote")
