from fastapi import APIRouter, Depends, BackgroundTasks
from backend.pipeline.main import FinanceDataPipeline
from backend.api.deps import get_pipeline
from backend.api.schemas import DiscoverResponse
from backend.pipeline.utils.logger import pipeline_logger
import threading
import time

router = APIRouter(prefix="/api/discover", tags=["discovery"])

_pipeline_state = {
    "running": False,
    "mode": None,
    "progress": None,
}


@router.get("/status")
def get_status():
    return _pipeline_state


def _run_sector_discovery(pipeline: FinanceDataPipeline):
    try:
        _pipeline_state["running"] = True
        _pipeline_state["mode"] = "sectors"
        _pipeline_state["progress"] = {"phase": "discovering_sectors"}
        pipeline.run_sector_discovery()
        _pipeline_state["progress"] = {"phase": "complete"}
    except Exception as e:
        pipeline_logger.error(f"Sector discovery failed: {e}")
        _pipeline_state["progress"] = {"phase": "error", "error": str(e)}
    finally:
        _pipeline_state["running"] = False


def _run_company_discovery(pipeline: FinanceDataPipeline, timeout: int):
    try:
        _pipeline_state["running"] = True
        _pipeline_state["mode"] = "companies"
        _pipeline_state["progress"] = {"phase": "discovering_companies"}
        pipeline.run_company_discovery(timeout_minutes=timeout)
        _pipeline_state["progress"] = {"phase": "complete"}
    except Exception as e:
        pipeline_logger.error(f"Company discovery failed: {e}")
        _pipeline_state["progress"] = {"phase": "error", "error": str(e)}
    finally:
        _pipeline_state["running"] = False


@router.post("/sectors", response_model=DiscoverResponse)
def discover_sectors(background_tasks: BackgroundTasks):
    if _pipeline_state["running"]:
        return DiscoverResponse(message="Pipeline already running", count=0)

    pipeline = get_pipeline()
    thread = threading.Thread(target=_run_sector_discovery, args=(pipeline,), daemon=True)
    thread.start()
    return DiscoverResponse(message="Sector discovery started", count=0)


@router.post("/companies", response_model=DiscoverResponse)
def discover_companies(background_tasks: BackgroundTasks, timeout: int = 60):
    if _pipeline_state["running"]:
        return DiscoverResponse(message="Pipeline already running", count=0)

    pipeline = get_pipeline()
    thread = threading.Thread(target=_run_company_discovery, args=(pipeline, timeout), daemon=True)
    thread.start()
    return DiscoverResponse(message="Company discovery started", count=0)
