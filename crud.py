from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas


# Student CRUD operations
def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_student_by_student_id(db: Session, student_id: str):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(
        name=student.name,
        email=student.email,
        student_id=student.student_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


# Course CRUD operations
def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses_by_student(db: Session, student_id: int):
    return db.query(models.Course).filter(models.Course.student_id == student_id).all()


def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(
        name=course.name,
        code=course.code,
        credits=course.credits,
        semester=course.semester,
        year=course.year,
        student_id=course.student_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


# Assignment CRUD operations
def get_assignment(db: Session, assignment_id: int):
    return db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()


def get_assignments_by_course(db: Session, course_id: int):
    return db.query(models.Assignment).filter(models.Assignment.course_id == course_id).all()


def create_assignment(db: Session, assignment: schemas.AssignmentCreate):
    db_assignment = models.Assignment(
        name=assignment.name,
        type=assignment.type,
        score=assignment.score,
        max_score=assignment.max_score,
        weight=assignment.weight,
        course_id=assignment.course_id
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


# Grade calculation functions
def calculate_course_grade(db: Session, course_id: int):
    assignments = get_assignments_by_course(db, course_id)

    if not assignments:
        return 0.0

    total_weighted_score = 0.0
    total_weight = 0.0

    for assignment in assignments:
        percentage = (assignment.score / assignment.max_score) * 100
        weighted_score = percentage * (assignment.weight / 100)
        total_weighted_score += weighted_score
        total_weight += assignment.weight

    if total_weight == 0:
        return 0.0

    return total_weighted_score / (total_weight / 100)


def calculate_gpa(db: Session, student_id: int):
    courses = get_courses_by_student(db, student_id)

    if not courses:
        return 0.0

    total_grade_points = 0.0
    total_credits = 0

    for course in courses:
        course_grade = calculate_course_grade(db, course.id)
        grade_point = grade_to_gpa(course_grade)
        total_grade_points += grade_point * course.credits
        total_credits += course.credits

    if total_credits == 0:
        return 0.0

    return total_grade_points / total_credits


def grade_to_gpa(grade: float):
    """Convert percentage grade to 4.0 GPA scale"""
    if grade >= 97:
        return 4.0
    elif grade >= 93:
        return 3.7
    elif grade >= 90:
        return 3.3
    elif grade >= 87:
        return 3.0
    elif grade >= 83:
        return 2.7
    elif grade >= 80:
        return 2.3
    elif grade >= 77:
        return 2.0
    elif grade >= 73:
        return 1.7
    elif grade >= 70:
        return 1.3
    elif grade >= 65:
        return 1.0
    else:
        return 0.0


def predict_final_grade(db: Session, course_id: int, target_grade: float = 90.0):
    assignments = get_assignments_by_course(db, course_id)

    total_weight = sum(assignment.weight for assignment in assignments)
    remaining_weight = 100.0 - total_weight

    if remaining_weight <= 0:
        return {
            "current_grade": calculate_course_grade(db, course_id),
            "predicted_grade": calculate_course_grade(db, course_id),
            "remaining_weight": 0.0,
            "needed_score": None
        }

    current_weighted_score = 0.0
    for assignment in assignments:
        percentage = (assignment.score / assignment.max_score) * 100
        weighted_score = percentage * (assignment.weight / 100)
        current_weighted_score += weighted_score

    needed_score = (target_grade - current_weighted_score) / (remaining_weight / 100)

    return {
        "current_grade": current_weighted_score / ((100 - remaining_weight) / 100) if remaining_weight < 100 else 0,
        "predicted_grade": target_grade if needed_score <= 100 else current_weighted_score + remaining_weight,
        "remaining_weight": remaining_weight,
        "needed_score": max(0, min(100, needed_score))
    }