MORSE_CODE = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",

    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
}


class MorseDecoder:

    def __init__(self):
        self.current_symbols = ""

    def add_symbol(self, symbol):

        if symbol not in (".", "-"):
            return None

        self.current_symbols += symbol

        return self.current_symbols

    def decode_current(self):

        if not self.current_symbols:
            return None

        return MORSE_CODE.get(
            self.current_symbols
        )

    def finish_character(self):

        if not self.current_symbols:
            return None

        character = MORSE_CODE.get(
            self.current_symbols
        )

        self.current_symbols = ""

        return character

    def clear(self):

        self.current_symbols = ""

    def get_current_symbols(self):

        return self.current_symbols