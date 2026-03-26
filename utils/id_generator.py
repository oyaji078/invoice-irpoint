from datetime import datetime
from typing import List, Dict


def _invoice_prefix(invoice_type: str) -> str:
    kind = (invoice_type or "penjualan").lower()
    if kind == "service":
        return "SIR"
    if kind == "gabungan":
        return "GIR"
    return "PIR"


def generate_invoice_id(existing: List[Dict], date_str: str, invoice_type: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        dt = datetime.utcnow()
    prefix = f"{_invoice_prefix(invoice_type)}-{dt.strftime('%Y%m')}-"
    seq = 1
    for inv in existing:
        inv_id = inv.get("invoiceId", "")
        if inv_id.startswith(prefix):
            try:
                number = int(inv_id.split("-")[-1])
                seq = max(seq, number + 1)
            except ValueError:
                continue
    return f"{prefix}{seq:04d}"


def generate_item_id(existing: List[Dict]) -> str:
    seq = 1
    for item in existing:
        item_id = item.get("id", "")
        if item_id.startswith("ITEM-"):
            try:
                number = int(item_id.split("-")[-1])
                seq = max(seq, number + 1)
            except ValueError:
                continue
    return f"ITEM-{seq:03d}"
