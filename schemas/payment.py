from typing import Optional, Literal
from pydantic import BaseModel, Field


class PaymentMethod(BaseModel):
    label: str = Field(..., min_length=2)
    methodType: Optional[Literal["cash", "bank", "ewallet", "other"]] = "cash"
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    details: Optional[str] = None
