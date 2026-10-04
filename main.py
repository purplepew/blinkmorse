import cv2
import time

from config import (
    CAMERA_INDEX,
    STATIC_BLINK_THRESHOLD,
    BLINK_LOG_PATH,
)

from vision.face_landmarker import FaceLandmarker
from vision.ear import calculate_average_ear
from blink.detector import BlinkDetector
from blink.logger import BlinkLogger


def main():
    # --------------------------------------------------------
    # Initialize components
    # --------------------------------------------------------
    face_landmarker = FaceLandmarker()
    blink_logger = BlinkLogger(BLINK_LOG_PATH)
    blink_detector = BlinkDetector(STATIC_BLINK_THRESHOLD)
    blink_count = 0

    # --------------------------------------------------------
    # Open webcam
    # --------------------------------------------------------
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------
    while cap.isOpened():
        success, frame = cap.read()
        timestamp_ms = int(time.monotonic() * 1000)

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # ----------------------------------------------------
        # MediaPipe
        # ----------------------------------------------------
        results = face_landmarker.detect(frame, timestamp_ms)

        # ----------------------------------------------------
        # Face detected
        # ----------------------------------------------------
        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]

            # ------------------------------------------------
            # EAR
            # ------------------------------------------------
            ear, left_eye, right_eye = calculate_average_ear(
                face_landmarks,
                width,
                height,
            )

            # ------------------------------------------------
            # Draw eye landmarks
            # ------------------------------------------------
            for x, y in left_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            for x, y in right_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # ------------------------------------------------
            # Display EAR
            # ------------------------------------------------
            cv2.putText(
                frame,
                f"EAR: {ear:.3f}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                2,
            )

            # ------------------------------------------------
            # Blink detection
            # ------------------------------------------------
            (
                blink_started,
                blink_ended,
                blink_duration,
            ) = blink_detector.update(ear, timestamp_ms)

            # ------------------------------------------------
            # Show blink status
            # ------------------------------------------------
            if blink_detector.is_closed:
                cv2.putText(
                    frame,
                    "EYE CLOSED",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3,
                )

            # ------------------------------------------------
            # Completed blink
            # ------------------------------------------------
            if blink_ended:
                blink_count += 1
                blink_logger.log_blink(blink_count, blink_duration)
                print(f"Blink #{blink_count}: {blink_duration} ms")
                cv2.putText(
                    frame,
                    f"BLINK #{blink_count}: {blink_duration} ms",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
        else:
            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 165, 255),
                2,
            )

        # ----------------------------------------------------
        # Show camera
        # ----------------------------------------------------
        cv2.imshow("BlinkMorse", frame)

        # Q = quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------
    cap.release()
    cv2.destroyAllWindows()
    face_landmarker.close()


if __name__ == "__main__":
    main()