import pytest
import tempfile
import os
from solution import read_file_chunks

@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)

def test_basic_reading(temp_file):
    with open(temp_file, 'w') as f:
        f.write("line1\nline2\nline3\n")

    result = list(read_file_chunks(temp_file))
    assert result == ["line1", "line2", "line3"]

def test_skip_empty_lines(temp_file):
    with open(temp_file, 'w') as f:
        f.write("line1\n\nline2\n  \nline3\n")

    result = list(read_file_chunks(temp_file))
    assert result == ["line1", "line2", "line3"]

def test_no_final_newline(temp_file):
    with open(temp_file, 'w') as f:
        f.write("line1\nline2")

    result = list(read_file_chunks(temp_file))
    assert result == ["line1", "line2"]

def test_small_chunks(temp_file):
    with open(temp_file, 'w') as f:
        f.write("abcdefghij\nklmnop\nqrs\n")

    result = list(read_file_chunks(temp_file, chunk_size=5))
    assert result == ["abcdefghij", "klmnop", "qrs"]

def test_empty_file(temp_file):
    with open(temp_file, 'w') as f:
        pass

    result = list(read_file_chunks(temp_file))
    assert result == []

def test_whitespace_stripping(temp_file):
    with open(temp_file, 'w') as f:
        f.write("  line1  \n\tline2\t\n")

    result = list(read_file_chunks(temp_file))
    assert result == ["line1", "line2"]

def test_large_lines(temp_file):
    long_line = "x" * 5000
    with open(temp_file, 'w') as f:
        f.write(f"{long_line}\nshort\n")

    result = list(read_file_chunks(temp_file, chunk_size=100))
    assert result == [long_line, "short"]
