
import threading

from classesense.core import STUDENTS_DIR
from classesense.detector import FaceDetector
from classesense.enrollment import StudentEnrollment
from classesense.recognizer import FaceRecognizer
from classesense.attendance import AttendanceManager
from classesense.processor import ClassroomProcessor


class AttendanceService:
    """
    Coordinates the ClassSense AI attendance engine.
    """

    def __init__(self):
        self.detector = None
        self.student_database = {}
        self.recognizer = FaceRecognizer(self.student_database)
        self._initialized = False
        self._initialization_lock = threading.Lock()

    def refresh_student_database(self):
        """Safely rebuild the student database."""
        with self._initialization_lock:
            if self.detector is None:
                self.detector = FaceDetector()

            enrollment = StudentEnrollment(self.detector)
            database = enrollment.build_database(STUDENTS_DIR)

            self.student_database = database
            self.recognizer = FaceRecognizer(self.student_database)
            self._initialized = True

    def ensure_initialized(self):
        """Initialize the AI engine only once."""
        if self._initialized:
            return

        with self._initialization_lock:
            if not self._initialized:
                if self.detector is None:
                    self.detector = FaceDetector()

                enrollment = StudentEnrollment(self.detector)
                database = enrollment.build_database(STUDENTS_DIR)

                self.student_database = database
                self.recognizer = FaceRecognizer(self.student_database)
                self._initialized = True

    def get_students(self):
        """
        Return enrolled student IDs directly from folders.
        Does not initialize the face recognition model.
        """
        STUDENTS_DIR.mkdir(parents=True, exist_ok=True)

        return sorted(
            folder.name
            for folder in STUDENTS_DIR.iterdir()
            if folder.is_dir()
        )

    def create_attendance_session(self):
        self.ensure_initialized()

        attendance = AttendanceManager()
        processor = ClassroomProcessor(
            self.detector,
            self.recognizer,
            attendance
        )

        return attendance, processor

    def process_classroom_image(self, image_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)

        attendance, processor = self.create_attendance_session()
        result = processor.process_image(image_path, output_dir)

        if result is None:
            return None

        absent_students = attendance.get_absent_students(
            self.student_database
        )

        return {
            "image_name": result["image_name"],
            "faces_detected": result["faces_detected"],
            "recognized_students": sorted(attendance.present_students),
            "absent_students": sorted(absent_students),
            "unknown_faces": result["unknown_faces"],
            "total_enrolled": len(self.student_database),
            "output_path": result["output_path"],
        }

    def calculate_image_score(self, result):
        recognized_count = len(result["recognized_students"])
        faces_detected = result["faces_detected"]
        unknown_faces = result["unknown_faces"]

        return (
            recognized_count * 1000
            + faces_detected * 10
            - unknown_faces
        )

    def process_multiple_classroom_images(self, image_paths, output_dir):
        if not image_paths:
            return None

        analyzed_results = []

        for image_path in image_paths:
            result = self.process_classroom_image(
                image_path,
                output_dir
            )

            if result is None:
                continue

            result["image_score"] = self.calculate_image_score(result)
            analyzed_results.append(result)

        if not analyzed_results:
            return None

        best_result = max(
            analyzed_results,
            key=lambda result: result["image_score"]
        )

        best_result["total_images_analyzed"] = len(image_paths)
        best_result["successful_images_analyzed"] = len(analyzed_results)
        best_result["best_image_selected"] = True
        best_result.pop("image_score", None)

        return best_result
