import csv
import statistics
from pathlib import Path

from config import BLINK_LOG_PATH


def load_blink_durations(file_path):
    durations = []

    path = Path(file_path)

    if not path.exists():
        print(f"ERROR: Log file not found: {path}")
        return durations

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            try:
                duration = float(row["duration_ms"])
                durations.append(duration)
            except (ValueError, KeyError):
                continue

    return durations


def analyze_durations(durations):

    if not durations:
        print("No blink data available.")
        return

    print("\n========== Blink Duration Analysis ==========")

    print(f"Number of blinks : {len(durations)}")
    print(f"Minimum duration : {min(durations):.2f} ms")
    print(f"Maximum duration : {max(durations):.2f} ms")
    print(f"Mean duration    : {statistics.mean(durations):.2f} ms")
    print(f"Median duration  : {statistics.median(durations):.2f} ms")

    if len(durations) >= 2:
        print(
            f"Std. deviation   : "
            f"{statistics.stdev(durations):.2f} ms"
        )
    else:
        print("Std. deviation   : Not enough data")

    print("\nBlink durations:")

    for index, duration in enumerate(durations, start=1):
        print(
            f"Blink #{index}: "
            f"{duration:.2f} ms"
        )

    print("============================================")


def main():

    durations = load_blink_durations(
        BLINK_LOG_PATH
    )

    analyze_durations(durations)


if __name__ == "__main__":
    main()