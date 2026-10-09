import cv2
import time


from config import (
    CAMERA_INDEX,
    STATIC_BLINK_THRESHOLD,
    SHORT_BLINK_LOG_PATH,
    LONG_BLINK_LOG_PATH,
    MORSE_CHARACTER_GAP_MS,
    MORSE_WORD_GAP_MS,
)

from vision.face_landmarker import FaceLandmarker
from vision.ear import calculate_average_ear
from blink.detector import BlinkDetector
from blink.logger import BlinkLogger

from blink.calibration import Calibration
from blink.adaptive_threshold import AdaptiveThreshold

from morse.decoder import MorseDecoder

blink_detector = BlinkDetector(
    STATIC_BLINK_THRESHOLD
)

short_blink_logger = BlinkLogger(
    SHORT_BLINK_LOG_PATH
)

long_blink_logger = BlinkLogger(
    LONG_BLINK_LOG_PATH
)

adaptive_threshold = AdaptiveThreshold(
    window_size=10,
    minimum_separation_ms=50
)

calibration = Calibration(
    adaptive_threshold
)

morse_decoder = MorseDecoder()

last_blink_end_time = None

decoded_text = ""

blink_count = 0


def main():
    # --------------------------------------------------------
    # Initialize components
    # --------------------------------------------------------
    face_landmarker = FaceLandmarker()
    short_blink_logger = BlinkLogger(SHORT_BLINK_LOG_PATH)
    long_blink_logger = BlinkLogger(LONG_BLINK_LOG_PATH)
    blink_detector = BlinkDetector(STATIC_BLINK_THRESHOLD)
    blink_count = 0
    last_blink_end_time = None
    decoded_text = ""

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

                duration_ms = blink_duration

                if calibration.is_complete():

                    # Normal Morse operation
                    symbol = adaptive_threshold.classify(
                        duration_ms
                    )
                    adapted = False

                    if symbol is not None:

                        logger = (
                            short_blink_logger
                            if symbol == "."
                            else long_blink_logger
                        )
                        logger.log_blink(
                            blink_count,
                            duration_ms,
                            "post_calibration"
                        )
                        blink_count += 1

                        adapted = adaptive_threshold.adapt(duration_ms)

                        morse_decoder.add_symbol(
                            symbol
                        )

                        print(
                            f"Blink: {duration_ms} ms "
                            f"-> {symbol}"
                        )

                        if adapted:

                            print(
                                "Adaptive update:"
                            )

                            print(
                                f"  Short center: "
                                f"{adaptive_threshold.get_short_center():.0f} ms"
                            )

                            print(
                                f"  Long center: "
                                f"{adaptive_threshold.get_long_center():.0f} ms"
                            )

                            print(
                                f"  Threshold: "
                                f"{adaptive_threshold.get_threshold():.0f} ms"
                            )

                else:

                    # Calibration mode
                    calibration_phase = calibration.get_phase()
                    accepted = calibration.add_blink(
                        duration_ms
                    )

                    if accepted:
                        logger = (
                            short_blink_logger
                            if calibration_phase == "SHORT"
                            else long_blink_logger
                        )
                        logger.log_blink(
                            blink_count,
                            duration_ms,
                            "calibration"
                        )
                        blink_count += 1

                        print(
                            f"Calibration blink: "
                            f"{duration_ms} ms"
                        )
                    else:
                        print(
                            f"Ignored calibration blink: "
                            f"{duration_ms} ms"
                        )

                last_blink_end_time = timestamp_ms
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

        if (
            last_blink_end_time is not None
            and morse_decoder.get_current_symbols()
        ):

            gap = (
                timestamp_ms
                - last_blink_end_time
            )

            if gap >= MORSE_CHARACTER_GAP_MS:

                character = (
                    morse_decoder.finish_character()
                )

                if character is not None:

                    decoded_text += character

                    print(
                        f"Character decoded: "
                        f"{character}"
                    )
            
            

        if not calibration.is_complete():

            phase = calibration.get_phase()

            current, target = calibration.get_progress()

            if phase == "SHORT":

                instruction = "Perform SHORT blinks"

            elif phase == "LONG":

                instruction = "Perform LONG blinks"

            else:

                instruction = "Calibration complete"

            cv2.putText(
                frame,
                "CALIBRATION",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                instruction,
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Progress: {current}/{target}",
                (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        else:

            threshold = adaptive_threshold.get_threshold()
            short_center = adaptive_threshold.get_short_center()
            long_center = adaptive_threshold.get_long_center()

            cv2.putText(
                frame,
                "READY - Morse input",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Threshold: {threshold:.0f} ms",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Short: {short_center:.0f} ms",
                (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Long: {long_center:.0f} ms",
                (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
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