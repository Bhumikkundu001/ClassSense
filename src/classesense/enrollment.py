import numpy as np


class StudentEnrollment:
    """
    Builds the student face embedding database
    from enrollment images.
    """

    def __init__(self, detector):

        self.detector = detector


    def build_database(self, students_folder):
        """
        Build a student database from enrollment images.

        Expected structure:

        students_folder/
            Student_1/
                image1.jpg
                image2.jpg
                image3.jpg

            Student_2/
                image1.jpg
                image2.jpg
        """

        student_database = {}

        print("Building student database...\n")


        for student_folder in sorted(
            students_folder.iterdir()
        ):

            if not student_folder.is_dir():
                continue


            embeddings = []


            for image_path in sorted(
                student_folder.glob("*.jpg")
            ):

                embedding = (
                    self.detector
                    .get_largest_face_embedding(
                        image_path
                    )
                )


                if embedding is not None:

                    embeddings.append(
                        embedding
                    )


            if len(embeddings) == 0:

                print(
                    f"Warning: No valid faces found for "
                    f"{student_folder.name}"
                )

                continue


            # Average enrollment embeddings
            reference_embedding = np.mean(
                embeddings,
                axis=0
            )


            # Normalize the averaged embedding
            reference_embedding /= np.linalg.norm(
                reference_embedding
            )


            student_database[
                student_folder.name
            ] = reference_embedding


            print(
                f"Loaded {student_folder.name}: "
                f"{len(embeddings)} images"
            )


        print(
            f"\nTotal enrolled students: "
            f"{len(student_database)}"
        )


        return student_database