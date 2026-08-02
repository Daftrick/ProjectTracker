"""Pagos ligados a cotizaciones.

Cada pago referencia una cotización (quote_id) y, por comodidad de consulta,
también el proyecto (project_id). Campos: fecha, monto, concepto/nota.
Disponible para todos los usuarios autenticados (ver rutas en routes/quotes.py).
"""

from .storage import load as _load, new_id, save as _save, today


def _normalize_payment(payment):
    if not isinstance(payment, dict):
        return None
    project_id = str(payment.get("project_id") or "").strip()
    quote_id = str(payment.get("quote_id") or "").strip()
    if not project_id or not quote_id:
        return None
    try:
        amount = round(float(payment.get("amount", 0) or 0), 2)
    except (TypeError, ValueError):
        amount = 0.0
    return {
        "id": str(payment.get("id") or new_id()).strip() or new_id(),
        "project_id": project_id,
        "quote_id": quote_id,
        "date": str(payment.get("date") or "").strip(),
        "amount": amount,
        "concept": str(payment.get("concept") or "").strip(),
        "created_at": str(payment.get("created_at") or "").strip() or today(),
    }


def get_payments() -> list:
    try:
        raw = _load("payments")
    except Exception:
        raw = []
    if not isinstance(raw, list):
        return []
    return [p for p in (_normalize_payment(item) for item in raw) if p is not None]


def save_payments(data: list):
    normalized = [p for p in (_normalize_payment(item) for item in data) if p is not None]
    _save("payments", normalized)


def get_payments_for_quote(quote_id: str) -> list:
    quote_id = str(quote_id or "").strip()
    return sorted(
        (p for p in get_payments() if p["quote_id"] == quote_id),
        key=lambda p: (p["date"], p["created_at"]),
        reverse=True,
    )


def get_payments_for_project(project_id: str) -> list:
    project_id = str(project_id or "").strip()
    return sorted(
        (p for p in get_payments() if p["project_id"] == project_id),
        key=lambda p: (p["date"], p["created_at"]),
        reverse=True,
    )


def payment_summary(total, payments) -> dict:
    """Total cotizado vs. pagado y saldo pendiente para un conjunto de pagos."""
    try:
        total = round(float(total or 0), 2)
    except (TypeError, ValueError):
        total = 0.0
    paid = round(sum(p.get("amount", 0) for p in payments), 2)
    return {"total": total, "paid": paid, "balance": round(total - paid, 2)}


def add_payment(project_id, quote_id, date_value, amount, concept):
    payments = get_payments()
    new_payment = _normalize_payment({
        "id": new_id(),
        "project_id": project_id,
        "quote_id": quote_id,
        "date": date_value,
        "amount": amount,
        "concept": concept,
        "created_at": today(),
    })
    payments.append(new_payment)
    save_payments(payments)
    return new_payment


def update_payment(payment_id, date_value, amount, concept) -> bool:
    payments = get_payments()
    payment = next((p for p in payments if p["id"] == str(payment_id)), None)
    if not payment:
        return False
    payment["date"] = date_value
    payment["amount"] = amount
    payment["concept"] = concept
    save_payments(payments)
    return True


def delete_payment(payment_id) -> bool:
    payments = get_payments()
    remaining = [p for p in payments if p["id"] != str(payment_id)]
    if len(remaining) == len(payments):
        return False
    save_payments(remaining)
    return True


def get_payment_by_id(payment_id):
    payment_id = str(payment_id or "").strip()
    return next((p for p in get_payments() if p["id"] == payment_id), None)
