from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from schemas.payment import PaymentMethod


class InvoiceCustomer(BaseModel):
    customerName: str = Field(..., min_length=2)
    customerPhone: Optional[str] = None
    customerAddress: Optional[str] = None


class InvoiceItem(BaseModel):
    name: str = Field(..., min_length=1)
    qty: int = Field(..., gt=0)
    unitPrice: float = Field(..., gt=0)
    discount: Optional[float] = Field(default=0, ge=0)


class InvoiceBase(BaseModel):
    date: str
    invoiceType: Optional[Literal["penjualan", "service", "gabungan"]] = "penjualan"
    customer: InvoiceCustomer
    items: List[InvoiceItem]
    paymentMethod: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    status: Optional[Literal["Sent", "Paid", "Overdue"]] = "Sent"


class InvoiceCreate(InvoiceBase):
    invoiceId: Optional[str] = None


class InvoiceUpdate(BaseModel):
    date: Optional[str] = None
    invoiceType: Optional[Literal["penjualan", "service", "gabungan"]] = None
    customer: Optional[InvoiceCustomer] = None
    items: Optional[List[InvoiceItem]] = None
    paymentMethod: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    status: Optional[Literal["Sent", "Paid", "Overdue"]] = None
