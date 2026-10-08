class BlinkDetector:

    def __init__(
        self,
        threshold,
        minimum_blink_duration_ms=80,
        maximum_blink_duration_ms=1500
    ):
        self.threshold = threshold

        # Prevent extremely short noise from being
        # classified as a blink.
        self.minimum_blink_duration_ms = minimum_blink_duration_ms

        # Prevent a long eye closure from becoming
        # an extremely large blink event.
        self.maximum_blink_duration_ms = maximum_blink_duration_ms

        # Current state
        self.is_closed = False

        # Time when the current blink started
        self.blink_start_time = None

        # Most recently completed blink duration
        self.last_blink_duration_ms = None

    def update(self, ear, timestamp_ms):
        """
        Process one EAR measurement.

        Returns:
            blink_started: True when the eye closes.
            blink_ended: True when the eye opens again.
            duration_ms: Duration of the completed blink.
        """

        blink_started = False
        blink_ended = False
        duration_ms = None

        # ----------------------------------------------------
        # EYE CLOSED
        # ----------------------------------------------------

        if ear < self.threshold:

            # Only trigger once when transitioning
            # from OPEN -> CLOSED.
            if not self.is_closed:

                self.is_closed = True

                self.blink_start_time = timestamp_ms

                blink_started = True

        # ----------------------------------------------------
        # EYE OPEN
        # ----------------------------------------------------

        else:

            # Only trigger when transitioning
            # from CLOSED -> OPEN.
            if self.is_closed:

                self.is_closed = False

                if self.blink_start_time is not None:

                    duration_ms = (
                        timestamp_ms
                        - self.blink_start_time
                    )

                    # Only accept reasonable blink durations.
                    if (
                        self.minimum_blink_duration_ms
                        <= duration_ms
                        <= self.maximum_blink_duration_ms
                    ):

                        self.last_blink_duration_ms = duration_ms

                        blink_ended = True

                self.blink_start_time = None

        return (
            blink_started,
            blink_ended,
            duration_ms
        )