# ============================================================
# BlinkMorse Configuration
# ============================================================

MODEL_PATH = "models/face_landmarker.task"

NUM_FACES = 1

MIN_FACE_DETECTION_CONFIDENCE = 0.5

MIN_FACE_PRESENCE_CONFIDENCE = 0.5

MIN_TRACKING_CONFIDENCE = 0.5

# Temporary static threshold.
# This will eventually be replaced by adaptive thresholding.
STATIC_BLINK_THRESHOLD = 0.22

CAMERA_INDEX = 0

# Labeled blink data output
SHORT_BLINK_LOG_PATH = "data/short_blink_log.csv"
LONG_BLINK_LOG_PATH = "data/long_blink_log.csv"

# Morse timing
MORSE_CHARACTER_GAP_MS = 2500
MORSE_WORD_GAP_MS = 3000