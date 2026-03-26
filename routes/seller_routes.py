from fastapi import APIRouter, HTTPException

from services.seller_service import get_seller as get_seller_service, update_seller as update_seller_service
from schemas.seller import SellerProfile
from utils.response import ok, fail

router = APIRouter(prefix="/api/seller", tags=["seller"])


@router.get("")
def get_seller():
    return ok(get_seller_service())


@router.put("")
def update_seller(profile: SellerProfile):
    try:
        data = update_seller_service(profile.model_dump())
        return ok(data, "Seller profile updated")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))
