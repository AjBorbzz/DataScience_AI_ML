from typing import List, Optional, Literal 
from fastapi import FastAPI, Body 
from pydantic import BaseModel, Field
import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type


class SummarizeReport(BaseModel):
    log: str = Field(...,description = "Raw log line or multi-line blob")
    source: Optional[str] = Field(None, description="Source system e.g., firewall, EDR, xdr, syslog")
    format: Optional[str] = Field(None, description="Log format e.g., json, cef, syslog, leef")
    language: Literal["en"] | None = Field("en", description="Currently only English is tuned in the prompt")


class SummarizeRequest(BaseModel):
    summary: str
    risk: Literal["low", "medium", "high", "unknown"]
    ioc_candidates: List[str] = []
    reasoning: Optional[str] = None