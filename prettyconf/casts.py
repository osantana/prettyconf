import json

from .exceptions import InvalidConfiguration


class AbstractCast(object):
    def __call__(self, value):
        raise NotImplementedError()  # pragma: no cover


class Boolean(AbstractCast):
    default_values = {
        "1": True, "true": True, "yes": True, "y": True, "on": True, "t": True,
        "0": False, "false": False, "no": False, "n": False, "off": False, "f": False
    }

    def __init__(self, values=None):
        self.values = self.default_values
        if isinstance(values, dict):
            self.values.update(values)

    def __call__(self, value):
        try:
            return self.values[str(value).lower()]
        except KeyError:
            raise InvalidConfiguration("Error casting value {!r} to boolean".format(value))


class List(AbstractCast):
    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes

    def _parse(self, string):
        elements = []
        element = []
        quote = ""
        for char in string:
            # open quote
            if char in self.quotes and not quote:
                quote = char
                element.append(char)
                continue

            # close quote
            if char in self.quotes and char == quote:
                quote = ""
                element.append(char)
                continue

            if quote:
                element.append(char)
                continue

            if char == self.delimiter:
                elements.append("".join(element))
                element = []
                continue

            element.append(char)

        # remaining element
        if element:
            elements.append("".join(element))

        return self.cast(e.strip() for e in elements)

    def cast(self, sequence):
        return list(sequence)

    def __call__(self, value):
        return self._parse(value)


class Tuple(List):
    def cast(self, sequence):
        return tuple(sequence)


class Option(AbstractCast):
    """
    Example::
        _INSTALLED_APPS = ("foo", "bar")
        INSTALLED_APPS = config("ENVIRONMENT", default="production", cast=Option({
            "production": _INSTALLED_APPS,
            "local": _INSTALLED_APPS + ("baz",)
        }))
    """

    def __init__(self, options):
        self.options = options

    def __call__(self, value):
        try:
            return self.options[value]
        except KeyError:
            raise InvalidConfiguration("Invalid option {!r}".format(value))


class JSON(AbstractCast):
    def __call__(self, value):
        try:
            return json.loads(value)
        except json.JSONDecodeError as ex:
            raise InvalidConfiguration('Invalid option {!r}'.format(value)) from ex
        except TypeError:
            return value
