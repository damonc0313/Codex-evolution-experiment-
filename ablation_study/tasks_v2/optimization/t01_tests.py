import pytest
from solution import allocate_resources


def test_non_overlapping_tasks():
    """Simple non-overlapping case."""
    tasks = [
        {"start": 0, "end": 3, "resources_needed": 2, "value": 10},
        {"start": 3, "end": 6, "resources_needed": 2, "value": 12}
    ]
    value, selected = allocate_resources(3, tasks)
    assert value == 22
    assert set(selected) == {0, 1}


def test_overlapping_tasks():
    """Must choose one of overlapping tasks."""
    tasks = [
        {"start": 0, "end": 5, "resources_needed": 2, "value": 10},
        {"start": 2, "end": 7, "resources_needed": 2, "value": 15}
    ]
    value, selected = allocate_resources(3, tasks)
    assert value == 15  # Choose task 1
    assert selected == [1]


def test_resource_constraint():
    """Not enough resources for task."""
    tasks = [
        {"start": 0, "end": 3, "resources_needed": 5, "value": 20}
    ]
    value, selected = allocate_resources(3, tasks)
    assert value == 0
    assert selected == []


def test_resource_reuse():
    """Resources freed after task completes."""
    tasks = [
        {"start": 0, "end": 2, "resources_needed": 3, "value": 10},
        {"start": 2, "end": 4, "resources_needed": 3, "value": 12}
    ]
    value, selected = allocate_resources(3, tasks)
    assert value == 22  # Both tasks


def test_optimal_selection():
    """Choose best combination."""
    tasks = [
        {"start": 0, "end": 2, "resources_needed": 1, "value": 5},
        {"start": 1, "end": 3, "resources_needed": 1, "value": 10},
        {"start": 2, "end": 4, "resources_needed": 1, "value": 5}
    ]
    value, selected = allocate_resources(1, tasks)
    assert value == 10  # Choose task 1


def test_empty_tasks():
    """No tasks."""
    value, selected = allocate_resources(5, [])
    assert value == 0
    assert selected == []


def test_sorted_output():
    """Indices returned in sorted order."""
    tasks = [
        {"start": 0, "end": 2, "resources_needed": 1, "value": 5},
        {"start": 2, "end": 4, "resources_needed": 1, "value": 3}
    ]
    _, selected = allocate_resources(2, tasks)
    assert selected == sorted(selected)
