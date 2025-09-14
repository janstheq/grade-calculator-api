from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Assignment Schemas
class AssignmentBase(BaseModel):
    name: str
    type: str
    score: float
    max_score: float
    weight: float


class AssignmentCreate(AssignmentBase):
    course_id: int


class Assignment(AssignmentBase):
    id: int
    course_id: int
    date_submitted: datetime

    class Config:
        from_attributes = True


# Course Schemas
class CourseBase(BaseModel):
    name: str
    code: str
    credits: int
    semester: str
    year: int


class CourseCreate(CourseBase):
    student_id: int


class Course(CourseBase):
    id: int
    student_id: int
    created_at: datetime
    assignments: List[Assignment] = []

    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    name: str
    email: str
    student_id: str


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    id: int
    created_at: datetime
    courses: List[Course] = []

    class Config:
        from_attributes = True


# Response Schemas
class GPAResponse(BaseModel):
    student_id: int
    current_gpa: float
    total_credits: int
    courses_count: int


class GradePrediction(BaseModel):
    course_id: int
    course_name: str
    current_grade: float
    predicted_final_grade: float
    remaining_weight: float


class ProgressReport(BaseModel):
    student_id: int
    student_name: str
    current_gpa: float
    total_credits: int
    courses: List[dict]