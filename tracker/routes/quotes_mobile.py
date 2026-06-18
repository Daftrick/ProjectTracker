import os
import tempfile

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from ..catalog import catalog_maps, hydrate_quote
from ..pdfs import build_quote_pdf
from ..services import (
    filter_catalog_by_disciplina,
    finalize_mobile_draft,
    remove_item_from_draft,
    upsert_mobile_draft,
)
from ..storage import load, save

bp = Blueprint("quotes_mobile_bp", __name__, url_prefix="/cotizar/mobile")


def _find_project(project_id):
    return next((p for p in load("projects") if p["id"] == project_id), None)


def _find_draft(quotes, project_id):
    return next(
        (q for q in quotes if q.get("project_id") == project_id and q.get("status") == "draft"),
        None,
    )


def _discipline_list(catalog):
    seen = []
    for item in catalog:
        d = item.get("disciplina", "")
        if d and d not in seen:
            seen.append(d)
    return seen


# ---------------------------------------------------------------------------
# Paso 1 — Selección de proyecto
# ---------------------------------------------------------------------------

@bp.route("/", endpoint="mobile_projects")
def mobile_projects():
    projects = [p for p in load("projects") if not p.get("closed_at")]
    quotes = load("quotes")
    draft_by_project = {
        q["project_id"]: q for q in quotes if q.get("status") == "draft"
    }
    return render_template(
        "mobile_projects.html",
        projects=projects,
        draft_by_project=draft_by_project,
    )


# ---------------------------------------------------------------------------
# Paso 2 — Agregar ítems al borrador
# ---------------------------------------------------------------------------

@bp.route("/<project_id>/items", endpoint="mobile_items")
def mobile_items(project_id):
    project = _find_project(project_id)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("quotes_mobile_bp.mobile_projects"))

    quotes = load("quotes")
    draft = _find_draft(quotes, project_id)

    if request.args.get("nueva") == "1" and draft:
        updated = [q for q in quotes if not (q.get("project_id") == project_id and q.get("status") == "draft")]
        save("quotes", updated)
        draft = None
        return redirect(url_for("quotes_mobile_bp.mobile_items", project_id=project_id))

    catalog_all = load("catalogo")
    disciplina = request.args.get("disciplina") or "Todos"
    filtered = filter_catalog_by_disciplina(catalog_all, disciplina if disciplina != "Todos" else None)
    disciplinas = ["Todos"] + _discipline_list(catalog_all)

    item_ids_in_draft = {i["catalog_item_id"] for i in (draft["items"] if draft else [])}

    return render_template(
        "mobile_items.html",
        project=project,
        draft=draft,
        catalog=filtered,
        disciplinas=disciplinas,
        active_disciplina=disciplina,
        item_ids_in_draft=item_ids_in_draft,
    )


@bp.route("/<project_id>/items", methods=["POST"], endpoint="mobile_add_item")
def mobile_add_item(project_id):
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("quotes_mobile_bp.mobile_projects"))

    item_id = request.form.get("item_id", "").strip()
    try:
        qty = float(request.form.get("qty", "1") or "1")
    except ValueError:
        qty = 1.0

    if item_id:
        catalog_by_id, _ = catalog_maps()
        quotes = load("quotes")
        updated, _ = upsert_mobile_draft(quotes, project, catalog_by_id, item_id, qty)
        save("quotes", updated)

    disciplina = request.form.get("disciplina", "")
    redirect_url = url_for("quotes_mobile_bp.mobile_items", project_id=project_id)
    if disciplina and disciplina != "Todos":
        redirect_url += f"?disciplina={disciplina}"
    return redirect(redirect_url)


# ---------------------------------------------------------------------------
# Remove item
# ---------------------------------------------------------------------------

@bp.route("/<project_id>/remove_item", methods=["POST"], endpoint="mobile_remove_item")
def mobile_remove_item(project_id):
    item_id = request.form.get("item_id", "").strip()
    if item_id:
        quotes = load("quotes")
        updated, _ = remove_item_from_draft(quotes, project_id, item_id)
        save("quotes", updated)
    return redirect(url_for("quotes_mobile_bp.mobile_review", project_id=project_id))


# ---------------------------------------------------------------------------
# Paso 3 — Revisión del borrador
# ---------------------------------------------------------------------------

@bp.route("/<project_id>/review", endpoint="mobile_review")
def mobile_review(project_id):
    project = _find_project(project_id)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("quotes_mobile_bp.mobile_projects"))

    quotes = load("quotes")
    draft = _find_draft(quotes, project_id)
    if not draft:
        flash("No hay borrador activo para este proyecto.", "warning")
        return redirect(url_for("quotes_mobile_bp.mobile_items", project_id=project_id))

    return render_template("mobile_review.html", project=project, draft=draft)


# ---------------------------------------------------------------------------
# Paso 4 — Generar PDF
# ---------------------------------------------------------------------------

@bp.route("/<project_id>/generate_pdf", methods=["POST"], endpoint="mobile_generate_pdf")
def mobile_generate_pdf(project_id):
    project = _find_project(project_id)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("quotes_mobile_bp.mobile_projects"))

    quotes = load("quotes")
    draft = _find_draft(quotes, project_id)
    if not draft:
        flash("No hay borrador activo.", "warning")
        return redirect(url_for("quotes_mobile_bp.mobile_items", project_id=project_id))

    updated, finalized = finalize_mobile_draft(quotes, project, draft["id"])
    if not finalized:
        flash("No se pudo finalizar el borrador.", "danger")
        return redirect(url_for("quotes_mobile_bp.mobile_review", project_id=project_id))

    save("quotes", updated)

    catalog_by_id, catalog_by_name = catalog_maps()
    hydrated = hydrate_quote(finalized, catalog_by_id, catalog_by_name)

    pdf_name = f"{hydrated.get('quote_number', 'COT')}.pdf"

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        build_quote_pdf(project, hydrated, tmp_path)
        import io
        with open(tmp_path, "rb") as f:
            pdf_bytes = io.BytesIO(f.read())
        pdf_bytes.seek(0)
        return send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=pdf_name,
        )
    except Exception as exc:
        flash(f"Error al generar PDF: {exc}", "danger")
        return redirect(url_for("quotes_mobile_bp.mobile_review", project_id=project_id))
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
