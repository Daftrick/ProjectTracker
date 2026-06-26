"""Helpers compartidos entre validators, form_models, admin y rutas."""
import datetime
import re


def clean(value):
    return str(value or "").strip()


def parse_form_float(value, field_label, errors, row=None, default=0.0, field_errors=None, field_key=None):
    """Convierte a float con reporte de errores en lista `errors`. Usado en validadores de formulario."""
    raw = clean(value)
    if raw == "":
        return default
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        prefix = f"Fila {row}: " if row else ""
        message = f"{prefix}{field_label} debe ser un número válido."
        errors.append(message)
        if field_errors is not None and field_key:
            field_errors.setdefault(field_key, message)
        return default


def parse_float(value, default=0.0):
    """Convierte a float silenciosamente. Usado donde no se necesita reporte de error."""
    raw = clean(value).replace(",", ".")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def folder_name(project):
    return f"IE-{project.get('folder_num', '000')}-{project['clave']}"


def parse_csv_plano_filename(filename, clave=None):
    clave_pattern = re.escape(clave) if clave else r"(?P<clave>[A-Za-z0-9_-]+)"
    pattern = re.compile(
        rf"^(?P<project>{clave_pattern})-v(?P<version>\d+)-i(?P<consecutive>\d+)-(?P<date>\d{{8}})\.csv$",
        re.IGNORECASE,
    )
    match = pattern.match(filename or "")
    if not match:
        return None
    date_token = match.group("date")
    try:
        date_label = datetime.datetime.strptime(date_token, "%Y%m%d").strftime("%d/%m/%Y")
    except ValueError:
        date_label = date_token
    return {
        "project": match.group("project"),
        "version": int(match.group("version")),
        "consecutive": int(match.group("consecutive")),
        "date": date_token,
        "date_label": date_label,
    }


def deleted_catalog_item_at(ids, names, descriptions, units, prices, deleted_dates, index):
    """Construye el snapshot de un artículo de catálogo eliminado desde listas de campos paralelos."""
    deleted_id = clean(ids[index]) if index < len(ids) else ""
    if not deleted_id:
        return None
    return {
        "id": deleted_id,
        "nombre": clean(names[index]) if index < len(names) else "",
        "descripcion": clean(descriptions[index]) if index < len(descriptions) else "",
        "unidad": clean(units[index]) if index < len(units) else "",
        "precio": parse_float(prices[index]) if index < len(prices) else 0.0,
        "deleted_at": clean(deleted_dates[index]) if index < len(deleted_dates) else "",
    }
