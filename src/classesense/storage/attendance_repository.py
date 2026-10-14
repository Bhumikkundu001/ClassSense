import json

from datetime import datetime
from pathlib import Path
from uuid import uuid4


class AttendanceRepository:
    """
    Handles persistent storage of attendance records.
    """

    def __init__(
        self,
        storage_file
    ):

        self.storage_file = Path(
            storage_file
        )

        self.storage_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    def save_attendance(
        self,
        attendance_data
    ):
        """
        Save one attendance session.
        """

        records = self.get_all_records()

        record = {
            "id": str(
                uuid4()
            ),

            "timestamp": (
                datetime.now().isoformat()
            ),

            "image_name": attendance_data[
                "image_name"
            ],

            "total_enrolled": attendance_data[
                "total_enrolled"
            ],

            "present_students": attendance_data[
                "recognized_students"
            ],

            "absent_students": attendance_data[
                "absent_students"
            ],

            "unknown_faces": attendance_data[
                "unknown_faces"
            ]
        }

        records.append(
            record
        )

        self._write_records(
            records
        )

        return record


    def get_all_records(
        self
    ):
        """
        Return all saved attendance records.

        Latest records are returned first.
        """

        if not self.storage_file.exists():

            return []

        try:

            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []

        if not isinstance(
            records,
            list
        ):

            return []

        # Sort latest attendance first
        return sorted(
            records,
            key=lambda record: record.get(
                "timestamp",
                ""
            ),
            reverse=True
        )


    def get_records_by_date(
        self,
        selected_date
    ):
        """
        Return attendance records for one date.

        selected_date format:
        YYYY-MM-DD
        """

        records = (
            self.get_all_records()
        )

        return [
            record
            for record in records
            if record.get(
                "timestamp",
                ""
            ).startswith(
                selected_date
            )
        ]


    def _write_records(
        self,
        records
    ):
        """
        Write records safely to JSON storage.
        """

        with open(
            self.storage_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=4
            )