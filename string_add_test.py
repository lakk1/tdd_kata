from string_add_test import add


def test_empty_string():
    assert add("") == 0


def test_single_number():
    assert add("1") == 1


def test_two_numbers():
    assert add("1,2") == 3


def test_multiple_numbers():
    assert add("1,2,3,4") == 10
