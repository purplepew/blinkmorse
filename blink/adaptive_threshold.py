from statistics import median


class AdaptiveThreshold:

    def __init__(
        self,
        window_size=10,
        minimum_separation_ms=50,
        adaptation_margin=0.20
    ):
        self.window_size = window_size
        self.minimum_separation_ms = minimum_separation_ms
        self.adaptation_margin = adaptation_margin

        self.short_durations = []
        self.long_durations = []

        self.short_center = None
        self.long_center = None
        self.threshold = None

    # --------------------------------------------------
    # Calibration samples
    # --------------------------------------------------

    def add_short_blink(self, duration_ms):
        self.short_durations.append(duration_ms)

        if len(self.short_durations) > self.window_size:
            self.short_durations.pop(0)

        self.update()

    def add_long_blink(self, duration_ms):
        self.long_durations.append(duration_ms)

        if len(self.long_durations) > self.window_size:
            self.long_durations.pop(0)

        self.update()

    # --------------------------------------------------
    # Online adaptation
    # --------------------------------------------------

    def adapt(self, duration_ms):

        if self.threshold is None:
            return False

        # Margin around the current threshold.
        # 20% of the distance between the short
        # and long centers.
        margin = (
            self.long_center
            - self.short_center
        ) * self.adaptation_margin

        lower_boundary = (
            self.threshold - margin
        )

        upper_boundary = (
            self.threshold + margin
        )

        # ------------------------------------------
        # Clearly SHORT
        # ------------------------------------------

        if duration_ms < lower_boundary:

            self.short_durations.append(
                duration_ms
            )

            if len(self.short_durations) > self.window_size:
                self.short_durations.pop(0)

            self.update()

            return True

        # ------------------------------------------
        # Clearly LONG
        # ------------------------------------------

        if duration_ms > upper_boundary:

            self.long_durations.append(
                duration_ms
            )

            if len(self.long_durations) > self.window_size:
                self.long_durations.pop(0)

            self.update()

            return True

        # ------------------------------------------
        # Ambiguous
        # ------------------------------------------

        return False

    # --------------------------------------------------
    # Calculate threshold
    # --------------------------------------------------

    def update(self):

        if not self.short_durations:
            return

        if not self.long_durations:
            return

        new_short_center = median(
            self.short_durations
        )

        new_long_center = median(
            self.long_durations
        )

        separation = (
            new_long_center
            - new_short_center
        )

        if separation < self.minimum_separation_ms:
            return

        self.short_center = new_short_center
        self.long_center = new_long_center

        # Weighted adaptive boundary
        self.threshold = (
            self.short_center
            + (
                self.long_center
                - self.short_center
            ) * 0.40
        )

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------

    def classify(self, duration_ms):

        if self.threshold is None:
            return None

        if duration_ms < self.threshold:
            return "."

        return "-"

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    def get_confidence(self, duration_ms):

        if (
            self.short_center is None
            or self.long_center is None
            or self.threshold is None
        ):
            return 0.0

        distance = abs(
            duration_ms - self.threshold
        )

        half_range = (
            self.long_center
            - self.short_center
        ) / 2.0

        if half_range <= 0:
            return 0.0

        confidence = distance / half_range

        return min(confidence, 1.0)

    # --------------------------------------------------
    # Getters
    # --------------------------------------------------

    def get_threshold(self):
        return self.threshold

    def get_short_center(self):
        return self.short_center

    def get_long_center(self):
        return self.long_center

    def get_status(self):

        return {
            "short_center": self.short_center,
            "long_center": self.long_center,
            "threshold": self.threshold,
            "short_samples": len(
                self.short_durations
            ),
            "long_samples": len(
                self.long_durations
            ),
        }