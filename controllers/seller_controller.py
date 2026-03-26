from typing import Dict, Any
from services.seller_service import get_seller, update_seller


def fetch_seller() -> Dict[str, Any]:
    return get_seller()


def save_seller(payload: Dict[str, Any]) -> Dict[str, Any]:
    return update_seller(payload)
