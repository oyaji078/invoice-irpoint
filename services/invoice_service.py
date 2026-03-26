from typing import List, Dict, Any, Optional

from utils.paths import DATA_DIR
from utils.json_storage import read_json, write_json_atomic
from utils.id_generator import generate_invoice_id

INVOICES_FILE = DATA_DIR / "invoices.json"


def list_invoices(search: Optional[str] = None) -> List[Dict[str, Any]]:
    invoices = read_json(str(INVOICES_FILE), [])
    if search:
        q = search.lower()
        invoices = [
            inv
            for inv in invoices
            if q in inv.get("invoiceId", "").lower()
            or q in inv.get("customer", {}).get("customerName", "").lower()
        ]
    return invoices


def get_invoice(invoice_id: str) -> Optional[Dict[str, Any]]:
    invoices = read_json(str(INVOICES_FILE), [])
    for inv in invoices:
        if inv.get("invoiceId") == invoice_id:
            return inv
    return None


def _calculate_summary(items: List[Dict[str, Any]]) -> Dict[str, float]:
    subtotal = 0.0
    total_discount = 0.0
    for line in items:
        qty = int(line.get("qty", 0))
        unit_price = float(line.get("unitPrice", 0))
        discount_value = float(line.get("discount", 0))

        gross = qty * unit_price
        discount_amount = max(discount_value, 0)

        subtotal += gross
        total_discount += discount_amount

    grand_total = subtotal - total_discount
    return {
        "subtotal": round(subtotal, 2),
        "totalDiscount": round(total_discount, 2),
        "grandTotal": round(grand_total, 2),
    }


def create_invoice(payload: Dict[str, Any]) -> Dict[str, Any]:
    invoices = read_json(str(INVOICES_FILE), [])
    invoice_type = payload.get("invoiceType", "penjualan")
    invoice_id = payload.get("invoiceId") or generate_invoice_id(invoices, payload.get("date", ""), invoice_type)
    if any(inv.get("invoiceId") == invoice_id for inv in invoices):
        raise ValueError("Invoice ID already exists")

    if not payload.get("items"):
        raise ValueError("Invoice items are required")

    items = payload.get("items", [])
    summary = _calculate_summary(items)

    invoice = {
        "invoiceId": invoice_id,
        "invoiceType": invoice_type,
        "date": payload.get("date"),
        "customer": payload.get("customer"),
        "items": items,
        "paymentMethod": payload.get("paymentMethod"),
        "notes": payload.get("notes"),
        "status": payload.get("status", "Sent"),
        "summary": summary,
    }
    invoices.append(invoice)
    write_json_atomic(str(INVOICES_FILE), invoices)
    return invoice


def update_invoice(invoice_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    invoices = read_json(str(INVOICES_FILE), [])
    for idx, inv in enumerate(invoices):
        if inv.get("invoiceId") == invoice_id:
            updated = {**inv}
            for key, value in payload.items():
                if value is None:
                    continue
                updated[key] = value
            updated["invoiceId"] = invoice_id
            updated["summary"] = _calculate_summary(updated.get("items", []))
            invoices[idx] = updated
            write_json_atomic(str(INVOICES_FILE), invoices)
            return updated
    raise KeyError("Invoice not found")


def delete_invoice(invoice_id: str) -> None:
    invoices = read_json(str(INVOICES_FILE), [])
    new_invoices = [inv for inv in invoices if inv.get("invoiceId") != invoice_id]
    if len(new_invoices) == len(invoices):
        raise KeyError("Invoice not found")
    write_json_atomic(str(INVOICES_FILE), new_invoices)


def build_invoice_view(invoice: Dict[str, Any]) -> Dict[str, Any]:
    lines = []
    subtotal = 0.0
    total_discount = 0.0

    for idx, line in enumerate(invoice.get("items", []), start=1):
        name = line.get("name") or "Item"

        qty = int(line.get("qty", 0))
        unit_price = float(line.get("unitPrice", 0))
        discount_value = float(line.get("discount", 0))

        gross = qty * unit_price
        discount_amount = max(discount_value, 0)
        total = max(gross - discount_amount, 0)

        subtotal += gross
        total_discount += discount_amount

        lines.append(
            {
                "no": idx,
                "name": name,
                "qty": qty,
                "unitPrice": unit_price,
                "discount": discount_amount,
                "lineTotal": total,
            }
        )

    summary = {
        "subtotal": subtotal,
        "totalDiscount": total_discount,
        "grandTotal": subtotal - total_discount,
    }

    return {"lines": lines, "summary": summary}
