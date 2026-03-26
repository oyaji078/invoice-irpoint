from typing import Dict, Any, List, Optional
from services.items_service import list_items, get_item, create_item, update_item, delete_item


def list_items_controller(search: Optional[str] = None) -> List[Dict[str, Any]]:
    return list_items(search)


def get_item_controller(item_id: str) -> Optional[Dict[str, Any]]:
    return get_item(item_id)


def create_item_controller(payload: Dict[str, Any]) -> Dict[str, Any]:
    return create_item(payload)


def update_item_controller(item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return update_item(item_id, payload)


def delete_item_controller(item_id: str) -> None:
    delete_item(item_id)
