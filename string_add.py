import re


def parse_delimiter(val):
    if val.startswith("//"):
        parts = val.split("\n", 1)
        delimiter_part = parts[0][2:]
        if delimiter_part.startswith("[") and delimiter_part.endswith("]"):
            delimiter = re.escape(delimiter_part[1:-1])
        else:
            delimiter = re.escape(delimiter_part)
        return delimiter, parts[1]
    return ",", val


def add(val):
    if not val:
        return 0

    delimiter, val = parse_delimiter(val)
    val = val.replace("\n", delimiter)
    numbers = re.split(delimiter, val)
    parsed_numbers = [int(number) for number in numbers]

    negatives = [num for num in parsed_numbers if num < 0]
    if negatives:
        raise ValueError(f"negatives not allowed: {negatives}")

    filtered_numbers = [num for num in parsed_numbers if num <= 1000]
    total = sum(filtered_numbers)
    return total
