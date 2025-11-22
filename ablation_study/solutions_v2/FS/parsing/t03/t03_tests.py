import pytest
from solution import parse_csv


def test_simple_csv():
    """Basic CSV with no quotes."""
    text = "a,b,c\n1,2,3"
    result = parse_csv(text)
    assert result == [["a", "b", "c"], ["1", "2", "3"]]


def test_quoted_fields():
    """Fields with quotes."""
    text = '"name","age","city"\n"Alice","30","NYC"'
    result = parse_csv(text)
    assert result == [["name", "age", "city"], ["Alice", "30", "NYC"]]


def test_quoted_delimiter():
    """Quoted field containing delimiter."""
    text = 'name,location\nAlice,"New York, NY"'
    result = parse_csv(text)
    assert result == [["name", "location"], ["Alice", "New York, NY"]]


def test_escaped_quotes():
    """Quotes inside quoted fields."""
    text = 'name,nickname\n"Bob","Bob ""The Builder"""'
    result = parse_csv(text)
    assert result == [["name", "nickname"], ["Bob", 'Bob "The Builder"']]


def test_multiline_field():
    """Quoted field with newline."""
    text = 'name,bio\n"Alice","First line\nSecond line"'
    result = parse_csv(text)
    assert result == [["name", "bio"], ["Alice", "First line\nSecond line"]]


def test_empty_fields():
    """Empty fields in CSV."""
    text = "a,b,c\n1,,3"
    result = parse_csv(text)
    assert result == [["a", "b", "c"], ["1", "", "3"]]


def test_trailing_comma():
    """Row ending with comma (empty last field)."""
    text = "a,b,c\n1,2,"
    result = parse_csv(text)
    assert result == [["a", "b", "c"], ["1", "2", ""]]


def test_custom_delimiter():
    """Use different delimiter."""
    text = "a;b;c\n1;2;3"
    result = parse_csv(text, delimiter=";")
    assert result == [["a", "b", "c"], ["1", "2", "3"]]


def test_whitespace_handling():
    """Whitespace around unquoted fields."""
    text = "a , b , c\n 1 , 2 , 3"
    result = parse_csv(text)
    # Should trim whitespace from unquoted fields
    assert result == [["a", "b", "c"], ["1", "2", "3"]]


def test_preserve_quoted_whitespace():
    """Preserve whitespace in quoted fields."""
    text = 'a,b\n" Alice "," Bob "'
    result = parse_csv(text)
    assert result == [["a", "b"], [" Alice ", " Bob "]]


def test_single_column():
    """CSV with one column."""
    text = "name\nAlice\nBob"
    result = parse_csv(text)
    assert result == [["name"], ["Alice"], ["Bob"]]


def test_single_row():
    """CSV with header only."""
    text = "a,b,c"
    result = parse_csv(text)
    assert result == [["a", "b", "c"]]


def test_empty_csv():
    """Empty string."""
    text = ""
    result = parse_csv(text)
    assert result == [] or result == [[""]]


def test_complex_example():
    """Realistic CSV with various features."""
    text = '''name,age,city,note
Alice,30,New York,"Loves ""pizza"""
"Bob ""Bobby""",25,"San Francisco, CA","Works
from home"
Charlie,35,Boston,'''
    result = parse_csv(text)
    assert len(result) == 4
    assert result[0] == ["name", "age", "city", "note"]
    assert result[1] == ["Alice", "30", "New York", 'Loves "pizza"']
    assert result[2] == ['Bob "Bobby"', "25", "San Francisco, CA", "Works\nfrom home"]
    assert result[3] == ["Charlie", "35", "Boston", ""]
