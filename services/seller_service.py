from typing import Dict, Any

from utils.paths import DATA_DIR
from utils.json_storage import read_json, write_json_atomic

SELLER_FILE = DATA_DIR / "seller.json"

DEFAULT_SELLER = {
    "storeName": "",
    "sellerName": "",
    "email": "",
    "phone": "",
    "address": "",
    "logoUrl": "",
}


def get_seller() -> Dict[str, Any]:
    return read_json(str(SELLER_FILE), DEFAULT_SELLER)


def update_seller(data: Dict[str, Any]) -> Dict[str, Any]:
    write_json_atomic(str(SELLER_FILE), data)
    return data
