class AttendanceManager:
    """
    Manages attendance results for a classroom session.
    """

    def __init__(self):

        self.present_students = set()

        self.total_faces = 0

        self.total_unknown_faces = 0


    def process_result(self, person, decision):
        """
        Process the recognition result of one detected face.
        """

        self.total_faces += 1


        if decision == "MATCH":

            self.present_students.add(
                person
            )

            return True


        self.total_unknown_faces += 1

        return False


    def get_absent_students(self, student_database):
        """
        Return enrolled students who were not recognized.
        """

        all_students = set(
            student_database.keys()
        )

        absent_students = (
            all_students -
            self.present_students
        )

        return absent_students


    def get_statistics(self, student_database):
        """
        Return final attendance statistics.
        """

        absent_students = self.get_absent_students(
            student_database
        )

        return {
            "total_faces": self.total_faces,
            "present_students": len(
                self.present_students
            ),
            "unknown_faces": self.total_unknown_faces,
            "absent_students": len(
                absent_students
            )
        }