import hashlib
import os
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from models import Base, Question, Recording, Student
from schemas import (
    BatchCheckResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    RecordingResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from tasks import check_audio_file

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
    # 获取学生和题目信息
    student = await db.execute(
        select(Student.student_id, Student.name)
        .where(Student.student_id == student_id)
    )
    student_result = student.first()
    if not student_result:
        raise HTTPException(status_code=404, detail="Student not found")
    
    question = await db.execute(
        select(Question.id, Question.title)
        .where(Question.id == question_id)
    )
    question_result = question.first()
    if not question_result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 保存文件
    file_content = await audio.read()
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filename = f'{question_id}_{student_id}_{datetime.now().strftime("%Y-%m-%d")}.webm'
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 创建录音记录
    task_id = hashlib.sha1(f'{question_id}_{datetime.now().strftime("%Y-%m-%d")}'.encode('utf-8')).hexdigest()
    recording = Recording(
        task_id=task_id,
        filename=filename,
        duration=duration,
        student_id=student_id,
        student_name=student_result.name,
        question_id=question_id,
        question_title=question_result.title,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)
    
    return recording


@app.get("/recordings/{question_id}", response_model=List[RecordingResponse])
async def get_recording(question_id: int, db: AsyncSession = Depends(get_db)):
    task_id = hashlib.sha1(f'{question_id}_{datetime.now().strftime("%Y-%m-%d")}'.encode('utf-8')).hexdigest()
    result = await db.execute(select(Recording).where(Recording.task_id == task_id))
    recordings = result.scalars().all()
    return recordings


@app.get("/recordings/batch-check/{question_id}", response_model=List[BatchCheckResponse])
async def batch_check_recordings(question_id: int, db: AsyncSession = Depends(get_db)):
    results = []
    task_id = hashlib.sha1(f'{question_id}_{datetime.now().strftime("%Y-%m-%d")}'.encode('utf-8')).hexdigest()
    result = await db.execute(select(Recording).where(Recording.task_id == task_id, Recording.check_result != 'checked'))
    recordings = result.scalars().all()
    
    # 提交检查任务到Celery
    for recording in recordings:
        check_audio_file.delay(recording.id)
        results.append(BatchCheckResponse(
            recording_id=recording.id,
            check_result="Task submitted for processing"
        ))
    
    return results
