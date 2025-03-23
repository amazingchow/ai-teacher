from pydantic import BaseModel, Field
from typing import Optional, List

# 学生模型
class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    student_id: str = Field(..., min_length=2, max_length=20)
    gender: str = Field(..., pattern='^[MF]$')
    age: int = Field(..., ge=6, le=15)
    class_name: str = Field(..., min_length=2, max_length=50)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    student_id: Optional[str] = Field(None, min_length=2, max_length=20)
    gender: Optional[str] = Field(None, pattern='^[MF]$')
    age: Optional[int] = Field(None, ge=6, le=15)
    class_name: Optional[str] = Field(None, min_length=2, max_length=50)

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True

# 题目模型
class QuestionBase(BaseModel):
    category: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2)
    content: str = Field(..., min_length=2)
    answer: Optional[str] = Field(None)

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(QuestionBase):
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    title: Optional[str] = Field(None, min_length=2)
    content: Optional[str] = Field(None, min_length=2)
    answer: Optional[str] = Field(None)

class QuestionResponse(QuestionBase):
    id: int

    class Config:
        from_attributes = True

# 录音文件模型
class RecordingBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    duration: float = Field(..., gt=0)
    student_id: str = Field(..., min_length=2, max_length=20)
    question_id: int = Field(...)
    check_result: Optional[str] = None
    created_at: str = Field(..., min_length=1, max_length=50)

class RecordingResponse(RecordingBase):
    id: int

    class Config:
        from_attributes = True

# 批量检查请求模型
class BatchCheckRequest(BaseModel):
    recording_ids: List[int] = Field(..., min_items=1)

# 批量检查响应模型
class BatchCheckResponse(BaseModel):
    recording_id: int
    check_result: str