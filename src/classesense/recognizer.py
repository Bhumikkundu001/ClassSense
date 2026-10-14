import numpy as np

from classesense.core import MATCH_THRESHOLD


class FaceRecognizer:
    """
    Compares a detected face embedding with the
    enrolled student database.
    """

    def __init__(self, student_database):
        """
        Args:
            student_database:
                Dictionary in the format:

                {
                    "Student_Name": embedding,
                    ...
                }
        """

        self.student_database = student_database


    def recognize_face(self, embedding):
        """
        Find the best matching enrolled student.

        Returns:
            person_name
            similarity_score
            decision
        """

        best_person = None
        best_score = -1.0


        for person_name, reference in self.student_database.items():

            score = float(
                np.dot(
                    embedding,
                    reference
                )
            )

            if score > best_score:

                best_score = score
                best_person = person_name


        if best_score >= MATCH_THRESHOLD:

            return (
                best_person,
                best_score,
                "MATCH"
            )


        return (
            best_person,
            best_score,
            "UNKNOWN"
        )