import pytest
from solution import batch_process

def test_exact_batches():
    items = [1, 2, 3, 4, 5, 6]
    result = batch_process(items, batch_size=3)
    assert result == [[1, 2, 3], [4, 5, 6]]
    assert items == []

def test_partial_final_batch():
    items = [1, 2, 3, 4, 5]
    result = batch_process(items, batch_size=3)
    assert result == [[1, 2, 3], [4, 5]]
    assert items == []

def test_single_batch():
    items = [1, 2]
    result = batch_process(items, batch_size=5)
    assert result == [[1, 2]]
    assert items == []

def test_empty_input():
    items = []
    result = batch_process(items)
    assert result == []
    assert items == []

def test_batch_size_one():
    items = ['a', 'b', 'c']
    result = batch_process(items, batch_size=1)
    assert result == [['a'], ['b'], ['c']]
    assert items == []

def test_preserves_order():
    items = list(range(10))
    result = batch_process(items, batch_size=4)
    assert result == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

def test_string_items():
    items = ['alpha', 'beta', 'gamma', 'delta']
    result = batch_process(items, batch_size=2)
    assert result == [['alpha', 'beta'], ['gamma', 'delta']]
