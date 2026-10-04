class AdaptiveThreshold:

    def __init__(self):
        self.short_durations = []
        self.long_durations = []

        self.short_center = None
        self.long_center = None
        self.threshold = None

    def add_short_blink(self, duration_ms):
        self.short_durations.append(duration_ms)
        self.update()

    def add_long_blink(self, duration_ms):
        self.long_durations.append(duration_ms)
        self.update()

    def update(self):

        if not self.short_durations:
            return

        if not self.long_durations:
            return

        self.short_center = (
            sum(self.short_durations)
            / len(self.short_durations)
        )

        self.long_center = (
            sum(self.long_durations)
            / len(self.long_durations)
        )

        self.threshold = (
            self.short_center
            + self.long_center
        ) / 2.0

    def classify(self, duration_ms):

        if self.threshold is None:
            return None

        if duration_ms < self.threshold:
            return "."

        return "-"

    def get_threshold(self):

        return self.threshold