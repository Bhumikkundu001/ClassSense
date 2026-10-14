from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import (
    TA_CENTER
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


class PDFReportGenerator:
    """
    Generates PDF attendance reports for ClassSense.
    """

    def __init__(
        self,
        output_dir
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    def generate_report(
        self,
        attendance_record
    ):
        """
        Generate a PDF report from an attendance record.
        """

        # ------------------------------------------
        # CREATE PDF FILE NAME
        # ------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        pdf_filename = (
            f"attendance_report_{timestamp}.pdf"
        )

        pdf_path = (
            self.output_dir /
            pdf_filename
        )


        # ------------------------------------------
        # CREATE DOCUMENT
        # ------------------------------------------

        document = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )


        elements = []


        # ------------------------------------------
        # STYLES
        # ------------------------------------------

        styles = (
            getSampleStyleSheet()
        )


        title_style = ParagraphStyle(
            "ClassSenseTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=22,
            spaceAfter=10
        )


        subtitle_style = ParagraphStyle(
            "ClassSenseSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            textColor=colors.grey,
            spaceAfter=25
        )


        section_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            spaceBefore=15,
            spaceAfter=10
        )


        # ------------------------------------------
        # TITLE
        # ------------------------------------------

        elements.append(
            Paragraph(
                "ClassSense Attendance Report",
                title_style
            )
        )


        elements.append(
            Paragraph(
                "AI-Powered Classroom Attendance System",
                subtitle_style
            )
        )


        # ------------------------------------------
        # ATTENDANCE SUMMARY
        # ------------------------------------------

        elements.append(
            Paragraph(
                "Attendance Summary",
                section_style
            )
        )


        present_students = (
            attendance_record.get(
                "present_students",
                attendance_record.get(
                    "recognized_students",
                    []
                )
            )
        )


        absent_students = (
            attendance_record.get(
                "absent_students",
                []
            )
        )


        total_enrolled = (
            attendance_record.get(
                "total_enrolled",
                0
            )
        )


        unknown_faces = (
            attendance_record.get(
                "unknown_faces",
                0
            )
        )


        summary_data = [

            [
                "Total Enrolled",
                str(total_enrolled)
            ],

            [
                "Present Students",
                str(
                    len(
                        present_students
                    )
                )
            ],

            [
                "Absent Students",
                str(
                    len(
                        absent_students
                    )
                )
            ],

            [
                "Unknown Faces",
                str(unknown_faces)
            ]
        ]


        summary_table = Table(
            summary_data,
            colWidths=[
                250,
                150
            ]
        )


        summary_table.setStyle(
            TableStyle(

                [

                    (
                        "GRID",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        1,
                        colors.grey
                    ),

                    (
                        "BACKGROUND",
                        (
                            0,
                            0
                        ),
                        (
                            0,
                            -1
                        ),
                        colors.lightgrey
                    ),

                    (
                        "FONTNAME",
                        (
                            0,
                            0
                        ),
                        (
                            0,
                            -1
                        ),
                        "Helvetica-Bold"
                    ),

                    (
                        "ALIGN",
                        (
                            1,
                            0
                        ),
                        (
                            1,
                            -1
                        ),
                        "CENTER"
                    )

                ]

            )
        )


        elements.append(
            summary_table
        )


        elements.append(
            Spacer(
                1,
                25
            )
        )


        # ------------------------------------------
        # PRESENT STUDENTS
        # ------------------------------------------

        elements.append(
            Paragraph(
                "Present Students",
                section_style
            )
        )


        if present_students:

            present_data = [

                [
                    "S.No.",
                    "Student ID"
                ]

            ]


            for index, student_id in enumerate(
                sorted(
                    present_students
                ),
                start=1
            ):

                present_data.append(

                    [
                        str(index),
                        student_id
                    ]

                )


            present_table = Table(
                present_data,
                colWidths=[
                    80,
                    320
                ]
            )


            present_table.setStyle(
                TableStyle(

                    [

                        (
                            "GRID",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            1,
                            colors.grey
                        ),

                        (
                            "BACKGROUND",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                0
                            ),
                            colors.lightgrey
                        ),

                        (
                            "FONTNAME",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                0
                            ),
                            "Helvetica-Bold"
                        ),

                        (
                            "ALIGN",
                            (
                                0,
                                0
                            ),
                            (
                                0,
                                -1
                            ),
                            "CENTER"
                        )

                    ]

                )
            )


            elements.append(
                present_table
            )


        else:

            elements.append(
                Paragraph(
                    "No students were recognized as present.",
                    styles["Normal"]
                )
            )


        elements.append(
            Spacer(
                1,
                25
            )
        )


        # ------------------------------------------
        # ABSENT STUDENTS
        # ------------------------------------------

        elements.append(
            Paragraph(
                "Absent Students",
                section_style
            )
        )


        if absent_students:

            absent_data = [

                [
                    "S.No.",
                    "Student ID"
                ]

            ]


            for index, student_id in enumerate(
                sorted(
                    absent_students
                ),
                start=1
            ):

                absent_data.append(

                    [
                        str(index),
                        student_id
                    ]

                )


            absent_table = Table(
                absent_data,
                colWidths=[
                    80,
                    320
                ]
            )


            absent_table.setStyle(
                TableStyle(

                    [

                        (
                            "GRID",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            1,
                            colors.grey
                        ),

                        (
                            "BACKGROUND",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                0
                            ),
                            colors.lightgrey
                        ),

                        (
                            "FONTNAME",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                0
                            ),
                            "Helvetica-Bold"
                        ),

                        (
                            "ALIGN",
                            (
                                0,
                                0
                            ),
                            (
                                0,
                                -1
                            ),
                            "CENTER"
                        )

                    ]

                )
            )


            elements.append(
                absent_table
            )


        else:

            elements.append(
                Paragraph(
                    "All enrolled students are present.",
                    styles["Normal"]
                )
            )


        # ------------------------------------------
        # FOOTER
        # ------------------------------------------

        elements.append(
            Spacer(
                1,
                30
            )
        )


        elements.append(
            Paragraph(
                (
                    "Generated by ClassSense • "
                    "AI-Powered Attendance System"
                ),
                subtitle_style
            )
        )


        # ------------------------------------------
        # BUILD PDF
        # ------------------------------------------

        document.build(
            elements
        )


        return pdf_path