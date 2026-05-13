from fastapi import APIRouter
from backend.pipeline.main import FinanceDataPipeline

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
def get_status():
    pipeline = FinanceDataPipeline()
    stats = pipeline.queue_manager.get_statistics()
    storage_stats = pipeline.storage.get_storage_stats()
    return {
        "pipeline": stats,
        "storage": storage_stats,
    }


@router.get("/companies")
def list_companies(search: str = ""):
    pipeline = FinanceDataPipeline()
    if search:
        return pipeline.queue_manager.search_company_by_name(search)
    return pipeline.queue_manager.list_all_companies()


@router.get("/companies/{name}")
def get_company(name: str):
    pipeline = FinanceDataPipeline()
    data = pipeline.storage.load_company_data(name)
    if not data:
        return {"error": "Company not found"}, 404
    return data
