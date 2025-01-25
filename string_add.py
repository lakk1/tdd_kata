def add(val):
    if not val:
        return 0
    numbers = val.split(",")
    parsed_numbers = [int(number) for number in numbers]
    total = sum(parsed_numbers)
    return total
