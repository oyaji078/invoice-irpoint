from fastapi import APIRouter, HTTPException
from typing import List

from services.payment_service import list_payment_methods, save_payment_methods
from schemas.payment import PaymentMethod
from utils.response import ok, fail

router = APIRouter(prefix="/api/payment-methods", tags=["payment-methods"])


@router.get("")
def get_payment_methods():
    return ok(list_payment_methods())


@router.put("")
def update_payment_methods(methods: List[PaymentMethod]):
    try:
        data = save_payment_methods([m.model_dump() for m in methods])
        return ok(data, "Payment methods updated")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))
