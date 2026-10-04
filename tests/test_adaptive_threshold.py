from blink.adaptive_threshold import AdaptiveThreshold


def main():

    adaptive = AdaptiveThreshold()

    short_blinks = [
        96,
        299,
        241,
        292,
        290,
        304,
        303,
        305,
        351,
        240,
        291,
        290,
        352,
        375,
        364,
        366,
        329,
        415,
        353,
        388,
        358,
        115
    ]

    long_blinks = [
        479,
        481,
        668,
        960,
        936,
        960,
        964,
        803,
        984,
        655,
        772,
        961,
        875,
        768,
        837,
        687,
        959,
        945,
        834,
        527,
        907
    ]

    for duration in short_blinks:
        adaptive.add_short_blink(duration)

    for duration in long_blinks:
        adaptive.add_long_blink(duration)

    print("========== Adaptive Threshold Test ==========")

    print(
        f"Short center : "
        f"{adaptive.short_center:.2f} ms"
    )

    print(
        f"Long center  : "
        f"{adaptive.long_center:.2f} ms"
    )

    print(
        f"Threshold    : "
        f"{adaptive.threshold:.2f} ms"
    )

    print("\nClassification tests:")

    test_durations = [
        200,
        300,
        400,
        500,
        550,
        600,
        800
    ]

    for duration in test_durations:

        result = adaptive.classify(duration)

        print(
            f"{duration} ms -> {result}"
        )

    print("============================================")


if __name__ == "__main__":
    main()