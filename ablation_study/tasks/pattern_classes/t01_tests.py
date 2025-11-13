import pytest
from solution import Counter

def test_default_initialization():
    c = Counter()
    assert c.value == 0

def test_custom_initialization():
    c = Counter(initial=10)
    assert c.value == 10

def test_increment():
    c = Counter()
    c.increment()
    assert c.value == 1
    c.increment()
    assert c.value == 2

def test_increment_by_amount():
    c = Counter()
    result = c.increment(5)
    assert result == 5
    assert c.value == 5

def test_decrement():
    c = Counter(10)
    c.decrement()
    assert c.value == 9
    c.decrement(3)
    assert c.value == 6

def test_negative_values():
    c = Counter()
    c.decrement(5)
    assert c.value == -5

def test_reset():
    c = Counter(5)
    c.increment(10)
    assert c.value == 15
    c.reset()
    assert c.value == 5

def test_history():
    c = Counter(0)
    assert c.get_history() == [0]

    c.increment(5)
    assert c.get_history() == [0, 5]

    c.increment(3)
    assert c.get_history() == [0, 5, 8]

    c.decrement(2)
    assert c.get_history() == [0, 5, 8, 6]

def test_history_after_reset():
    c = Counter(10)
    c.increment(5)
    c.reset()
    history = c.get_history()
    assert history == [10, 15, 10]

def test_multiple_resets():
    c = Counter(0)
    c.increment(10)
    c.reset()
    c.increment(20)
    c.reset()
    assert c.value == 0
    assert c.get_history() == [0, 10, 0, 20, 0]

def test_return_values():
    c = Counter()
    assert c.increment() == 1
    assert c.increment(4) == 5
    assert c.decrement(2) == 3
