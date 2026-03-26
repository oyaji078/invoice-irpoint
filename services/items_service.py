from typing import List, Dict, Any, Optional

from utils.paths import DATA_DIR
from utils.json_storage import read_json, write_json_atomic
from utils.id_generator import generate_item_id

ITEMS_FILE = DATA_DIR / "items.json"


def list_items(search: Optional[str] = None) -> List[Dict[str, Any]]:
    items = read_json(str(ITEMS_FILE), [])
    if search:
        q = search.lower()
        items = [
            i
            for i in items
            if q in i.get("name", "").lower()
            or q in i.get("sku", "").lower()
            or q in i.get("id", "").lower()
        ]
    return items


def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    items = read_json(str(ITEMS_FILE), [])
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def create_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = read_json(str(ITEMS_FILE), [])
    item_id = payload.get("id") or generate_item_id(items)
    if any(i.get("id") == item_id for i in items):
        raise ValueError("Item ID already exists")
    item = {
        "id": item_id,
        "name": payload.get("name"),
        "sku": payload.get("sku"),
        "unit": payload.get("unit"),
        "price": payload.get("price"),
        "taxRate": payload.get("taxRate", 0),
    }
    items.append(item)
    write_json_atomic(str(ITEMS_FILE), items)
    return item


def update_item(item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    items = read_json(str(ITEMS_FILE), [])
    for idx, item in enumerate(items):
        if item.get("id") == item_id:
            updated = {**item, **{k: v for k, v in payload.items() if v is not None}}
            updated["id"] = item_id
            items[idx] = updated
            write_json_atomic(str(ITEMS_FILE), items)
            return updated
    raise KeyError("Item not found")


def delete_item(item_id: str) -> None:
    items = read_json(str(ITEMS_FILE), [])
    new_items = [i for i in items if i.get("id") != item_id]
    if len(new_items) == len(items):
        raise KeyError("Item not found")
    write_json_atomic(str(ITEMS_FILE), new_items)
