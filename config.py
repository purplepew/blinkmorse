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

# Blink data output
BLINK_LOG_PATH = "data/blink_log.csv"