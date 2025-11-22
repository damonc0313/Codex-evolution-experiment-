import pytest
from solution import schedule_with_setup


def test_no_setup_costs():
    """All setup costs zero."""
    jobs = [10, 20, 15]
    setup = {(i, j): 0 for i in range(3) for j in range(3) if i != j}
    total, order = schedule_with_setup(jobs, setup)
    assert total == 45  # Just sum of processing times
    assert len(order) == 3


def test_minimize_setup():
    """Choose order minimizing setup."""
    jobs = [10, 20]
    setup = {
        (0, 1): 5,
        (1, 0): 10
    }
    total, order = schedule_with_setup(jobs, setup)
    # Order [0, 1]: 10 + 5 + 20 = 35
    # Order [1, 0]: 20 + 10 + 10 = 40
    assert total == 35
    assert order == [0, 1]


def test_single_job():
    """One job - no setup."""
    jobs = [15]
    setup = {}
    total, order = schedule_with_setup(jobs, setup)
    assert total == 15
    assert order == [0]


def test_empty_jobs():
    """No jobs."""
    total, order = schedule_with_setup([], {})
    assert total == 0
    assert order == []


def test_complex_setup():
    """Multiple jobs with varying setup costs."""
    jobs = [10, 20, 30]
    setup = {
        (0, 1): 5, (0, 2): 3,
        (1, 0): 5, (1, 2): 2,
        (2, 0): 3, (2, 1): 2
    }
    total, order = schedule_with_setup(jobs, setup)
    # Should find good order
    assert total > 0
    assert len(order) == 3
    assert set(order) == {0, 1, 2}


def test_all_jobs_scheduled():
    """Every job appears exactly once."""
    jobs = [5, 10, 15, 20]
    setup = {(i, j): 1 for i in range(4) for j in range(4) if i != j}
    _, order = schedule_with_setup(jobs, setup)
    assert len(order) == 4
    assert set(order) == {0, 1, 2, 3}
