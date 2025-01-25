def add(val):
    if not val:
        return 0

    delimiter = ","
    if val.startswith("//"):
        parts = val.split("\n", 1)
        delimiter = parts[0][2:]
        val = parts[1]

    val = val.replace("\n", delimiter)
    numbers = val.split(delimiter)
    parsed_numbers = [int(number) for number in numbers]
    total = sum(parsed_numbers)
    return total
