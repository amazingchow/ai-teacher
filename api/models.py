from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), index=True, unique=True, nullable=False)
    gender = Column(String(1), nullable=False)  # 'M' for male, 'F' for female
    age = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=False)
    # recordings = relationship("Recording", back_populates="student")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    # recordings = relationship("Recording", back_populates="question")


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), index=True, nullable=False)  # 任务ID，SHA1(question_id + '_' + current_date(2025-03-23))
    filename = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)  # 录音时长（秒）
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    student_name = Column(String(50), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_title = Column(Text, nullable=False)
    check_result = Column(Text, nullable=False, default='pending')  # 检查结果
    score = Column(Integer, nullable=True)  # 得分
    created_at = Column(String(50), nullable=False)  # 创建时间

    # student = relationship("Student", back_populates="recordings")
    # question = relationship("Question", back_populates="recordings")
