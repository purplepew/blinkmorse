
import csv
from pathlib import Path
from random import Random
from collections import Counter
from statistics import fmean, median, pstdev


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SHORT_BLINK_LOG_PATH = DATA_DIR / "short_blink_log.csv"
LONG_BLINK_LOG_PATH = DATA_DIR / "long_blink_log.csv"
CALIBRATION_SIZE = 10
EVALUATION_SEEDS = (42, 43, 44, 45, 46)


def load_blink_samples(log_path, label):
    with log_path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "sample_id": f"{log_path.stem}:{row_number}",
                "duration_ms": float(row["duration_ms"]),
                "label": label,
            }
            for row_number, row in enumerate(csv.DictReader(file), start=1)
        ]


def load_samples():
    short_blinks = load_blink_samples(SHORT_BLINK_LOG_PATH, ".")
    long_blinks = load_blink_samples(LONG_BLINK_LOG_PATH, "-")

    if (len(short_blinks) <= CALIBRATION_SIZE
            or len(long_blinks) <= CALIBRATION_SIZE):
        raise ValueError(
            "Each blink log needs more than 10 samples: "
            "10 are reserved for calibration and the rest are held out."
        )

    return short_blinks, long_blinks

WINDOW_SIZE = 10
ADAPTATION_MARGIN = 0.20
MINIMUM_SEPARATION_MS = 50
RANDOM_SEED = 42


class ThresholdModel:
    def __init__(self, boundary_weight, adaptive):
        self.boundary_weight = boundary_weight
        self.adaptive = adaptive

        self.short_samples = []
        self.long_samples = []

        self.short_center = None
        self.long_center = None
        self.threshold = None

    def calibrate(self, short_samples, long_samples):
        self.short_samples = [
            sample["duration_ms"] for sample in short_samples[-WINDOW_SIZE:]
        ]
        self.long_samples = [
            sample["duration_ms"] for sample in long_samples[-WINDOW_SIZE:]
        ]
        self.update()

    def update(self):
        if not self.short_samples or not self.long_samples:
            return

        short_center = median(self.short_samples)
        long_center = median(self.long_samples)

        separation = long_center - short_center

        if separation < MINIMUM_SEPARATION_MS:
            return None

        self.short_center = short_center
        self.long_center = long_center

        self.threshold = (
            short_center
            + separation * self.boundary_weight
        )

    def classify(self, duration_ms):
        if self.threshold is None:
            raise ValueError("Threshold has not been initialized.")

        return "." if duration_ms < self.threshold else "-"

    def adapt(self, duration_ms):
        if not self.adaptive or self.threshold is None:
            return None

        separation = self.long_center - self.short_center
        margin = separation * ADAPTATION_MARGIN

        lower = self.threshold - margin
        upper = self.threshold + margin

        if duration_ms < lower:
            self.short_samples.append(duration_ms)
            self.short_samples = self.short_samples[-WINDOW_SIZE:]
            accepted_group = "short"

        elif duration_ms > upper:
            self.long_samples.append(duration_ms)
            self.long_samples = self.long_samples[-WINDOW_SIZE:]
            accepted_group = "long"

        else:
            return None

        self.update()
        return accepted_group


def prepare_split(seed):
    rng = Random(seed)
    short, long = load_samples()
    rng.shuffle(short)
    rng.shuffle(long)

    calibration_short = short[:CALIBRATION_SIZE]
    calibration_long = long[:CALIBRATION_SIZE]
    test_samples = (
        short[CALIBRATION_SIZE:] + long[CALIBRATION_SIZE:]
    )

    calibration_ids = {
        sample["sample_id"]
        for sample in calibration_short + calibration_long
    }
    test_ids = {sample["sample_id"] for sample in test_samples}
    if calibration_ids & test_ids:
        raise AssertionError("Calibration and test samples overlap.")

    rng.shuffle(test_samples)
    return calibration_short, calibration_long, test_samples


def evaluate(weight, adaptive, calibration_short, calibration_long,
             test_samples):

    model = ThresholdModel(weight, adaptive)
    model.calibrate(calibration_short, calibration_long)

    if model.threshold is None:
        raise ValueError("Calibration failed to produce a threshold.")

    initial_threshold = model.threshold
    correct = 0
    total = len(test_samples)

    confusion = Counter()
    update_log = []

    for sample in test_samples:
        duration_ms = sample["duration_ms"]
        actual = sample["label"]
        # Predict BEFORE adaptation, just as the live system should.
        threshold_before = model.threshold
        predicted = model.classify(duration_ms)

        confusion[(actual, predicted)] += 1

        if predicted == actual:
            correct += 1

        # The label is used only for scoring, never for adaptation.
        accepted_group = model.adapt(duration_ms)
        update_log.append({
            "sample_id": sample["sample_id"],
            "duration_ms": duration_ms,
            "predicted": predicted,
            "threshold_before": threshold_before,
            "threshold_after": model.threshold,
            "accepted_group": accepted_group or "none",
        })

    accuracy = 100 * correct / total if total else 0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "initial_threshold": initial_threshold,
        "final_threshold": model.threshold,
        "confusion": confusion,
        "update_log": update_log,
    }


def print_update_log(result):
    print("\nSeed 42 adaptive update log:")
    print(
        f"{'Sample':<24} {'Duration':>9} {'Predicted':>10} "
        f"{'Before':>10} {'After':>10} {'Accepted':>10}"
    )
    for update in result["update_log"]:
        print(
            f"{update['sample_id']:<24} "
            f"{update['duration_ms']:>9.1f} "
            f"{update['predicted']:>10} "
            f"{update['threshold_before']:>10.1f} "
            f"{update['threshold_after']:>10.1f} "
            f"{update['accepted_group']:>10}"
        )


def main():
    print("=== BlinkMorse Threshold Evaluation Audit ===")
    print(f"Calibration rows per class: {CALIBRATION_SIZE}")
    print(f"Seeds: {', '.join(map(str, EVALUATION_SEEDS))}")
    print("Adaptive model: 40% boundary; control: fixed 45% boundary")
    print()

    adaptive_accuracies = []
    fixed_accuracies = []

    for seed in EVALUATION_SEEDS:
        calibration_short, calibration_long, test_samples = prepare_split(seed)
        adaptive = evaluate(
            0.40, True, calibration_short, calibration_long, test_samples
        )
        fixed = evaluate(
            0.45, False, calibration_short, calibration_long, test_samples
        )
        adaptive_accuracies.append(adaptive["accuracy"])
        fixed_accuracies.append(fixed["accuracy"])

        print(
            f"Seed {seed}: test={len(test_samples):>2} | "
            f"Adaptive 40%={adaptive['accuracy']:>6.2f}% | "
            f"Fixed 45%={fixed['accuracy']:>6.2f}%"
        )

        if seed == 42:
            print_update_log(adaptive)

    print("\nSeed summary:")
    print(
        f"Adaptive 40%: mean={fmean(adaptive_accuracies):.2f}% "
        f"variation={pstdev(adaptive_accuracies):.2f} percentage points"
    )
    print(
        f"Fixed 45%:    mean={fmean(fixed_accuracies):.2f}% "
        f"variation={pstdev(fixed_accuracies):.2f} percentage points"
    )


if __name__ == "__main__":
    main()