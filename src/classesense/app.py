import cv2

from classesense.core import (
    REAL_STUDENTS_DIR,
    CLASSROOM_DIR,
    create_session_results_dir,
    SUPPORTED_IMAGE_EXTENSIONS,
)

from classesense.detector import FaceDetector
from classesense.enrollment import StudentEnrollment
from classesense.recognizer import FaceRecognizer
from classesense.attendance import AttendanceManager
from classesense.reporting import (
    CSVReporter,
    SessionReporter,
)
from classesense.processor import ClassroomProcessor


def main():

    # ============================================================
    # LOAD FACE DETECTOR
    # ============================================================

    detector = FaceDetector()


    # ============================================================
    # BUILD REAL STUDENT DATABASE
    # ============================================================

    enrollment = StudentEnrollment(detector)

    student_database = enrollment.build_database(
        REAL_STUDENTS_DIR
    )

    if not student_database:

        print(
            "\nERROR: No students were loaded "
            "from the enrollment database."
        )

        print(
            f"Please check the folder:\n"
            f"{REAL_STUDENTS_DIR}"
        )

        return


    # ============================================================
    # CREATE RECOGNITION COMPONENT
    # ============================================================

    recognizer = FaceRecognizer(
        student_database
    )


    # ============================================================
    # CREATE ATTENDANCE MANAGER
    # ============================================================

    attendance = AttendanceManager()
    processor = ClassroomProcessor(
    detector,
    recognizer,
    attendance
)


    # ============================================================
    # FIND CLASSROOM IMAGES
    # ============================================================

    image_paths = sorted(
    image_path
    for extension in SUPPORTED_IMAGE_EXTENSIONS
    for image_path in CLASSROOM_DIR.glob(
        f"*{extension}"
    )
)

    if not image_paths:

        print(
            "\nERROR: No classroom images were found."
        )

        print(
            f"Please add .jpg images to:\n"
            f"{CLASSROOM_DIR}"
        )

        return


    # ============================================================
    # PREPARE RESULTS DIRECTORY
    # ============================================================

    session_results_dir = create_session_results_dir()

    print(
    f"\nSession results will be saved to:\n"
    f"{session_results_dir}"
    )


    print("\n========================================")
    print("CLASSENSE ATTENDANCE SESSION")
    print("========================================")

    print(
        f"\nClassroom images found: "
        f"{len(image_paths)}"
    )


    # ============================================================
    # PROCESS ALL CLASSROOM IMAGES
    # ============================================================

    processed_images = []

    for image_path in image_paths:

        result = processor.process_image(
        image_path,
        session_results_dir
    )

        if result is not None:

            processed_images.append(
            result
        )


    # ============================================================
    # FINAL ATTENDANCE REPORT
    # ============================================================

    absent_students = (
        attendance.get_absent_students(
            student_database
        )
    )

    statistics = attendance.get_statistics(
        student_database
    )


    print("\n========================================")
    print("FINAL CLASS ATTENDANCE")
    print("========================================")

    print(
        f"\nTotal unique students present: "
        f"{len(attendance.present_students)}"
    )

    for person in sorted(
        attendance.present_students
    ):

        print(
            f"{person} -> PRESENT"
        )


    # ============================================================
    # ABSENT STUDENTS
    # ============================================================

    print("\n========================================")
    print("ABSENT STUDENTS")
    print("========================================")

    print(
        f"\nTotal absent students: "
        f"{len(absent_students)}"
    )

    for person in sorted(
        absent_students
    ):

        print(
            f"{person} -> ABSENT"
        )


    # ============================================================
    # FINAL STATISTICS
    # ============================================================

    print("\n========================================")
    print("FINAL STATISTICS")
    print("========================================")

    print(
    f"Classroom images successfully processed: "
    f"{len(processed_images)}"
    )

    print(
        f"Total faces detected: "
        f"{statistics['total_faces']}"
    )

    print(
        f"Unique students recognized: "
        f"{statistics['present_students']}"
    )

    print(
        f"Unknown faces detected: "
        f"{statistics['unknown_faces']}"
    )

    print(
        f"Absent students: "
        f"{statistics['absent_students']}"
    )


    # ============================================================
    # SAVE CSV REPORT
    # ============================================================

    reporter = CSVReporter()

    csv_output_path = (
        session_results_dir /
        "attendance.csv"
    )

    reporter.save_attendance(
        csv_output_path,
        attendance.present_students,
        absent_students
    )
    # ============================================================
    # SAVE SESSION SUMMARY
    # ============================================================

    session_reporter = SessionReporter()

    summary_output_path = (
    session_results_dir /
    "session_summary.txt"
)

    session_reporter.save_summary(
    summary_output_path,
    processed_images,
    statistics,
    attendance.present_students,
    absent_students
)


    print("\n========================================")
    print("CLASSENSE ATTENDANCE COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()