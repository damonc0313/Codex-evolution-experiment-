import pytest
from solution import retry_operation
import time

def test_success_first_try():
    def operation():
        return "success"

    success, result = retry_operation(operation)
    assert success is True
    assert result == "success"

def test_success_after_retries():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("Not yet")
        return "success"

    success, result = retry_operation(operation, max_attempts=3)
    assert success is True
    assert result == "success"
    assert attempts["count"] == 3

def test_all_attempts_fail():
    def operation():
        raise RuntimeError("Always fails")

    success, result = retry_operation(operation, max_attempts=2)
    assert success is False
    assert isinstance(result, RuntimeError)

def test_exponential_backoff():
    attempts = []

    def operation():
        attempts.append(time.time())
        raise ValueError("Fail")

    retry_operation(operation, max_attempts=3, base_delay=0.1)

    # Check delays are approximately exponential
    assert len(attempts) == 3
    if len(attempts) >= 2:
        delay1 = attempts[1] - attempts[0]
        assert 0.08 < delay1 < 0.15  # ~0.1 seconds

    if len(attempts) >= 3:
        delay2 = attempts[2] - attempts[1]
        assert 0.15 < delay2 < 0.25  # ~0.2 seconds

def test_single_attempt():
    def operation():
        raise ValueError("Fail")

    success, result = retry_operation(operation, max_attempts=1)
    assert success is False
    assert isinstance(result, ValueError)

def test_different_exception_types():
    def operation():
        raise KeyError("Missing key")

    success, result = retry_operation(operation)
    assert success is False
    assert isinstance(result, KeyError)

def test_return_value_preserved():
    def operation():
        return {"data": [1, 2, 3], "status": "ok"}

    success, result = retry_operation(operation)
    assert success is True
    assert result == {"data": [1, 2, 3], "status": "ok"}
