from typing import Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=2)
    sku: Optional[str] = None
    unit: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    taxRate: float = Field(default=0, ge=0)


class ItemCreate(ItemBase):
    id: Optional[str] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    taxRate: Optional[float] = Field(default=None, ge=0)
