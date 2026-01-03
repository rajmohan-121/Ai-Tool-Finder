from pydantic import BaseModel, Field
from typing import Optional

class AdminCreate(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str


class ToolCreate(BaseModel):
    name: str = Field(..., min_length=2)
    use_case: str = Field(..., min_length=5)
    category: Optional[str] = None
    pricing: str

class ReviewCreate(BaseModel):
    tool_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ToolResponse(BaseModel):
    id: int
    name: str
    use_case: str
    category: Optional[str] = None
    pricing: str
    avg_rating: float

    class Config:
        orm_mode = True

class ReviewResponse(BaseModel):
    id: int
    tool_id: int
    rating: int
    comment: Optional[str]
    status: str

    class Config:
        orm_mode = True
