import asyncio
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from routes.seller_routes import router as seller_router
from routes.items_routes import router as items_router
from routes.invoice_routes import router as invoices_router
from routes.payment_routes import router as payment_router
from utils.response import fail
from utils.paths import STATIC_DIR

if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

PAGES = {
    "index.html": "index.html",
    "seller.html": "seller.html",
    "items.html": "items.html",
    "invoices.html": "invoices.html",
    "invoice_preview.html": "invoice_preview.html",
}

app = FastAPI(title="Invoice Generator", version="1.0.0")

app.include_router(seller_router)
app.include_router(items_router)
app.include_router(invoices_router)
app.include_router(payment_router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    index_path = STATIC_DIR / "index.html"
    return FileResponse(str(index_path))


@app.get("/{page_name}")
def serve_page(page_name: str):
    if page_name not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(str(STATIC_DIR / PAGES[page_name]))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=fail(str(exc.detail)))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=fail(str(exc), code="server_error"))
