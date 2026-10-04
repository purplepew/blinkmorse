import csv
from pathlib import Path
from datetime import datetime


class BlinkLogger:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        # Create parent directory if needed
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Create CSV file and header if it doesn't exist
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:

            with open(
                self.file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "blink_number",
                    "timestamp",
                    "duration_ms"
                ])

    def log_blink(self, blink_number, duration_ms):

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
                duration_ms
            ])