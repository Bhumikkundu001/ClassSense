
from classesense.core import STUDENTS_DIR

from classesense.detector import FaceDetector
from classesense.enrollment import StudentEnrollment
from classesense.recognizer import FaceRecognizer
from classesense.attendance import AttendanceManager
from classesense.processor import ClassroomProcessor


class AttendanceService:
    """
    Coordinates the ClassSense AI attendance engine.

    This service is independent of FastAPI so it can be
    reused by the API, terminal application, or future UI.
    """

    def __init__(self):
        # Defer model loading until the AI engine is needed.
        self.detector = None
        self.student_database = {}
        self.recognizer = FaceRecognizer(self.student_database)
        self._initialized = False

    def refresh_student_database(self):
        """
        Rebuild the student database from enrollment images.
        Initialize the detector only when required.
        """
        if self.detector is None:
            self.detector = FaceDetector()

        enrollment = StudentEnrollment(self.detector)
        self.student_database = enrollment.build_database(STUDENTS_DIR)
        self.recognizer = FaceRecognizer(self.student_database)
        self._initialized = True

    def ensure_initialized(self):
        """Initialize the AI engine when first required."""
        if not self._initialized:
            self.refresh_student_database()

    def get_students(self):
        """Return all currently enrolled student IDs."""
        self.ensure_initialized()
        return sorted(self.student_database.keys())

    def create_attendance_session(self):
        """Create the components required for one attendance session."""
        self.ensure_initialized()

        attendance = AttendanceManager()
        processor = ClassroomProcessor(
            self.detector,
            self.recognizer,
            attendance
        )

        return attendance, processor

    def process_classroom_image(self, image_path, output_dir):
        """Process one classroom image and return the complete result."""
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
        """
        Score an image by prioritizing recognized students,
        then detected faces, while penalizing unknown faces.
        """
        recognized_count = len(result["recognized_students"])
        faces_detected = result["faces_detected"]
        unknown_faces = result["unknown_faces"]

        score = (
            recognized_count * 1000
            + faces_detected * 10
            - unknown_faces
        )

        return score

    def process_multiple_classroom_images(self, image_paths, output_dir):
        """
        Process multiple classroom images and select the
        highest-scoring result.
        """
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

            score = self.calculate_image_score(result)
            result["image_score"] = score
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
