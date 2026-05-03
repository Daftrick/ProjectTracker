from .storage import today


def delete_project_data(project_id, projects, tasks, deliveries, quotes, materiales, fichas):
    remaining_projects = [item for item in projects if item.get("id") != project_id]
    remaining_tasks = [item for item in tasks if item.get("project_id") != project_id]
    remaining_deliveries = [item for item in deliveries if item.get("project_id") != project_id]
    remaining_quotes = [item for item in quotes if item.get("project_id") != project_id]
    remaining_materiales = [item for item in materiales if item.get("project_id") != project_id]
    cleaned_fichas = []
    ficha_refs_removed = 0

    for ficha in fichas:
        updated = dict(ficha)
        before = list(updated.get("projects", []) or [])
        after = [item for item in before if item != project_id]
        ficha_refs_removed += len(before) - len(after)
        updated["projects"] = after
        cleaned_fichas.append(updated)

    return {
        "projects": remaining_projects,
        "tasks": remaining_tasks,
        "deliveries": remaining_deliveries,
        "quotes": remaining_quotes,
        "materiales": remaining_materiales,
        "fichas": cleaned_fichas,
        "counts": {
            "projects": len(projects) - len(remaining_projects),
            "tasks": len(tasks) - len(remaining_tasks),
            "deliveries": len(deliveries) - len(remaining_deliveries),
            "quotes": len(quotes) - len(remaining_quotes),
            "materiales": len(materiales) - len(remaining_materiales),
            "ficha_refs": ficha_refs_removed,
        },
    }

def delete_catalog_items_data(item_ids, catalogo, quotes, materiales, today_value=None):
    ids = {str(item_id).strip() for item_id in item_ids}
    deleted_at = today_value or today()
    deleted_items = {
        str(item.get("id", "")).strip(): {
            "id": str(item.get("id", "")).strip(),
            "nombre": item.get("nombre", ""),
            "descripcion": item.get("descripcion", ""),
            "unidad": item.get("unidad", ""),
            "precio": item.get("precio", 0),
            "deleted_at": deleted_at,
        }
        for item in catalogo
        if str(item.get("id", "")).strip() in ids
    }
    remaining_catalogo = [item for item in catalogo if str(item.get("id", "")).strip() not in ids]
    cleaned_quotes, quote_refs = _mark_deleted_catalog_refs(quotes, deleted_items)
    cleaned_materiales, material_refs = _mark_deleted_catalog_refs(materiales, deleted_items)

    return {
        "catalogo": remaining_catalogo,
        "quotes": cleaned_quotes,
        "materiales": cleaned_materiales,
        "counts": {
            "catalogo": len(catalogo) - len(remaining_catalogo),
            "quote_refs": quote_refs,
            "material_refs": material_refs,
        },
    }


def purge_deleted_catalog_items_from_record(record):
    updated = dict(record)
    before = list(updated.get("items", []) or [])
    updated["items"] = [item for item in before if not item.get("deleted_catalog_item")]
    return updated, len(before) - len(updated["items"])


def restore_deleted_catalog_item_in_record(record, item_index, new_catalog_id):
    """Reconnect a deleted catalog item to a new catalog item"""
    updated = dict(record)
    items = list(updated.get("items", []) or [])

    if 0 <= item_index < len(items):
        item = dict(items[item_index])
        if item.get("deleted_catalog_item"):
            # Remove the deleted catalog item reference and set new catalog ID
            item.pop("deleted_catalog_item", None)
            item["catalog_item_id"] = str(new_catalog_id).strip()
            items[item_index] = item
            updated["items"] = items
            return updated, True

    return updated, False


def preserve_deleted_catalog_item_in_record(record, item_index):
    """Mark a deleted catalog item as preserved (keep historical reference)"""
    updated = dict(record)
    items = list(updated.get("items", []) or [])

    if 0 <= item_index < len(items):
        item = dict(items[item_index])
        if item.get("deleted_catalog_item"):
            # Mark as preserved - keep the deleted_catalog_item but add a flag
            item["deleted_catalog_preserved"] = True
            items[item_index] = item
            updated["items"] = items
            return updated, True

    return updated, False


def audit_deleted_catalog_items(records, record_type="quote"):
    """
    Audit records for deleted catalog items and return summary statistics.

    Args:
        records: List of records (quotes or ldms)
        record_type: Type of records ("quote" or "ldm")

    Returns:
        Dict with audit statistics and detailed item information
    """
    audit_results = {
        "total_records": len(records),
        "records_with_deleted_items": 0,
        "total_deleted_items": 0,
        "preserved_items": 0,
        "unresolved_items": 0,
        "details": []
    }

    for record in records:
        record_id = record.get("id", "")
        record_name = record.get("quote_number", "") if record_type == "quote" else record.get("ldm_number", "")
        deleted_items = []

        for idx, item in enumerate(record.get("items", [])):
            if item.get("deleted_catalog_item"):
                is_preserved = item.get("deleted_catalog_preserved", False)
                deleted_items.append({
                    "index": idx,
                    "description": item.get("description", ""),
                    "deleted_item": item["deleted_catalog_item"],
                    "preserved": is_preserved,
                    "qty": item.get("qty", 0),
                    "price": item.get("price", 0),
                    "total": item.get("total", 0)
                })

        if deleted_items:
            audit_results["records_with_deleted_items"] += 1
            audit_results["total_deleted_items"] += len(deleted_items)
            audit_results["preserved_items"] += sum(1 for item in deleted_items if item["preserved"])
            audit_results["unresolved_items"] += sum(1 for item in deleted_items if not item["preserved"])

            audit_results["details"].append({
                "record_id": record_id,
                "record_name": record_name,
                "record_type": record_type,
                "deleted_items": deleted_items
            })

    return audit_results


def _mark_deleted_catalog_refs(records, deleted_items):
    cleaned = []
    refs_marked = 0
    for record in records:
        updated = dict(record)
        updated_items = []
        for item in updated.get("items", []) or []:
            updated_item = dict(item)
            catalog_item_id = str(updated_item.get("catalog_item_id", "")).strip()
            if catalog_item_id in deleted_items:
                updated_item["deleted_catalog_item"] = deleted_items[catalog_item_id]
                updated_item["catalog_item_id"] = ""
                refs_marked += 1
            updated_items.append(updated_item)
        updated["items"] = updated_items
        cleaned.append(updated)
    return cleaned, refs_marked
