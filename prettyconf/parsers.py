from typing import Union, Tuple, Iterator

STATE_INITIAL = "initial"
STATE_PARSING_KEY = "parsing_key"
STATE_PARSING_VALUE = "parsing_value"
STATE_PARSING_VALUE_ESCAPE = "parsing_value_escape"
STATE_PARSING_COMMENT = "parsing_comment"

COMMENT = "#"
END_OF_LINE = "\n"
ESCAPE_CHAR = "\\"
SPACES = set(" \n")
QUOTES = set("'\"")


class BufferedStreamReader:
    BUFFER_SIZE = 1024

    def __init__(self, stream):
        self.stream = stream
        self.buffer = stream.read(self.BUFFER_SIZE)
        self.position = 0

    def read_char(self):
        if self._is_buffer_depleted():
            self._fill_buffer()
            if not self.buffer:
                return None

        char = self.buffer[self.position]
        self.position += 1
        return char

    def _is_buffer_depleted(self):
        return self.position >= len(self.buffer)

    def _fill_buffer(self):
        self.buffer = self.stream.read(self.BUFFER_SIZE)
        self.position = 0


class EnvFileParser:
    def __init__(self, stream):
        self.state = STATE_INITIAL
        self._stream = BufferedStreamReader(stream)

        self._current_key = []
        self._current_value = []
        self._current_quote = ""
        self._key_parsed = False

    def parse_config(self) -> Iterator[Tuple[str, str]]:
        key = self._current_key
        value = self._current_value

        while True:
            char = self._stream.read_char()
            if not char:
                if key or value:
                    yield self._return_current_config()
                break

            if self._process_initial(char):
                continue

            if self._process_quotes(char):
                continue

            if self._start_comment(char):
                continue

            parsed_value = self._finish_comment(char)
            if parsed_value:
                if isinstance(parsed_value, tuple):
                    yield parsed_value
                continue

            if self._parse_key(char):
                continue

            parsed_value = self._parse_value(char)
            if parsed_value:
                if isinstance(parsed_value, tuple):
                    yield parsed_value
                continue

            if self._parse_escaped_value(char):
                continue

    def _start_comment(self, char):
        if char == COMMENT and (not self._current_quote or self.state == STATE_INITIAL):
            self.state = STATE_PARSING_COMMENT
            return True

        return False

    def _finish_comment(self, char) -> Union[bool, Tuple[str, str]]:
        if not (self.state == STATE_PARSING_COMMENT and char == END_OF_LINE):
            return False

        if not (self._current_key or self._current_value) or not self._key_parsed:
            # Key started with a comment
            self._reset_state()
            return True

        return self._return_current_config()

    def _process_quotes(self, char):
        if char not in QUOTES:
            return False
        if not self._current_quote:
            self._current_quote = char
            return True

        if self._current_quote == char:
            self._current_quote = ""
            return True

        self._current_value.append(char)
        return True

    def _process_initial(self, char):
        if self.state != STATE_INITIAL:
            return False

        if self._start_comment(char):
            return True

        if char in SPACES:
            return True

        self._current_key.append(char)
        self.state = STATE_PARSING_KEY
        return True

    def _parse_key(self, char):
        if self.state != STATE_PARSING_KEY:
            return False

        if char == "=":
            self.state = STATE_PARSING_VALUE
            self._key_parsed = True
            return True

        if char == END_OF_LINE:
            self._reset_state()
            return True

        self._current_key.append(char)
        return True

    def _parse_value(self, char) -> Union[bool, Tuple[str, str]]:
        if self.state != STATE_PARSING_VALUE:
            return False

        if char == ESCAPE_CHAR:
            self.state = STATE_PARSING_VALUE_ESCAPE
            return True

        if char == " " and not (self._current_value or self._current_quote):
            return True

        if char == END_OF_LINE:
            return self._return_current_config()

        self._current_value.append(char)
        return True

    def _parse_escaped_value(self, char):
        if self.state != STATE_PARSING_VALUE_ESCAPE:
            return False

        if char == END_OF_LINE:
            # resume value parsing on the next line
            self.state = STATE_PARSING_VALUE
            return True

        # That was a literal \
        self.state = STATE_PARSING_VALUE
        self._current_value.extend([ESCAPE_CHAR, char])
        return True

    def _return_current_config(self) -> Tuple[str, str]:
        key, value = "".join(self._current_key), "".join(self._current_value)
        self._reset_state()
        return key.rstrip(), value.rstrip()

    def _reset_state(self):
        self.state = STATE_INITIAL
        self._current_key.clear()
        self._current_value.clear()
        self._key_parsed = False
