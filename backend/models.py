from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class StudentProfile(BaseModel):
    name: str = Field(..., max_length=100)
    age: int = Field(..., ge=10, le=100)
    stream: str = Field(..., max_length=50)           # Engineering, Medical, Arts, Commerce, Science, Law, Design
    preferred_branch: Optional[str] = Field("Any", max_length=50)
    marks: float = Field(..., ge=0, le=100)           # Percentage or score
    exam_type: str = Field(..., max_length=50)        # JEE, NEET, 12th %, CET, CAT, CLAT, CUET
    preferred_state: Optional[str] = Field("Any", max_length=50)
    budget: Optional[str] = Field("Any", max_length=50)  # Any, <5L, 5-15L, 15L+
    college_type: Optional[str] = Field("Any", max_length=50)  # Govt, Private, Any
    category: Optional[str] = Field("Open", max_length=50)     # Open, OBC, SC, ST, EWS
    family_income: Optional[str] = Field("Any", max_length=50) # <8L, >8L, etc.
    gender: Optional[str] = Field("Male", max_length=20)       # Male, Female, Other

class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    content: str = Field(..., max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=1000)
    student_profile: StudentProfile
    history: Optional[List[ChatMessage]] = Field(default_factory=list, max_length=50)

class RecommendRequest(BaseModel):
    student_profile: StudentProfile

class CollegeSearchRequest(BaseModel):
    stream: Optional[str] = None
    state: Optional[str] = None
    max_budget: Optional[str] = None
    college_type: Optional[str] = None
    min_marks: Optional[float] = None
