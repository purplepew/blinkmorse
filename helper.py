def initialize_adaptive_threshold(adaptive_threshold):

    short_blinks = [
        96, 299, 241, 292, 290,
        304, 303, 305, 351, 240,
        291, 290, 352, 375, 364,
        366, 329, 415, 353, 388,
        358, 115
    ]

    long_blinks = [
        479, 481, 668, 960, 936,
        960, 964, 803, 984, 655,
        772, 961, 875, 768, 837,
        687, 959, 945, 834, 527,
        907
    ]

    for duration in short_blinks:
        adaptive_threshold.add_short_blink(duration)

    for duration in long_blinks:
        adaptive_threshold.add_long_blink(duration)