from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from services.invoice_service import (
    list_invoices as list_invoices_service,
    get_invoice as get_invoice_service,
    create_invoice as create_invoice_service,
    update_invoice as update_invoice_service,
    delete_invoice as delete_invoice_service,
    build_invoice_view as build_invoice_view_service,
)
from services.seller_service import get_seller as get_seller_service
from schemas.invoice import InvoiceCreate, InvoiceUpdate
from services.pdf_service import html_to_pdf
from utils.id_generator import generate_invoice_id
from utils.response import ok, fail
from utils.template_env import render_template
from utils.formatter import format_idr, format_date
from utils.paths import STATIC_DIR

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


def _load_invoice_css() -> str:
    css_path = STATIC_DIR / "css" / "invoice.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


@router.get("")
def list_invoices(search: str = Query(default=None)):
    invoices = list_invoices_service(search)
    return ok(invoices)


@router.get("/{invoice_id}")
def get_invoice(invoice_id: str):
    invoice = get_invoice_service(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=fail("Invoice not found", code="not_found"))
    return ok(invoice)


@router.post("")
def create_invoice(payload: InvoiceCreate):
    try:
        created = create_invoice_service(payload.model_dump())
        return ok(created, "Invoice created")
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc), code="validation"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc), code="validation"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=fail(str(exc)))


@router.post("/preview", response_class=HTMLResponse)
async def invoice_preview(payload: InvoiceCreate):
    invoice = payload.model_dump()
    invoice_type = invoice.get("invoiceType", "penjualan")
    if not invoice.get("invoiceId"):
        invoice["invoiceId"] = generate_invoice_id(
            list_invoices_service(), invoice.get("date", ""), invoice_type
        )
    if invoice.get("items") is None:
        invoice["items"] = []
    seller = get_seller_service()
    view = build_invoice_view_service(invoice)
    html = render_template(
        "invoice.html",
        invoice=invoice,
        seller=seller,
        view=view,
        invoice_css=_load_invoice_css(),
        format_idr=format_idr,
        format_date=format_date,
    )
    return HTMLResponse(content=html)


@router.put("/{invoice_id}")
def update_invoice(invoice_id: str, payload: InvoiceUpdate):
    try:
        updated = update_invoice_service(invoice_id, payload.model_dump())
        return ok(updated, "Invoice updated")
    except KeyError:
        raise HTTPException(status_code=404, detail=fail("Invoice not found", code="not_found"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: str):
    try:
        delete_invoice_service(invoice_id)
        return ok(message="Invoice deleted")
    except KeyError:
        raise HTTPException(status_code=404, detail=fail("Invoice not found", code="not_found"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))


@router.get("/{invoice_id}/html", response_class=HTMLResponse)
async def invoice_html(invoice_id: str):
    invoice = get_invoice_service(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=fail("Invoice not found", code="not_found"))
    seller = get_seller_service()
    view = build_invoice_view_service(invoice)
    html = render_template(
        "invoice.html",
        invoice=invoice,
        seller=seller,
        view=view,
        invoice_css=_load_invoice_css(),
        format_idr=format_idr,
        format_date=format_date,
    )
    return HTMLResponse(content=html)


@router.get("/{invoice_id}/pdf")
async def invoice_pdf(invoice_id: str):
    invoice = get_invoice_service(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=fail("Invoice not found", code="not_found"))
    seller = get_seller_service()
    view = build_invoice_view_service(invoice)
    html = render_template(
        "invoice.html",
        invoice=invoice,
        seller=seller,
        view=view,
        invoice_css=_load_invoice_css(),
        format_idr=format_idr,
        format_date=format_date,
    )
    try:
        pdf_bytes = await html_to_pdf(html)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=fail(f"PDF generation failed: {exc}"))
    filename = f"{invoice_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
