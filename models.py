from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    student_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    courses = relationship("Course", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, index=True)
    credits = Column(Integer)
    student_id = Column(Integer, ForeignKey("students.id"))
    semester = Column(String)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    student = relationship("Student", back_populates="courses")
    assignments = relationship("Assignment", back_populates="course")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # exam, quiz, homework, project, etc.
    score = Column(Float)
    max_score = Column(Float)
    weight = Column(Float)  # percentage weight in final grade
    course_id = Column(Integer, ForeignKey("courses.id"))
    date_submitted = Column(DateTime, default=datetime.utcnow)

    # Relationship
    course = relationship("Course", back_populates="assignments")