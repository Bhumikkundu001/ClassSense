from pathlib import Path
import re
import shutil
from typing import List

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form
)
from classesense.reports.pdf_report import (
    PDFReportGenerator
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from classesense.core import STUDENTS_DIR

from classesense.storage.attendance_repository import (
    AttendanceRepository
)

from classesense.services.attendance_service import (
    AttendanceService
)

from classesense.auth.repository import (
    UserRepository
)

from classesense.auth.service import (
    AuthService
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="ClassSense API",
    description="AI-Powered Classroom Attendance System",
    version="2.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://class-sense-alpha.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DIRECTORIES
# --------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


UPLOAD_DIR = (
    PROJECT_ROOT /
    "data" /
    "api_uploads"
)


RESULTS_DIR = (
    PROJECT_ROOT /
    "data" /
    "api_results"
)


ATTENDANCE_FILE = (
    PROJECT_ROOT /
    "data" /
    "attendance_records.json"
)


USER_FILE = (
    PROJECT_ROOT /
    "data" /
    "users.json"
)


REPORTS_DIR = (
    PROJECT_ROOT /
    "data" /
    "reports"
)


# --------------------------------------------------
# CREATE REQUIRED DIRECTORIES
# --------------------------------------------------

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


STUDENTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/results",
    StaticFiles(
        directory=str(
            RESULTS_DIR
        )
    ),
    name="results"
)


app.mount(
    "/reports",
    StaticFiles(
        directory=str(
            REPORTS_DIR
        )
    ),
    name="reports"
)


# --------------------------------------------------
# LOAD CLASSSENSE AI SERVICE
# --------------------------------------------------

attendance_service = (
    AttendanceService()
)


# --------------------------------------------------
# ATTENDANCE STORAGE
# --------------------------------------------------

attendance_repository = (
    AttendanceRepository(
        ATTENDANCE_FILE
    )
)


pdf_report_generator = (
    PDFReportGenerator(
        REPORTS_DIR
    )
)


# --------------------------------------------------
# USER AUTHENTICATION
# --------------------------------------------------

user_repository = (
    UserRepository(
        USER_FILE
    )
)


auth_service = (
    AuthService(
        user_repository
    )
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class RegisterRequest(
    BaseModel
):

    username: str
    password: str
    role: str = "faculty"


class LoginRequest(
    BaseModel
):

    username: str
    password: str


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def validate_student_id(
    student_id
):
    """
    Validate a student ID.

    Only letters, numbers, underscores,
    and hyphens are allowed.
    """

    cleaned_id = (
        student_id.strip()
    )

    if not cleaned_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Student ID cannot be empty."
            )
        )


    if not re.fullmatch(
        r"[A-Za-z0-9_-]+",
        cleaned_id
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Student ID can contain only "
                "letters, numbers, underscores, "
                "and hyphens."
            )
        )


    return cleaned_id


def validate_image_file(
    image
):
    """
    Validate an uploaded image.
    """

    if not image.content_type:

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not determine file type."
            )
        )


    if not image.content_type.startswith(
        "image/"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"{image.filename} is not "
                "a valid image file."
            )
        )


def get_safe_filename(
    filename,
    fallback
):
    """
    Return a safe filename.
    """

    if not filename:

        return fallback


    return Path(
        filename
    ).name


# --------------------------------------------------
# BASIC ENDPOINTS
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": (
            "ClassSense API is running successfully!"
        ),
        "version": "2.0.0"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# STUDENT MANAGEMENT
# --------------------------------------------------

@app.get("/students")
def get_students():

    students = (
        attendance_service
        .get_students()
    )


    return {
        "total_students": len(
            students
        ),

        "students": students
    }


@app.post("/students")
async def add_student(

    student_id: str = Form(...),

    images: List[
        UploadFile
    ] = File(...)

):
    """
    Add a new student with one or more
    reference images.
    """

    student_id = (
        validate_student_id(
            student_id
        )
    )


    if not images:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload at least one "
                "student image."
            )
        )


    student_folder = (
        STUDENTS_DIR /
        student_id
    )


    if student_folder.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                "A student with this ID "
                "already exists."
            )
        )


    student_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    saved_images = []


    try:

        for index, image in enumerate(
            images,
            start=1
        ):

            validate_image_file(
                image
            )


            original_name = (
                get_safe_filename(
                    image.filename,
                    f"image_{index}.jpg"
                )
            )


            suffix = (
                Path(
                    original_name
                )
                .suffix
                .lower()
            )


            if suffix not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]:

                suffix = ".jpg"


            image_path = (
                student_folder /
                f"reference_{index}{suffix}"
            )


            with open(
                image_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer
                )


            saved_images.append(
                image_path.name
            )


        # Rebuild AI student database
        attendance_service.refresh_student_database()


        return {
            "message": (
                "Student added successfully."
            ),

            "student_id": student_id,

            "images_saved": saved_images,

            "total_students": len(
                attendance_service
                .student_database
            )
        }


    except Exception:

        # Remove incomplete student folder
        if student_folder.exists():

            shutil.rmtree(
                student_folder,
                ignore_errors=True
            )


        attendance_service.refresh_student_database()

        raise


    finally:

        for image in images:

            await image.close()


@app.put("/students/{student_id}")
async def update_student(

    student_id: str,

    images: List[
        UploadFile
    ] = File(...)

):
    """
    Replace a student's reference images.
    """

    student_id = (
        validate_student_id(
            student_id
        )
    )


    student_folder = (
        STUDENTS_DIR /
        student_id
    )


    if not student_folder.exists():

        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )


    if not images:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload at least one "
                "new reference image."
            )
        )


    temporary_folder = (
        STUDENTS_DIR /
        f"{student_id}_temporary"
    )


    if temporary_folder.exists():

        shutil.rmtree(
            temporary_folder
        )


    temporary_folder.mkdir(
        parents=True
    )


    saved_images = []


    try:

        for index, image in enumerate(
            images,
            start=1
        ):

            validate_image_file(
                image
            )


            original_name = (
                get_safe_filename(
                    image.filename,
                    f"image_{index}.jpg"
                )
            )


            suffix = (
                Path(
                    original_name
                )
                .suffix
                .lower()
            )


            if suffix not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]:

                suffix = ".jpg"


            image_path = (
                temporary_folder /
                f"reference_{index}{suffix}"
            )


            with open(
                image_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer
                )


            saved_images.append(
                image_path.name
            )


        # Remove old student images
        shutil.rmtree(
            student_folder
        )


        # Replace old folder
        temporary_folder.rename(
            student_folder
        )


        # Rebuild AI database
        attendance_service.refresh_student_database()


        return {
            "message": (
                "Student reference images "
                "updated successfully."
            ),

            "student_id": student_id,

            "images_saved": saved_images
        }


    except Exception:

        if temporary_folder.exists():

            shutil.rmtree(
                temporary_folder,
                ignore_errors=True
            )


        attendance_service.refresh_student_database()

        raise


    finally:

        for image in images:

            await image.close()


@app.delete("/students/{student_id}")
def delete_student(
    student_id: str
):
    """
    Delete a student and all reference images.
    """

    student_id = (
        validate_student_id(
            student_id
        )
    )


    student_folder = (
        STUDENTS_DIR /
        student_id
    )


    if not student_folder.exists():

        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )


    shutil.rmtree(
        student_folder
    )


    # Refresh AI database
    attendance_service.refresh_student_database()


    return {
        "message": (
            "Student deleted successfully."
        ),

        "student_id": student_id,

        "total_students": len(
            attendance_service
            .student_database
        )
    }


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

@app.post("/auth/register")
def register_user(
    request: RegisterRequest
):

    result = (
        auth_service.register_user(
            request.username,
            request.password,
            request.role
        )
    )


    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )


    return result


@app.post("/auth/login")
def login_user(
    request: LoginRequest
):

    result = (
        auth_service.login_user(
            request.username,
            request.password
        )
    )


    if not result["success"]:

        raise HTTPException(
            status_code=401,
            detail=result["message"]
        )


    return result


# --------------------------------------------------
# ATTENDANCE HISTORY
# --------------------------------------------------

@app.get("/attendance/history")
def get_attendance_history(
    date: str = None
):
    """
    Return all attendance records or
    records from a selected date.
    """

    if date:

        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}",
            date
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Date must use "
                    "YYYY-MM-DD format."
                )
            )


        records = (
            attendance_repository
            .get_records_by_date(
                date
            )
        )


    else:

        records = (
            attendance_repository
            .get_all_records()
        )


    return {
        "total_records": len(
            records
        ),

        "records": records
    }


# --------------------------------------------------
# PDF ATTENDANCE REPORTS
# --------------------------------------------------

def find_attendance_record(
    record_id: str
):
    """
    Find an attendance record by its ID.

    This keeps the API compatible with repositories
    that may not yet provide get_record_by_id().
    """

    if hasattr(
        attendance_repository,
        "get_record_by_id"
    ):

        record = (
            attendance_repository
            .get_record_by_id(
                record_id
            )
        )

        if record is not None:

            return record


    records = (
        attendance_repository
        .get_all_records()
    )


    for record in records:

        if str(
            record.get(
                "id",
                ""
            )
        ) == str(record_id):

            return record


    return None


@app.get(
    "/attendance/report/latest"
)
def download_latest_attendance_report():
    """
    Generate and download a PDF report for the
    latest attendance record.
    """

    records = (
        attendance_repository
        .get_all_records()
    )


    if not records:

        raise HTTPException(
            status_code=404,
            detail=(
                "No attendance records are available."
            )
        )


    record = records[-1]


    pdf_path = (
        pdf_report_generator
        .generate_report(
            record
        )
    )


    return FileResponse(
        path=str(
            pdf_path
        ),
        media_type="application/pdf",
        filename=pdf_path.name
    )


@app.get(
    "/attendance/report/{record_id}"
)
def download_attendance_report(
    record_id: str
):
    """
    Generate and download a PDF attendance report
    for a specific attendance record.
    """

    record = (
        find_attendance_record(
            record_id
        )
    )


    if record is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Attendance record not found."
            )
        )


    pdf_path = (
        pdf_report_generator
        .generate_report(
            record
        )
    )


    return FileResponse(
        path=str(
            pdf_path
        ),
        media_type="application/pdf",
        filename=pdf_path.name
    )


# --------------------------------------------------
# SINGLE IMAGE ATTENDANCE PROCESSING
# --------------------------------------------------

@app.post("/attendance")
async def process_attendance(

    image: UploadFile = File(...)

):
    """
    Process one classroom image.
    """

    try:

        # Validate image
        validate_image_file(
            image
        )


        # Safe filename
        safe_filename = (
            get_safe_filename(
                image.filename,
                "classroom_image.jpg"
            )
        )


        # Create upload path
        upload_path = (
            UPLOAD_DIR /
            safe_filename
        )


        # Save uploaded image
        with open(
            upload_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                image.file,
                buffer
            )


        # Process classroom image
        result = (
            attendance_service
            .process_classroom_image(
                upload_path,
                RESULTS_DIR
            )
        )


        if result is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not process "
                    "the uploaded image."
                )
            )


        # Save attendance record
        saved_record = (
            attendance_repository
            .save_attendance(
                result
            )
        )


        return {

            "record_id": (
                saved_record.get(
                    "id"
                )
            ),

            "timestamp": (
                saved_record.get(
                    "timestamp"
                )
            ),

            "image_name": result[
                "image_name"
            ],

            "faces_detected": result[
                "faces_detected"
            ],

            "total_enrolled": result[
                "total_enrolled"
            ],

            "recognized_students": sorted(
                result[
                    "recognized_students"
                ]
            ),

            "absent_students": sorted(
                result[
                    "absent_students"
                ]
            ),

            "unknown_faces": result[
                "unknown_faces"
            ],

            "result_image": (
                f"/results/"
                f"{result['output_path'].name}"
            )
        }


    finally:

        await image.close()


# --------------------------------------------------
# MULTIPLE IMAGE ATTENDANCE PROCESSING
# AUTOMATIC BEST IMAGE SELECTION
# --------------------------------------------------

@app.post("/attendance/multiple")
async def process_multiple_attendance(
    images: List[UploadFile] = File(...)
):
    """
    Process multiple classroom images.

    ClassSense automatically analyzes all images
    and selects the best image based on:

    1. Number of recognized students
    2. Number of detected faces
    3. Number of unknown faces
    """

    if not images:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload at least one image."
            )
        )


    uploaded_paths = []


    try:

        # ----------------------------------------------
        # VALIDATE AND SAVE ALL IMAGES
        # ----------------------------------------------

        for index, image in enumerate(
            images,
            start=1
        ):

            validate_image_file(
                image
            )


            original_name = (
                get_safe_filename(
                    image.filename,
                    f"classroom_{index}.jpg"
                )
            )


            # Add index to prevent files with the same
            # name from overwriting each other.
            upload_filename = (
                f"{index}_{original_name}"
            )


            upload_path = (
                UPLOAD_DIR /
                upload_filename
            )


            with open(
                upload_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer
                )


            uploaded_paths.append(
                upload_path
            )


        # ----------------------------------------------
        # PROCESS ALL IMAGES
        # ----------------------------------------------

        result = (
            attendance_service
            .process_multiple_classroom_images(
                uploaded_paths,
                RESULTS_DIR
            )
        )


        # ----------------------------------------------
        # HANDLE PROCESSING FAILURE
        # ----------------------------------------------

        if result is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not process any of the "
                    "uploaded classroom images."
                )
            )


        # ----------------------------------------------
        # SAVE ONLY THE BEST RESULT
        # ----------------------------------------------

        saved_record = (
            attendance_repository
            .save_attendance(
                result
            )
        )


        # ----------------------------------------------
        # RETURN BEST RESULT
        # ----------------------------------------------

        return {

            "record_id": (
                saved_record.get(
                    "id"
                )
            ),

            "timestamp": (
                saved_record.get(
                    "timestamp"
                )
            ),

            "best_image": result[
                "image_name"
            ],

            "total_images_analyzed": result.get(
                "total_images_analyzed",
                len(uploaded_paths)
            ),

            "successful_images_analyzed": result.get(
                "successful_images_analyzed",
                1
            ),

            "best_image_selected": result.get(
                "best_image_selected",
                True
            ),

            "faces_detected": result[
                "faces_detected"
            ],

            "total_enrolled": result[
                "total_enrolled"
            ],

            "recognized_students": sorted(
                result[
                    "recognized_students"
                ]
            ),

            "absent_students": sorted(
                result[
                    "absent_students"
                ]
            ),

            "unknown_faces": result[
                "unknown_faces"
            ],

            "result_image": (
                f"/results/"
                f"{result['output_path'].name}"
            )
        }


    finally:

        # Close all uploaded files
        for image in images:

            await image.close()