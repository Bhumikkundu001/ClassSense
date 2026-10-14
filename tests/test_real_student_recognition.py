import cv2

from classesense.core import REAL_STUDENTS_DIR
from classesense.detector import FaceDetector
from classesense.enrollment import StudentEnrollment
from classesense.recognizer import FaceRecognizer


def main():

    # ============================================================
    # LOAD FACE DETECTOR
    # ============================================================

    detector = FaceDetector()


    # ============================================================
    # BUILD DATABASE FROM REAL STUDENTS
    # ============================================================

    enrollment = StudentEnrollment(
        detector
    )

    student_database = enrollment.build_database(
        REAL_STUDENTS_DIR
    )

    if not student_database:

        print(
            "\nERROR: No students were loaded."
        )

        return


    # ============================================================
    # CREATE RECOGNIZER
    # ============================================================

    recognizer = FaceRecognizer(
        student_database
    )


    # ============================================================
    # FIND BU001 TEST IMAGES
    # ============================================================

    test_folder = (
        REAL_STUDENTS_DIR /
        "BU001" /
        "test"
    )

    image_paths = sorted(
        test_folder.glob("*.jpg")
    )


    if not image_paths:

        print(
            "\nERROR: No test images found."
        )

        print(
            f"Please check:\n{test_folder}"
        )

        return


    print("\n========================================")
    print("REAL STUDENT RECOGNITION TEST")
    print("========================================")

    print(
        f"\nTest images found: "
        f"{len(image_paths)}"
    )


    # ============================================================
    # PROCESS EACH TEST IMAGE
    # ============================================================

    for image_path in image_paths:

        print("\n========================================")
        print(
            f"PROCESSING: "
            f"{image_path.name}"
        )
        print("========================================")


        image = cv2.imread(
            str(image_path)
        )


        if image is None:

            print(
                "Could not read image."
            )

            continue


        # Detect every face in the image
        faces = detector.detect_faces(
            image
        )


        print(
            f"\nFaces detected: "
            f"{len(faces)}"
        )


        # ========================================================
        # RECOGNIZE EACH FACE
        # ========================================================

        for index, face in enumerate(
            faces,
            start=1
        ):

            embedding = (
                face.normed_embedding
            )


            person, score, decision = (
                recognizer.recognize_face(
                    embedding
                )
            )


            print(f"\nFace {index}")
            print(
                f"Candidate: {person}"
            )
            print(
                f"Similarity: {score:.4f}"
            )
            print(
                f"Decision: {decision}"
            )


    print("\n========================================")
    print("REAL STUDENT TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()