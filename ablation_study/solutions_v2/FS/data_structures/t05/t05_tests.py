import pytest
from solution import RollbackDSU


def test_basic_union_find():
    """Simple union and find operations."""
    dsu = RollbackDSU(5)
    dsu.union(0, 1)
    dsu.union(2, 3)

    assert dsu.find(0) == dsu.find(1)
    assert dsu.find(2) == dsu.find(3)
    assert dsu.find(0) != dsu.find(2)


def test_count_sets():
    """Count number of disjoint sets."""
    dsu = RollbackDSU(5)
    assert dsu.count_sets() == 5

    dsu.union(0, 1)
    assert dsu.count_sets() == 4

    dsu.union(2, 3)
    assert dsu.count_sets() == 3

    dsu.union(0, 2)
    assert dsu.count_sets() == 2


def test_union_same_set():
    """Union elements already in same set."""
    dsu = RollbackDSU(5)
    dsu.union(0, 1)
    dsu.union(1, 2)

    # 0 and 2 already connected
    result = dsu.union(0, 2)
    assert result == False  # Already in same set


def test_basic_rollback():
    """Rollback to previous state."""
    dsu = RollbackDSU(5)
    dsu.union(0, 1)
    cp = dsu.checkpoint()

    dsu.union(2, 3)
    dsu.union(0, 2)
    assert dsu.count_sets() == 2

    dsu.rollback(cp)
    assert dsu.count_sets() == 4
    assert dsu.find(0) == dsu.find(1)
    assert dsu.find(2) != dsu.find(3)


def test_multiple_checkpoints():
    """Multiple checkpoints can coexist."""
    dsu = RollbackDSU(5)

    dsu.union(0, 1)
    cp1 = dsu.checkpoint()

    dsu.union(2, 3)
    cp2 = dsu.checkpoint()

    dsu.union(0, 2)
    assert dsu.count_sets() == 2

    # Rollback to cp2
    dsu.rollback(cp2)
    assert dsu.count_sets() == 3

    # Rollback to cp1
    dsu.rollback(cp1)
    assert dsu.count_sets() == 4


def test_rollback_multiple_times():
    """Can rollback to same checkpoint multiple times."""
    dsu = RollbackDSU(5)
    dsu.union(0, 1)
    cp = dsu.checkpoint()

    dsu.union(2, 3)
    dsu.rollback(cp)
    assert dsu.count_sets() == 4

    dsu.union(3, 4)
    dsu.rollback(cp)
    assert dsu.count_sets() == 4


def test_checkpoint_initial_state():
    """Checkpoint before any operations."""
    dsu = RollbackDSU(5)
    cp = dsu.checkpoint()

    dsu.union(0, 1)
    dsu.union(2, 3)
    dsu.union(0, 2)

    dsu.rollback(cp)
    assert dsu.count_sets() == 5  # Back to all separate


def test_transitive_union():
    """Union creates transitive connections."""
    dsu = RollbackDSU(4)
    dsu.union(0, 1)
    dsu.union(1, 2)
    dsu.union(2, 3)

    # All should be in same set
    root = dsu.find(0)
    assert dsu.find(1) == root
    assert dsu.find(2) == root
    assert dsu.find(3) == root


def test_rollback_preserves_earlier():
    """Rollback doesn't affect earlier state."""
    dsu = RollbackDSU(5)

    dsu.union(0, 1)
    cp1 = dsu.checkpoint()

    dsu.union(2, 3)
    cp2 = dsu.checkpoint()

    dsu.union(3, 4)

    dsu.rollback(cp1)
    assert dsu.find(0) == dsu.find(1)
    assert dsu.find(2) != dsu.find(3)


def test_single_element():
    """DSU with one element."""
    dsu = RollbackDSU(1)
    assert dsu.count_sets() == 1
    assert dsu.find(0) == 0


def test_large_dsu():
    """Many elements with rollback."""
    dsu = RollbackDSU(100)

    # Connect 0-9
    for i in range(9):
        dsu.union(i, i+1)

    cp = dsu.checkpoint()

    # Connect 10-19
    for i in range(10, 19):
        dsu.union(i, i+1)

    # Connect the groups
    dsu.union(0, 10)
    assert dsu.count_sets() == 81  # 20 connected, 80 separate

    dsu.rollback(cp)
    assert dsu.count_sets() == 91  # 10 connected, 90 separate


def test_checkpoint_after_rollback():
    """Create checkpoint after rollback."""
    dsu = RollbackDSU(5)
    dsu.union(0, 1)
    cp1 = dsu.checkpoint()

    dsu.union(2, 3)
    dsu.rollback(cp1)

    cp2 = dsu.checkpoint()
    dsu.union(3, 4)

    dsu.rollback(cp2)
    assert dsu.count_sets() == 4  # Back to state after rollback
