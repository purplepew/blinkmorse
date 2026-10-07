import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from morse.decoder import MorseDecoder


def main():

    decoder = MorseDecoder()

    test_messages = {
        "....": "H",
        ".": "E",
        ".-..": "L",
        ".-..": "L",
        "---": "O",
    }

    print("========== Morse Decoder Test ==========")

    for symbols, expected in test_messages.items():

        decoder.clear()

        for symbol in symbols:
            decoder.add_symbol(symbol)

        result = decoder.decode_current()

        print(
            f"{symbols} -> {result} "
            f"(expected {expected})"
        )

    print("=========================================")


if __name__ == "__main__":
    main()