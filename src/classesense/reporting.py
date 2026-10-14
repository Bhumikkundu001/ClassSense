import csv


class CSVReporter:
    """
    Generates CSV attendance reports.
    """

    def save_attendance(
        self,
        output_path,
        present_students,
        absent_students
    ):
        """
        Save final attendance to a CSV file.
        """

        # Ensure the output folder exists
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(
                csv_file
            )

            # CSV header
            writer.writerow([
                "Student_ID",
                "Attendance_Status"
            ])

            # Present students
            for student in sorted(
                present_students
            ):

                writer.writerow([
                    student,
                    "PRESENT"
                ])

            # Absent students
            for student in sorted(
                absent_students
            ):

                writer.writerow([
                    student,
                    "ABSENT"
                ])


        print(
            f"Attendance saved successfully to:\n"
            f"{output_path}"
        )
class SessionReporter:
    """
    Generates a detailed summary report
    for an attendance session.
    """

    def save_summary(
        self,
        output_path,
        processed_images,
        statistics,
        present_students,
        absent_students
    ):
        """
        Save a detailed text summary of the
        attendance session.
        """

        session_name = output_path.parent.name


        with open(
            output_path,
            mode="w",
            encoding="utf-8"
        ) as summary_file:

            summary_file.write(
                "========================================\n"
            )

            summary_file.write(
                "CLASSENSE SESSION SUMMARY\n"
            )

            summary_file.write(
                "========================================\n\n"
            )


            # ----------------------------------------------------
            # SESSION INFORMATION
            # ----------------------------------------------------

            summary_file.write(
                f"Session ID: {session_name}\n\n"
            )


            # ----------------------------------------------------
            # PROCESSING STATISTICS
            # ----------------------------------------------------

            summary_file.write(
                "PROCESSING STATISTICS\n"
            )

            summary_file.write(
                "----------------------------------------\n"
            )

            summary_file.write(
                f"Images successfully processed: "
                f"{len(processed_images)}\n"
            )

            summary_file.write(
                f"Total faces detected: "
                f"{statistics['total_faces']}\n"
            )

            summary_file.write(
                f"Unknown faces: "
                f"{statistics['unknown_faces']}\n\n"
            )


            # ----------------------------------------------------
            # PRESENT STUDENTS
            # ----------------------------------------------------

            summary_file.write(
                "PRESENT STUDENTS\n"
            )

            summary_file.write(
                "----------------------------------------\n"
            )

            summary_file.write(
                f"Total present: "
                f"{len(present_students)}\n"
            )

            for student in sorted(
                present_students
            ):

                summary_file.write(
                    f"{student} -> PRESENT\n"
                )

            summary_file.write("\n")


            # ----------------------------------------------------
            # ABSENT STUDENTS
            # ----------------------------------------------------

            summary_file.write(
                "ABSENT STUDENTS\n"
            )

            summary_file.write(
                "----------------------------------------\n"
            )

            summary_file.write(
                f"Total absent: "
                f"{len(absent_students)}\n"
            )

            for student in sorted(
                absent_students
            ):

                summary_file.write(
                    f"{student} -> ABSENT\n"
                )


        print(
            f"Session summary saved successfully to:\n"
            f"{output_path}"
        )