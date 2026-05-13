from pydantic import BaseModel
from typing import Optional


class ExtractRequest(BaseModel):
    company_urls: Optional[list[str]] = None
    sector_names: Optional[list[str]] = None
    max_companies: Optional[int] = None
    skip_existing: bool = True


class PipelineStatus(BaseModel):
    running: bool
    mode: Optional[str] = None
    progress: Optional[dict] = None


class DiscoverResponse(BaseModel):
    message: str
    count: int
