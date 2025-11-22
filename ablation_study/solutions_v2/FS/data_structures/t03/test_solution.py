import pytest
from solution import IntervalTree


def test_basic_insert_query():
    """Insert and find overlapping intervals."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5, "A")
    id2 = tree.insert(3, 7, "B")

    results = tree.find_overlapping(4, 6)
    ids = {r[0] for r in results}
    assert ids == {id1, id2}


def test_non_overlapping():
    """Intervals that don't overlap."""
    tree = IntervalTree()
    tree.insert(1, 3)
    tree.insert(5, 7)

    results = tree.find_overlapping(4, 4)
    assert len(results) == 0


def test_exact_boundary():
    """Intervals touching at boundary overlap."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5)
    id2 = tree.insert(5, 10)

    results = tree.find_overlapping(5, 5)
    ids = {r[0] for r in results}
    assert ids == {id1, id2}


def test_delete_interval():
    """Delete removes interval from queries."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5, "A")
    id2 = tree.insert(3, 7, "B")

    assert tree.delete(id1) == True
    results = tree.find_overlapping(4, 6)
    assert len(results) == 1
    assert results[0][0] == id2


def test_delete_nonexistent():
    """Delete non-existent ID returns False."""
    tree = IntervalTree()
    tree.insert(1, 5)
    assert tree.delete(999) == False


def test_point_interval():
    """Single point interval [x, x]."""
    tree = IntervalTree()
    id1 = tree.insert(5, 5, "point")

    results = tree.find_overlapping(5, 5)
    assert len(results) == 1
    assert results[0][3] == "point"

    results = tree.find_overlapping(4, 6)
    assert len(results) == 1


def test_contained_interval():
    """Query interval contains stored interval."""
    tree = IntervalTree()
    id1 = tree.insert(3, 5)

    results = tree.find_overlapping(1, 10)
    assert len(results) == 1
    assert results[0][0] == id1


def test_containing_interval():
    """Stored interval contains query interval."""
    tree = IntervalTree()
    id1 = tree.insert(1, 10)

    results = tree.find_overlapping(3, 5)
    assert len(results) == 1
    assert results[0][0] == id1


def test_multiple_overlaps():
    """Multiple intervals overlap with query."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5)
    id2 = tree.insert(3, 7)
    id3 = tree.insert(6, 10)
    id4 = tree.insert(15, 20)

    results = tree.find_overlapping(4, 8)
    ids = {r[0] for r in results}
    assert ids == {id1, id2, id3}


def test_empty_tree():
    """Query on empty tree."""
    tree = IntervalTree()
    results = tree.find_overlapping(1, 10)
    assert len(results) == 0


def test_data_storage():
    """Attached data is preserved."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5, {"name": "interval1", "value": 42})

    results = tree.find_overlapping(3, 3)
    assert results[0][3] == {"name": "interval1", "value": 42}


def test_unique_ids():
    """Each insert gets unique ID."""
    tree = IntervalTree()
    id1 = tree.insert(1, 5)
    id2 = tree.insert(1, 5)  # Same interval
    id3 = tree.insert(2, 6)

    assert len({id1, id2, id3}) == 3  # All unique


def test_large_tree():
    """Performance with many intervals."""
    tree = IntervalTree()
    ids = []
    for i in range(100):
        ids.append(tree.insert(i, i+10))

    # Query middle range
    results = tree.find_overlapping(50, 55)
    assert len(results) >= 10  # Should find multiple overlaps
