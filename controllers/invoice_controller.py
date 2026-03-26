from typing import Dict, Any, List, Optional
from services.invoice_service import list_invoices, get_invoice, create_invoice, update_invoice, delete_invoice, build_invoice_view


def list_invoices_controller(search: Optional[str] = None) -> List[Dict[str, Any]]:
    return list_invoices(search)


def get_invoice_controller(invoice_id: str) -> Optional[Dict[str, Any]]:
    return get_invoice(invoice_id)


def create_invoice_controller(payload: Dict[str, Any]) -> Dict[str, Any]:
    return create_invoice(payload)


def update_invoice_controller(invoice_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return update_invoice(invoice_id, payload)


def delete_invoice_controller(invoice_id: str) -> None:
    delete_invoice(invoice_id)


def build_invoice_view_controller(invoice: Dict[str, Any]) -> Dict[str, Any]:
    return build_invoice_view(invoice)
