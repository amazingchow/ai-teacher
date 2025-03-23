from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    student_id = Column(String(20), unique=True, nullable=False)
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
    filename = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)  # 录音时长（秒）
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    check_result = Column(Text, nullable=True)  # 检查结果
    created_at = Column(String(50), nullable=False)  # 创建时间

    # student = relationship("Student", back_populates="recordings")
    # question = relationship("Question", back_populates="recordings")
    