import pytest
from solution import transpose

def test_square_matrix():
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    result = transpose(matrix)
    assert result == [
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ]

def test_rectangular_matrix():
    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8]
    ]
    result = transpose(matrix)
    assert result == [
        [1, 5],
        [2, 6],
        [3, 7],
        [4, 8]
    ]

def test_single_row():
    matrix = [[1, 2, 3, 4]]
    result = transpose(matrix)
    assert result == [[1], [2], [3], [4]]

def test_single_column():
    matrix = [[1], [2], [3], [4]]
    result = transpose(matrix)
    assert result == [[1, 2, 3, 4]]

def test_1x1_matrix():
    matrix = [[42]]
    result = transpose(matrix)
    assert result == [[42]]

def test_empty_matrix():
    assert transpose([]) == []

def test_strings():
    matrix = [
        ["a", "b", "c"],
        ["d", "e", "f"]
    ]
    result = transpose(matrix)
    assert result == [
        ["a", "d"],
        ["b", "e"],
        ["c", "f"]
    ]

def test_double_transpose():
    matrix = [
        [1, 2],
        [3, 4],
        [5, 6]
    ]
    result = transpose(transpose(matrix))
    assert result == matrix
