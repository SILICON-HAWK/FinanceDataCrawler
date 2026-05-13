from fastapi import FastAPI
from backend.api.routes.discovery import router as discovery_router
from backend.api.routes.extraction import router as extraction_router
from backend.api.routes.status import router as status_router

app = FastAPI(title="FinanceDataCrawler API", version="0.1.0")

app.include_router(discovery_router)
app.include_router(extraction_router)
app.include_router(status_router)


@app.get("/health")
def health():
    return {"status": "ok"}
