from pydantic import BaseModel, Field
from typing import List, Optional


class TrackRecord(BaseModel):
    h_index: Optional[float] = 0.0
    citations: Optional[int] = 0
    pubs_last_3y: Optional[int] = 0
    grants_success_rate: Optional[float] = 0.0
    custom_score: Optional[float] = 0.0


class Employee(BaseModel):
    id: str
    name: str
    role: str
    scholar_id: Optional[str] = None
    skills_text: str = ""
    track_record: TrackRecord = TrackRecord()


class WorkElement(BaseModel):
    id: str
    text: str
    keyphrases: List[str] = Field(default_factory=list)
    priority: Optional[int] = None


class CfpRequest(BaseModel):
    title: Optional[str] = None
    text: str


class AnalyzeResponse(BaseModel):
    work_elements: List[WorkElement]


class RecommendRequest(BaseModel):
    text: Optional[str] = None
    cfp_elements: Optional[List[WorkElement]] = None
    top_k: int = 3
    min_similarity: float = 0.25


class Candidate(BaseModel):
    employee_id: str
    name: str
    similarity: float
    rationale: Optional[str] = None


class Assignment(BaseModel):
    work_element_id: str
    candidates: List[Candidate]
    selected_employee_id: Optional[str] = None


class RecommendResponse(BaseModel):
    assignments: List[Assignment]
    coverage_score: float
    confidence_score: float
    gaps: List[str]
