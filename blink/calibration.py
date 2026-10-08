class Calibration:

    SHORT_TARGET = 10
    LONG_TARGET = 10

    def __init__(
        self,
        adaptive_threshold,
        minimum_duration_ms=80,
        maximum_duration_ms=1200
    ):
        self.adaptive_threshold = adaptive_threshold
        self.minimum_duration_ms = minimum_duration_ms
        self.maximum_duration_ms = maximum_duration_ms

        self.phase = "SHORT"
        self.completed = False

        self.short_count = 0
        self.long_count = 0

    def add_blink(self, duration_ms):

        if self.completed:
            return False

        if not (
            self.minimum_duration_ms
            <= duration_ms
            <= self.maximum_duration_ms
        ):
            return False

        if self.phase == "SHORT":

            self.adaptive_threshold.add_short_blink(
                duration_ms
            )

            self.short_count += 1

            if self.short_count >= self.SHORT_TARGET:
                self.phase = "LONG"

        elif self.phase == "LONG":

            self.adaptive_threshold.add_long_blink(
                duration_ms
            )

            self.long_count += 1

            if self.long_count >= self.LONG_TARGET:
                if self._has_reasonable_separation():
                    self.completed = True
                    self.phase = "READY"
                else:
                    self.long_count = self.LONG_TARGET - 1

        return True

    def _has_reasonable_separation(self):

        short_center = self.adaptive_threshold.get_short_center()
        long_center = self.adaptive_threshold.get_long_center()

        if short_center is None or long_center is None:
            return False

        separation = long_center - short_center

        return (
            long_center > short_center
            and separation >= self.adaptive_threshold.minimum_separation_ms
        )

    def is_complete(self):
        return self.completed

    def get_phase(self):
        return self.phase

    def get_progress(self):

        if self.phase == "SHORT":
            return (
                self.short_count,
                self.SHORT_TARGET
            )

        if self.phase == "LONG":
            return (
                self.long_count,
                self.LONG_TARGET
            )

        return (
            self.LONG_TARGET,
            self.LONG_TARGET
        )