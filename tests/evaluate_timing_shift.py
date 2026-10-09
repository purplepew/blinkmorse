
"""Simulated timing-drift evaluation for BlinkMorse.

IMPORTANT:
- Uses previously collected blink durations.
- Timing drift and recovery phases are simulations, not new observations.
- Labels are used only to score predictions, never to update the adaptive model.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from statistics import median

SEED = 42
BOUNDARY_WEIGHT = 0.40
WINDOW_SIZE = 10
MINIMUM_SEPARATION_MS = 50.0
ADAPTIVE_MARGIN_RATIO = 0.20
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SHORT_LOG_PATH = DATA_DIR / "short_blink_log.csv"
LONG_LOG_PATH = DATA_DIR / "long_blink_log.csv"


def load_blink_durations(log_path):
    """Load labeled blink durations from a BlinkLogger-compatible CSV."""
    with log_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        try:
            return [float(row["duration_ms"]) for row in reader]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid blink log format or duration in {log_path}"
            ) from error


def load_samples():
    short_samples = load_blink_durations(SHORT_LOG_PATH)
    long_samples = load_blink_durations(LONG_LOG_PATH)

    if len(short_samples) <= 10 or len(long_samples) <= 10:
        raise ValueError(
            "Each blink log needs more than 10 samples: "
            "10 are reserved for calibration and the rest are held out."
        )

    return short_samples, long_samples


@dataclass
class ThresholdModel:
    short_durations: list[float]
    long_durations: list[float]
    adaptive: bool
    weight: float = BOUNDARY_WEIGHT
    window_size: int = WINDOW_SIZE
    threshold: float = field(init=False)

    def __post_init__(self):
        self.short_durations = self.short_durations[-self.window_size:]
        self.long_durations = self.long_durations[-self.window_size:]
        self.threshold = self.calculate_threshold()

    def calculate_threshold(self) -> float:
        short_center = median(self.short_durations)
        long_center = median(self.long_durations)

        if long_center - short_center < MINIMUM_SEPARATION_MS:
            return (short_center + long_center) / 2

        return short_center + (
            long_center - short_center
        ) * self.weight

    def classify(self, duration_ms: float) -> str:
        return "." if duration_ms < self.threshold else "-"

    def adapt(self, duration_ms: float) -> None:
        """Update from duration only, without consulting the true label."""
        if not self.adaptive:
            return

        short_center = median(self.short_durations)
        long_center = median(self.long_durations)
        separation = long_center - short_center

        if separation < MINIMUM_SEPARATION_MS:
            return

        margin = separation * ADAPTIVE_MARGIN_RATIO
        lower = self.threshold - margin
        upper = self.threshold + margin

        if duration_ms < lower:
            self.short_durations.append(duration_ms)
            self.short_durations = self.short_durations[-self.window_size:]
        elif duration_ms > upper:
            self.long_durations.append(duration_ms)
            self.long_durations = self.long_durations[-self.window_size:]
        else:
            return

        new_short_center = median(self.short_durations)
        new_long_center = median(self.long_durations)

        if new_long_center - new_short_center >= MINIMUM_SEPARATION_MS:
            self.threshold = self.calculate_threshold()


def prepare_data():
    """Seeded calibration split, then a deterministic interleaved test sequence."""
    rng = Random(SEED)

    short, long = load_samples()
    rng.shuffle(short)
    rng.shuffle(long)

    calibration_short = short[:10]
    calibration_long = long[:10]
    heldout_short = short[10:]
    heldout_long = long[10:]

    # Interleave classes to make a reproducible test sequence.
    # This is NOT a reconstruction of the original recording chronology.
    sequence = []
    for i in range(max(len(heldout_short), len(heldout_long))):
        if i < len(heldout_short):
            sequence.append((".", heldout_short[i]))
        if i < len(heldout_long):
            sequence.append(("-", heldout_long[i]))

    return calibration_short, calibration_long, sequence


def make_phases(sequence):
    """Create baseline, simulated drift, and recovery phases."""
    baseline = [(label, duration) for label, duration in sequence]

    # Simulate short blinks getting slower and long blinks getting faster.
    drift = [
        (
            label,
            duration + 60 if label == "." else duration - 80
        )
        for label, duration in sequence
    ]

    # Simulate timing returning to the original observed durations.
    recovery = [(label, duration) for label, duration in sequence]

    return [
        ("Baseline", baseline),
        ("Simulated drift", drift),
        ("Recovery", recovery),
    ]


def score_phase(model, samples):
    correct = 0
    dot_to_dash = 0
    dash_to_dot = 0

    for actual, duration in samples:
        predicted = model.classify(duration)

        if predicted == actual:
            correct += 1
        elif actual == "." and predicted == "-":
            dot_to_dash += 1
        elif actual == "-" and predicted == ".":
            dash_to_dot += 1

        # Adapt only AFTER prediction and without using the label.
        model.adapt(duration)

    total = len(samples)
    accuracy = 100 * correct / total if total else 0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "dot_to_dash": dot_to_dash,
        "dash_to_dot": dash_to_dot,
    }


def main():
    calibration_short, calibration_long, sequence = prepare_data()
    phases = make_phases(sequence)

    fixed = ThresholdModel(
        calibration_short.copy(),
        calibration_long.copy(),
        adaptive=False,
    )
    adaptive = ThresholdModel(
        calibration_short.copy(),
        calibration_long.copy(),
        adaptive=True,
    )

    print("=== BlinkMorse Timing-Shift Evaluation ===")
    print("Timing-shift data: SIMULATED, not new real-world measurements")
    print(f"Calibration: {len(calibration_short)} short, "
          f"{len(calibration_long)} long")
    print(f"Held-out samples per phase: {len(sequence)}")
    print(f"Boundary weight: {BOUNDARY_WEIGHT:.2f}")
    print(f"Initial threshold: {fixed.threshold:.1f} ms")
    print()

    print(
        f"{'Phase':<18} {'Mode':<10} {'Accuracy':>10} "
        f"{'Correct':>10} {'Dot->Dash':>10} {'Dash->Dot':>10} "
        f"{'Start ms':>10} {'End ms':>10}"
    )
    print("-" * 100)

    for phase_name, samples in phases:
        for model_name, model in (("Fixed", fixed), ("Adaptive", adaptive)):
            start_threshold = model.threshold
            result = score_phase(model, samples)

            print(
                f"{phase_name:<18} {model_name:<10} "
                f"{result['accuracy']:>9.2f}% "
                f"{result['correct']:>5}/{result['total']:<4} "
                f"{result['dot_to_dash']:>10} "
                f"{result['dash_to_dot']:>10} "
                f"{start_threshold:>10.1f} "
                f"{model.threshold:>10.1f}"
            )

    print()
    print("Interpretation:")
    print("- Compare fixed vs adaptive accuracy within each phase.")
    print("- Check whether the adaptive threshold moves during simulated drift.")
    print("- A moving threshold alone does not prove better decoding.")
    print("- Recovery is tested after the drift phase, so the adaptive model")
    print("  carries its learned state into recovery.")


if __name__ == "__main__":
    main()