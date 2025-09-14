from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Grade Calculator API",
    description="A comprehensive API for calculating GPAs, predicting grades, and tracking academic progress",
    version="1.0.0"
)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Grade Calculator API"}


# Student endpoints
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check if student already exists
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_student = crud.get_student_by_student_id(db, student_id=student.student_id)
    if db_student:
        raise HTTPException(status_code=400, detail="Student ID already registered")

    return crud.create_student(db=db, student=student)


@app.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students


@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.delete("/students/{student_id}", response_model=schemas.DeleteResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    # Check if student exists
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Delete the student (this will also delete related courses and assignments due to CASCADE)
    success = crud.delete_student(db, student_id=student_id)

    if success:
        return schemas.DeleteResponse(
            success=True,
            message=f"Student '{db_student.name}' and all related data deleted successfully",
            deleted_id=student_id
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete student")

# Course endpoints
@app.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # Check if student exists
    db_student = crud.get_student(db, student_id=course.student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    return crud.create_course(db=db, course=course)


@app.get("/courses/{course_id}", response_model=schemas.Course)
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course


@app.delete("/courses/{course_id}", response_model=schemas.DeleteResponse)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    # Check if course exists
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Delete the course (this will also delete related assignments due to CASCADE)
    success = crud.delete_course(db, course_id=course_id)

    if success:
        return schemas.DeleteResponse(
            success=True,
            message=f"Course '{db_course.name}' and all related assignments deleted successfully",
            deleted_id=course_id
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete course")

@app.get("/students/{student_id}/courses", response_model=List[schemas.Course])
def read_student_courses(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    courses = crud.get_courses_by_student(db, student_id=student_id)
    return courses


# Assignment endpoints
@app.post("/assignments/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    # Check if course exists
    db_course = crud.get_course(db, course_id=assignment.course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    return crud.create_assignment(db=db, assignment=assignment)


@app.get("/assignments/{assignment_id}", response_model=schemas.Assignment)
def read_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, assignment_id=assignment_id)
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return db_assignment


@app.delete("/assignments/{assignment_id}", response_model=schemas.DeleteResponse)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    # Check if assignment exists
    db_assignment = crud.get_assignment(db, assignment_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Delete the assignment
    success = crud.delete_assignment(db, assignment_id=assignment_id)

    if success:
        return schemas.DeleteResponse(
            success=True,
            message=f"Assignment '{db_assignment.name}' deleted successfully",
            deleted_id=assignment_id
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete assignment")


@app.get("/courses/{course_id}/assignments", response_model=List[schemas.Assignment])
def read_course_assignments(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    assignments = crud.get_assignments_by_course(db, course_id=course_id)
    return assignments


# Grade calculation endpoints
@app.get("/courses/{course_id}/grade")
def get_course_grade(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    grade = crud.calculate_course_grade(db, course_id=course_id)
    return {
        "course_id": course_id,
        "course_name": db_course.name,
        "current_grade": round(grade, 2)
    }


@app.get("/students/{student_id}/gpa", response_model=schemas.GPAResponse)
def get_student_gpa(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    gpa = crud.calculate_gpa(db, student_id=student_id)
    courses = crud.get_courses_by_student(db, student_id=student_id)
    total_credits = sum(course.credits for course in courses)

    return schemas.GPAResponse(
        student_id=student_id,
        current_gpa=round(gpa, 2),
        total_credits=total_credits,
        courses_count=len(courses)
    )


@app.get("/courses/{course_id}/predict-grade")
def predict_course_grade(course_id: int, target_grade: float = 90.0, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    prediction = crud.predict_final_grade(db, course_id=course_id, target_grade=target_grade)

    return {
        "course_id": course_id,
        "course_name": db_course.name,
        "target_grade": target_grade,
        "current_grade": round(prediction["current_grade"], 2),
        "predicted_final_grade": round(prediction["predicted_grade"], 2),
        "remaining_weight": prediction["remaining_weight"],
        "needed_score_on_remaining": round(prediction["needed_score"], 2) if prediction["needed_score"] else None
    }


@app.get("/students/{student_id}/progress", response_model=schemas.ProgressReport)
def get_student_progress(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    gpa = crud.calculate_gpa(db, student_id=student_id)
    courses = crud.get_courses_by_student(db, student_id=student_id)
    total_credits = sum(course.credits for course in courses)

    course_details = []
    for course in courses:
        grade = crud.calculate_course_grade(db, course.id)
        course_details.append({
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "credits": course.credits,
            "current_grade": round(grade, 2),
            "semester": course.semester,
            "year": course.year
        })

    return schemas.ProgressReport(
        student_id=student_id,
        student_name=db_student.name,
        current_gpa=round(gpa, 2),
        total_credits=total_credits,
        courses=course_details
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)