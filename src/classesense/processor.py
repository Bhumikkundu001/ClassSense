import cv2


class ClassroomProcessor:
    """
    Processes classroom images by detecting faces,
    recognizing enrolled students, updating attendance,
    and saving annotated result images.
    """

    def __init__(
        self,
        detector,
        recognizer,
        attendance
    ):

        self.detector = detector
        self.recognizer = recognizer
        self.attendance = attendance


    def process_image(
        self,
        image_path,
        output_dir
    ):
        """
        Process one classroom image.

        Returns:
            Dictionary containing the image processing summary.
        """

        print("\n========================================")
        print(f"PROCESSING: {image_path.name}")
        print("========================================")


        # --------------------------------------------------------
        # READ IMAGE
        # --------------------------------------------------------

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            print("Could not read image.")

            return None


        # --------------------------------------------------------
        # DETECT FACES
        # --------------------------------------------------------

        faces = self.detector.detect_faces(
            image
        )

        print(
            f"Faces detected: "
            f"{len(faces)}"
        )


        image_matches = set()
        image_unknown_count = 0


        # --------------------------------------------------------
        # PROCESS EACH FACE
        # --------------------------------------------------------

        for index, face in enumerate(
            faces,
            start=1
        ):

            embedding = face.normed_embedding


            person, score, decision = (
                self.recognizer.recognize_face(
                    embedding
                )
            )


            # Update overall attendance
            self.attendance.process_result(
                person,
                decision
            )


            print(f"\nFace {index}")
            print(f"Candidate: {person}")
            print(f"Similarity: {score:.4f}")
            print(f"Decision: {decision}")


            # Bounding box
            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox


            # ----------------------------------------------------
            # MATCH
            # ----------------------------------------------------

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


            # ----------------------------------------------------
            # UNKNOWN
            # ----------------------------------------------------

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


        # --------------------------------------------------------
        # SAVE ANNOTATED IMAGE
        # --------------------------------------------------------

        output_path = (
            output_dir /
            image_path.name
        )

        cv2.imwrite(
            str(output_path),
            image
        )


        # --------------------------------------------------------
        # IMAGE SUMMARY
        # --------------------------------------------------------

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


        # --------------------------------------------------------
        # RETURN SUMMARY
        # --------------------------------------------------------

        return {
            "image_name": image_path.name,
            "faces_detected": len(faces),
            "recognized_students": image_matches,
            "unknown_faces": image_unknown_count,
            "output_path": output_path,
        }