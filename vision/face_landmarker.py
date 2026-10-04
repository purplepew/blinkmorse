import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    MODEL_PATH,
    NUM_FACES,
    MIN_FACE_DETECTION_CONFIDENCE,
    MIN_FACE_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)


class FaceLandmarker:

    def __init__(self):

        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=NUM_FACES,
            min_face_detection_confidence=MIN_FACE_DETECTION_CONFIDENCE,
            min_face_presence_confidence=MIN_FACE_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        self.landmarker = vision.FaceLandmarker.create_from_options(
            options
        )

    def detect(self, frame, timestamp_ms):

        rgb_frame = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
        )

        results = self.landmarker.detect_for_video(
            rgb_frame,
            timestamp_ms
        )

        return results

    def close(self):

        self.landmarker.close()