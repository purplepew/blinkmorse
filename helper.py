import csv
from pathlib import Path

from config import (
    SHORT_BLINK_LOG_PATH,
    LONG_BLINK_LOG_PATH,
)


def load_durations(file_path):
    with Path(file_path).open(newline="", encoding="utf-8") as file:
        return [
            float(row["duration_ms"])
            for row in csv.DictReader(file)
        ]


def initialize_adaptive_threshold(adaptive_threshold):
    short_blinks = load_durations(SHORT_BLINK_LOG_PATH)
    long_blinks = load_durations(LONG_BLINK_LOG_PATH)

    for duration in short_blinks:
        adaptive_threshold.add_short_blink(duration)

    for duration in long_blinks:
        adaptive_threshold.add_long_blink(duration)