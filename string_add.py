import re

MAX_NUMBER = 1000
DEFAULT_DELIMITER = ","
CUSTOM_PREFIX = "//"
START_WITH = "["
ENDS_WITH = "]"
SEPARATOR = "|"
VALIDATION_STRING = "negatives not allowed:"


def parse_delimiter(val):
    if val.startswith(CUSTOM_PREFIX):
        parts = val.split("\n", 1)
        delimiter_part = parts[0][2:]
        if delimiter_part.startswith(START_WITH) and delimiter_part.endswith(ENDS_WITH):
            delimiters = re.findall(r"\[(.*?)\]", delimiter_part)
            delimiter = SEPARATOR.join(map(re.escape, delimiters))
        else:
            delimiter = re.escape(delimiter_part)
        return delimiter, parts[1]
    return DEFAULT_DELIMITER, val


def valid_numbers(delimiter, number_string):
    number_string = number_string.replace("\n", delimiter)
    numbers = re.split(delimiter, number_string)
    return [int(number) for number in numbers]


def validate_negatives(numbers):
    negatives = [num for num in numbers if num < 0]
    if negatives:
        raise ValueError(f"{VALIDATION_STRING} {negatives}")


def add(input_string):
    if not input_string:
        return 0

    delimiter, number_string = parse_delimiter(input_string)

    parsed_numbers = valid_numbers(delimiter, number_string)

    validate_negatives(parsed_numbers)

    filtered_numbers = [num for num in parsed_numbers if num <= MAX_NUMBER]
    total = sum(filtered_numbers)
    return total
