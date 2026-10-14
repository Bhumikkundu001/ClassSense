import cv2

from classesense.core import (
    REAL_STUDENTS_DIR,
    CLASSROOM_DIR,
    CLASSROOM_RESULTS_DIR,
)

from classesense.detector import FaceDetector
from classesense.enrollment import StudentEnrollment
from classesense.recognizer import FaceRecognizer
from classesense.attendance import AttendanceManager
from classesense.reporting import CSVReporter


def main():

    # ============================================================
    # LOAD FACE DETECTOR
    # ============================================================

    detector = FaceDetector()


    # ============================================================
    # BUILD REAL STUDENT DATABASE
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
    # CREATE ATTENDANCE MANAGER
    # ============================================================

    attendance = AttendanceManager()


    # ============================================================
    # FIND CLASSROOM IMAGES
    # ============================================================

    image_paths = sorted(
        CLASSROOM_DIR.glob("*.jpg")
    )

    if not image_paths:

        print(
            "\nERROR: No classroom images found."
        )

        print(
            f"Please check:\n{CLASSROOM_DIR}"
        )

        return


    # Create output folder once
    CLASSROOM_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    print("\n========================================")
    print("REAL CLASSENSE ATTENDANCE SESSION")
    print("========================================")

    print(
        f"\nClassroom images found: "
        f"{len(image_paths)}"
    )


    # ============================================================
    # PROCESS ALL CLASSROOM IMAGES
    # ============================================================

    for image_path in image_paths:

        print("\n========================================")
        print(
            f"PROCESSING: {image_path.name}"
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


        # Detect all faces
        faces = detector.detect_faces(
            image
        )

        print(
            f"Faces detected: "
            f"{len(faces)}"
        )


        image_matches = set()
        image_unknown_count = 0


        # ========================================================
        # PROCESS EACH FACE
        # ========================================================

        for index, face in enumerate(
            faces,
            start=1
        ):

            embedding = face.normed_embedding

            person, score, decision = (
                recognizer.recognize_face(
                    embedding
                )
            )

            attendance.process_result(
                person,
                decision
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


            # Bounding box
            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox


            # ====================================================
            # MATCH
            # ====================================================

            if decision == "MATCH":

                image_matches.add(
                    person
                )

                label = (
                    f"{person} "
                    f"({score:.2f})"
                )

                color = (
                    0,
                    255,
                    0
                )


            # ====================================================
            # UNKNOWN
            # ====================================================

            else:

                image_unknown_count += 1

                label = (
                    f"UNKNOWN "
                    f"({score:.2f})"
                )

                color = (
                    0,
                    0,
                    255
                )


            # Draw bounding box
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                2
            )


            # Draw label
            cv2.putText(
                image,
                label,
                (
                    x1,
                    max(y1 - 10, 20)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )


        # ========================================================
        # SAVE ANNOTATED IMAGE
        # ========================================================

        output_path = (
            CLASSROOM_RESULTS_DIR /
            image_path.name
        )

        cv2.imwrite(
            str(output_path),
            image
        )


        # ========================================================
        # IMAGE SUMMARY
        # ========================================================

        print("\n--- IMAGE SUMMARY ---")

        print(
            f"Recognized: "
            f"{len(image_matches)}"
        )

        for person in sorted(
            image_matches
        ):

            print(
                f"{person} -> PRESENT"
            )

        print(
            f"Unknown faces: "
            f"{image_unknown_count}"
        )

        print(
            f"Result saved: "
            f"{output_path}"
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
        f"Classroom images processed: "
        f"{len(image_paths)}"
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
        CLASSROOM_RESULTS_DIR /
        "attendance.csv"
    )

    reporter.save_attendance(
        csv_output_path,
        attendance.present_students,
        absent_students
    )


    print("\n========================================")
    print("REAL CLASSENSE ATTENDANCE COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()