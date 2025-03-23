from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from typing import List
import os
from datetime import datetime

from models import Base, Student, Question, Recording
from database import engine, get_db
from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    RecordingResponse,
    BatchCheckRequest,
    BatchCheckResponse
)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 学生管理API
@app.get("/students", response_model=List[StudentResponse])
async def get_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return students

@app.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, student: StudentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    db_student = result.scalar_one_or_none()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for field, value in student.dict(exclude_unset=True).items():
        setattr(db_student, field, value)
    
    await db.commit()
    await db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}")
async def delete_student(student_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    db_student = result.scalar_one_or_none()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await db.delete(db_student)
    await db.commit()
    return {"message": "Student deleted successfully"}

# 题库管理API
@app.get("/questions", response_model=List[QuestionResponse])
async def get_questions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions

@app.post("/questions", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, db: AsyncSession = Depends(get_db)):
    db_question = Question(**question.dict())
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question

@app.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    db_question = result.scalar_one_or_none()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for field, value in question.dict(exclude_unset=True).items():
        setattr(db_question, field, value)
    
    await db.commit()
    await db.refresh(db_question)
    return db_question

@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    db_question = result.scalar_one_or_none()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    await db.delete(db_question)
    await db.commit()
    return {"message": "Question deleted successfully"}

# 录音文件管理API
@app.post("/recordings", response_model=None)
async def upload_recording(audio: UploadFile = File(...), student_id: str = Form(...), question_id: int = Form(...), duration: float = Form(None), db: AsyncSession = Depends(get_db)):
    # 检查学生和题目是否存在
    student_exists = await db.execute(select(exists().where(Student.student_id == student_id)))
    if not student_exists.scalar():
        raise HTTPException(status_code=404, detail="Student not found")
    
    question_exists = await db.execute(select(exists().where(Question.id == question_id)))
    if not question_exists.scalar():
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 保存文件
    file_content = await audio.read()
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, audio.filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 创建录音记录
    recording = Recording(
        filename=audio.filename,
        duration=duration,
        student_id=student_id,
        question_id=question_id,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)
    
    return recording

@app.post("/recordings/batch-check", response_model=List[BatchCheckResponse])
async def batch_check_recordings(request: BatchCheckRequest, db: AsyncSession = Depends(get_db)):
    results = []
    for recording_id in request.recording_ids:
        result = await db.execute(select(Recording).where(Recording.id == recording_id))
        recording = result.scalar_one_or_none()
        if recording:
            # TODO: 实现录音文件检查逻辑
            check_result = "检查结果示例"
            recording.check_result = check_result
            results.append(BatchCheckResponse(recording_id=recording_id, check_result=check_result))
    
    await db.commit()
    return results