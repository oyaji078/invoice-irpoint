from typing import Optional
from pydantic import BaseModel, Field


class SellerProfile(BaseModel):
    storeName: str = Field(..., min_length=2)
    sellerName: str = Field(..., min_length=2)
    email: Optional[str] = None
    phone: str = Field(..., min_length=5)
    address: str = Field(..., min_length=5)
    logoUrl: Optional[str] = None
