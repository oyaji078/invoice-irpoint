from fastapi import APIRouter, HTTPException, Query

from services.items_service import (
    list_items as list_items_service,
    get_item as get_item_service,
    create_item as create_item_service,
    update_item as update_item_service,
    delete_item as delete_item_service,
)
from schemas.item import ItemCreate, ItemUpdate
from utils.response import ok, fail

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("")
def list_items(search: str = Query(default=None)):
    items = list_items_service(search)
    return ok(items)


@router.post("")
def create_item(item: ItemCreate):
    try:
        created = create_item_service(item.model_dump())
        return ok(created, "Item created")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc), code="validation"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=fail(str(exc)))


@router.get("/{item_id}")
def get_item(item_id: str):
    item = get_item_service(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=fail("Item not found", code="not_found"))
    return ok(item)


@router.put("/{item_id}")
def update_item(item_id: str, payload: ItemUpdate):
    try:
        updated = update_item_service(item_id, payload.model_dump())
        return ok(updated, "Item updated")
    except KeyError:
        raise HTTPException(status_code=404, detail=fail("Item not found", code="not_found"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))


@router.delete("/{item_id}")
def delete_item(item_id: str):
    try:
        delete_item_service(item_id)
        return ok(message="Item deleted")
    except KeyError:
        raise HTTPException(status_code=404, detail=fail("Item not found", code="not_found"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=fail(str(exc)))
