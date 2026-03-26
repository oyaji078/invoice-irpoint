from typing import List, Dict, Any

from utils.paths import DATA_DIR
from utils.json_storage import read_json, write_json_atomic

PAYMENTS_FILE = DATA_DIR / "payment_methods.json"

DEFAULT_PAYMENTS = [
    {"label": "Tunai", "methodType": "cash"}
]


def list_payment_methods() -> List[Dict[str, Any]]:
    return read_json(str(PAYMENTS_FILE), DEFAULT_PAYMENTS)


def save_payment_methods(methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    write_json_atomic(str(PAYMENTS_FILE), methods)
    return methods
