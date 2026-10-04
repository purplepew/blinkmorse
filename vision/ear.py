import math


# MediaPipe Face Landmarker eye indices

LEFT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]

RIGHT_EYE = [
    362,
    385,
    384,
    263,
    373,
    380
]


def euclidean_distance(p1, p2):

    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1]
    )


def calculate_ear(eye_landmarks):

    vertical_1 = euclidean_distance(
        eye_landmarks[1],
        eye_landmarks[5]
    )

    vertical_2 = euclidean_distance(
        eye_landmarks[2],
        eye_landmarks[4]
    )

    horizontal = euclidean_distance(
        eye_landmarks[0],
        eye_landmarks[3]
    )

    if horizontal == 0:
        return 0.0

    return (
        vertical_1 + vertical_2
    ) / (
        2.0 * horizontal
    )


def extract_eye_points(face_landmarks, eye_indices, width, height):

    points = []

    for index in eye_indices:

        landmark = face_landmarks[index]

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

    return points


def calculate_average_ear(face_landmarks, width, height):

    left_eye = extract_eye_points(
        face_landmarks,
        LEFT_EYE,
        width,
        height
    )

    right_eye = extract_eye_points(
        face_landmarks,
        RIGHT_EYE,
        width,
        height
    )

    left_ear = calculate_ear(left_eye)

    right_ear = calculate_ear(right_eye)

    average_ear = (
        left_ear + right_ear
    ) / 2.0

    return average_ear, left_eye, right_eye