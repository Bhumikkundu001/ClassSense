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

        # Load the face detection model once
        self.detector = FaceDetector()

        # Load the student recognition database
        self.refresh_student_database()


    def refresh_student_database(self):
        """
        Rebuild the student database from the
        enrollment images.

        This is called whenever a student is added,
        updated, or deleted.
        """

        enrollment = StudentEnrollment(
            self.detector
        )

        self.student_database = (
            enrollment.build_database(
                STUDENTS_DIR
            )
        )

        self.recognizer = FaceRecognizer(
            self.student_database
        )


    def get_students(self):
        """
        Return all currently enrolled student IDs.
        """

        return sorted(
            self.student_database.keys()
        )


    def create_attendance_session(self):
        """
        Create the components required for one
        new attendance session.
        """

        attendance = AttendanceManager()

        processor = ClassroomProcessor(
            self.detector,
            self.recognizer,
            attendance
        )

        return (
            attendance,
            processor
        )


    def process_classroom_image(
        self,
        image_path,
        output_dir
    ):
        """
        Process one classroom image and return
        the complete attendance result.
        """

        # Ensure output directory exists
        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Create a fresh attendance session
        attendance, processor = (
            self.create_attendance_session()
        )

        # Process classroom image
        result = processor.process_image(
            image_path,
            output_dir
        )

        if result is None:
            return None

        # Get absent students
        absent_students = (
            attendance.get_absent_students(
                self.student_database
            )
        )

        # Return complete result
        return {
            "image_name": result["image_name"],

            "faces_detected": result["faces_detected"],

            "recognized_students": sorted(
                attendance.present_students
            ),

            "absent_students": sorted(
                absent_students
            ),

            "unknown_faces": result["unknown_faces"],

            "total_enrolled": len(
                self.student_database
            ),

            "output_path": result["output_path"],
        }


    def calculate_image_score(
        self,
        result
    ):
        """
        Calculate a quality score for an analyzed
        classroom image.

        Priority:
        1. More recognized students
        2. More faces detected
        3. Fewer unknown faces
        """

        recognized_count = len(
            result["recognized_students"]
        )

        faces_detected = (
            result["faces_detected"]
        )

        unknown_faces = (
            result["unknown_faces"]
        )

        # Recognition is the most important factor.
        # Face detection is the second factor.
        # Unknown faces reduce the score.
        score = (
            recognized_count * 1000
            +
            faces_detected * 10
            -
            unknown_faces
        )

        return score


    def process_multiple_classroom_images(
        self,
        image_paths,
        output_dir
    ):
        """
        Process multiple classroom images and
        automatically select the best image.

        The best image is selected according to
        recognition performance.
        """

        if not image_paths:
            return None

        analyzed_results = []

        for image_path in image_paths:

            result = self.process_classroom_image(
                image_path,
                output_dir
            )

            # Ignore images that could not be processed
            if result is None:
                continue

            # Calculate image quality score
            score = self.calculate_image_score(
                result
            )

            # Store score temporarily for comparison
            result["image_score"] = score

            analyzed_results.append(
                result
            )

        # No valid images were processed
        if not analyzed_results:
            return None

        # Select the highest-scoring image
        best_result = max(
            analyzed_results,
            key=lambda result: result[
                "image_score"
            ]
        )

        # Store summary information
        best_result["total_images_analyzed"] = len(
            image_paths
        )

        best_result["successful_images_analyzed"] = len(
            analyzed_results
        )

        best_result["best_image_selected"] = True

        # Remove internal score before returning
        best_result.pop(
            "image_score",
            None
        )

        return best_result