from blink.adaptive_threshold import AdaptiveThreshold


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
    115,
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
    907,
]


adaptive = AdaptiveThreshold(
    window_size=10,
    minimum_separation_ms=50
)


for duration in short_blinks:
    adaptive.add_short_blink(duration)


for duration in long_blinks:
    adaptive.add_long_blink(duration)


print()
print("=== Adaptive Threshold Test ===")
print()

print(
    f"Short center : "
    f"{adaptive.get_short_center():.2f} ms"
)

print(
    f"Long center  : "
    f"{adaptive.get_long_center():.2f} ms"
)

print(
    f"Threshold    : "
    f"{adaptive.get_threshold():.2f} ms"
)

print()

test_durations = [
    200,
    300,
    350,
    400,
    450,
    500,
    550,
    600,
    700,
    800,
    900,
]


print("Duration → Classification → Confidence")
print("---------------------------------------")

for duration in test_durations:

    classification = adaptive.classify(
        duration
    )

    confidence = adaptive.get_confidence(
        duration
    )

    print(
        f"{duration:4d} ms → "
        f"{classification} "
        f"→ {confidence:.2f}"
    )