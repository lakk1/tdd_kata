import pytest
from string_add import add


def test_empty_string():
    assert add("") == 0


def test_single_number():
    assert add("1") == 1


def test_two_numbers():
    assert add("1,2") == 3


def test_multiple_numbers():
    assert add("1,2,3,45") == 51


def test_newline_as_delimiter():
    assert add("1\n2,3") == 6
    assert add("1\n2\n3") == 6


def test_custom_delimiter():
    assert add("//;\n1;2") == 3
    assert add("//.\n1.2.3") == 6
    assert add("//|\n1|2|3") == 6
    assert add("//-\n1-2-3") == 6


def test_negative_numbers():
    with pytest.raises(ValueError, match=r"negatives not allowed: \[-1\]"):
        add("1,-1")
    with pytest.raises(ValueError, match=r"negatives not allowed: \[-2, -3\]"):
        add("1,-2,-3")


def test_ignore_numbers_above_1000():
    assert add("2,1001") == 2
    assert add("1000,999,2") == 2001
    assert add("1000,1001,2") == 1002


def test_custom_delimiter_any_length():
    assert add("//[***]\n1***2***3") == 6
    assert add("//[;;]\n1;;2;;3") == 6
    assert add("//[---]\n1---2---3") == 6


def test_multiple_delimiters():
    assert add("//[*][%]\n1*2%3") == 6
    assert add("//[***][%%%]\n1***2%%%3") == 6
    assert add("//[;][|]\n1;2|3") == 6
