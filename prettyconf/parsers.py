STATE_INITIAL = "initial"
STATE_PARSING_KEY = "parsing_key"
STATE_PARSING_VALUE = "parsing_value"
STATE_PARSING_VALUE_ESCAPE = "parsing_value_escape"
STATE_PARSING_COMMENT = "parsing_comment"

ESCAPE_CHAR = "\\"
SPACES = set(" \n")
QUOTES = set("'\"")


class EnvFileParser:
    BUFFER_SIZE = 1024

    def __init__(self, stream):
        self.stream = stream
        self.buffer = stream.read(self.BUFFER_SIZE)
        self.position = 0
        self.state = STATE_INITIAL

        self._current_key = []
        self._current_value = []
        self._current_quote = ""
        self._key_parsed = False

    def _read_char(self):
        if self.position >= len(self.buffer):
            self.buffer = self.stream.read(self.BUFFER_SIZE)
            if not self.buffer:
                return None
            self.position = 0

        char = self.buffer[self.position]
        self.position += 1
        return char

    def parse_config(self):
        key = self._current_key
        value = self._current_value

        while True:
            char = self._read_char()
            if not char:
                if key or value:
                    yield self._return_current_config()
                break

            if self.state == STATE_INITIAL:
                if char == "#":
                    self.state = STATE_PARSING_COMMENT
                    continue
                if char in SPACES:
                    continue
                key.append(char)
                self.state = STATE_PARSING_KEY
                continue

            if char in QUOTES:
                if not self._current_quote:
                    self._current_quote = char
                    continue
                if self._current_quote == char:
                    self._current_quote = ""
                    continue

                value.append(char)
                continue

            if char == "#" and not self._current_quote:
                self.state = STATE_PARSING_COMMENT
                continue

            if self.state == STATE_PARSING_COMMENT and char == "\n":
                if not (key or value) or not self._key_parsed:
                    # Key started with a comment
                    self._reset_state()
                    continue
                yield self._return_current_config()
                continue

            if self.state == STATE_PARSING_KEY:
                if char == "=":
                    self.state = STATE_PARSING_VALUE
                    self._key_parsed = True
                    continue
                if char == "\n":
                    self._reset_state()
                    continue
                key.append(char)
                continue

            if self.state == STATE_PARSING_VALUE:
                if char == ESCAPE_CHAR:
                    self.state = STATE_PARSING_VALUE_ESCAPE
                    continue

                if char == " " and not (value or self._current_quote):
                    continue

                if char == "\n":
                    yield self._return_current_config()
                    continue

                value.append(char)

            if self.state == STATE_PARSING_VALUE_ESCAPE:
                if char == "\n":
                    self.state = STATE_PARSING_VALUE
                    continue
                else:
                    # That was a literal \
                    self.state = STATE_PARSING_VALUE
                    value.extend([ESCAPE_CHAR, char])
                    continue

    def _return_current_config(self):
        key, value = "".join(self._current_key), "".join(self._current_value)
        self._reset_state()
        return key.rstrip(), value.rstrip()

    def _reset_state(self):
        self.state = STATE_INITIAL
        self._current_key.clear()
        self._current_value.clear()
        self._key_parsed = False
