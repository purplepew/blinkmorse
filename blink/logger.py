import csv
from pathlib import Path
from datetime import datetime


class BlinkLogger:

    HEADER = [
        "blink_number",
        "timestamp",
        "duration_ms",
        "phase"
    ]

    LEGACY_HEADER = [
        "blink_number",
        "timestamp",
        "duration_ms"
    ]

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        # Create parent directory if needed
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Create the CSV file and repair a missing header if needed.
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            self._write_rows([])
        else:
            self._ensure_header()

    def _write_rows(self, rows):
        with open(
            self.file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADER)
            writer.writerows(rows)

    def _ensure_header(self):
        with open(
            self.file_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            rows = list(csv.reader(file))

        if rows and rows[0] == self.HEADER:
            return

        if rows and rows[0] == self.LEGACY_HEADER:
            data_rows = rows[1:]
        else:
            data_rows = rows

        migrated_rows = [
            row if len(row) >= 4 else row + ["calibration"]
            for row in data_rows
        ]
        self._write_rows(migrated_rows)

    def log_blink(self, blink_number, duration_ms, phase):

        timestamp = datetime.now().isoformat(
            timespec="milliseconds"
        )

        with open(
            self.file_path,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                blink_number,
                timestamp,
                duration_ms,
                phase
            ])