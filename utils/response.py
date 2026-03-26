from typing import Any, Optional


def ok(data: Any = None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


def fail(message: str, code: str = "error", details: Optional[Any] = None) -> dict:
    return {
        "success": False,
        "error": {"message": message, "code": code, "details": details},
    }
