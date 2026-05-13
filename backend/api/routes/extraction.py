from fastapi import APIRouter, Depends, BackgroundTasks
from backend.pipeline.main import FinanceDataPipeline
from backend.api.deps import get_pipeline
from backend.api.schemas import ExtractRequest, PipelineStatus, DiscoverResponse
from backend.pipeline.utils.logger import pipeline_logger
import threading

router = APIRouter(prefix="/api/extract", tags=["extraction"])

_extraction_state = {
    "running": False,
    "progress": None,
    "processed": 0,
    "total": 0,
    "current_company": None,
}


@router.get("/status")
def get_extraction_status():
    return _extraction_state


def _run_extraction(pipeline: FinanceDataPipeline, req: ExtractRequest):
    try:
        _extraction_state["running"] = True
        _extraction_state["progress"] = {"phase": "starting"}

        companies_data = pipeline.queue_manager.load_company_queue()
        total = 0
        if req.sector_names:
            total = sum(len(urls) for s, urls in companies_data.items() if s in req.sector_names)
        else:
            total = sum(len(urls) for urls in companies_data.values())

        _extraction_state["total"] = total
        _extraction_state["processed"] = 0

        if req.company_urls:
            _extraction_state["progress"] = {"phase": "extracting_selected"}
            for url in req.company_urls:
                _extraction_state["current_company"] = url
                soup = pipeline.crawler.fetch_url(url)
                if soup:
                    result = pipeline.company_parser.parse(soup, company_url=url)
                    if result:
                        company_name = result["company_name"]
                        if req.skip_existing and pipeline.storage.company_exists(company_name):
                            continue
                        pipeline.storage.save_company_data(company_name, result)
                        _extraction_state["processed"] += 1
        else:
            kwargs = {}
            if req.max_companies:
                kwargs["max_companies"] = req.max_companies
            if req.sector_names:
                kwargs["sector_names"] = req.sector_names
            pipeline.run_company_extraction(**kwargs)
            _extraction_state["processed"] = _extraction_state["total"]
            _extraction_state["progress"] = {"phase": "complete"}

        _extraction_state["progress"] = {"phase": "complete"}
    except Exception as e:
        pipeline_logger.error(f"Extraction failed: {e}")
        _extraction_state["progress"] = {"phase": "error", "error": str(e)}
    finally:
        _extraction_state["running"] = False


@router.post("", response_model=DiscoverResponse)
def extract_companies(body: ExtractRequest, background_tasks: BackgroundTasks):
    if _extraction_state["running"]:
        return DiscoverResponse(message="Extraction already running", count=0)

    pipeline = get_pipeline()
    thread = threading.Thread(target=_run_extraction, args=(pipeline, body), daemon=True)
    thread.start()
    return DiscoverResponse(message="Extraction started", count=0)
