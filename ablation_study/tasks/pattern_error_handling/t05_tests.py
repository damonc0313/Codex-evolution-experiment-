import pytest
from solution import safe_resource_use

def test_successful_use():
    state = {"resource": None, "released": False}

    def acquire():
        state["resource"] = "my_resource"
        return "my_resource"

    def use(resource):
        return f"Used {resource}"

    def release(resource):
        state["released"] = True

    success, result = safe_resource_use(acquire, use, release)
    assert success is True
    assert result == "Used my_resource"
    assert state["released"] is True

def test_use_raises_exception():
    state = {"released": False}

    def acquire():
        return "resource"

    def use(resource):
        raise ValueError("Error during use")

    def release(resource):
        state["released"] = True

    success, result = safe_resource_use(acquire, use, release)
    assert success is False
    assert isinstance(result, ValueError)
    assert state["released"] is True  # Must release even on error

def test_file_like_resource():
    state = {"file": None, "closed": False}

    def acquire():
        state["file"] = {"name": "test.txt", "open": True}
        return state["file"]

    def use(file):
        if not file["open"]:
            raise RuntimeError("File not open")
        return file["name"]

    def release(file):
        file["open"] = False
        state["closed"] = True

    success, result = safe_resource_use(acquire, use, release)
    assert success is True
    assert result == "test.txt"
    assert state["closed"] is True

def test_connection_like_resource():
    state = {"connection": None, "disconnected": False}

    def acquire():
        state["connection"] = {"id": 123, "connected": True}
        return state["connection"]

    def use(conn):
        return conn["id"] * 2

    def release(conn):
        conn["connected"] = False
        state["disconnected"] = True

    success, result = safe_resource_use(acquire, use, release)
    assert success is True
    assert result == 246
    assert state["disconnected"] is True

def test_acquire_fails():
    state = {"released": False}

    def acquire():
        raise ConnectionError("Cannot acquire")

    def use(resource):
        return "Used"

    def release(resource):
        state["released"] = True

    success, result = safe_resource_use(acquire, use, release)
    assert success is False
    assert isinstance(result, ConnectionError)
    # Release should not be called if acquire fails
    # This is a design choice - test whichever behavior you implement

def test_multiple_uses():
    call_count = {"acquire": 0, "use": 0, "release": 0}

    def acquire():
        call_count["acquire"] += 1
        return f"resource_{call_count['acquire']}"

    def use(resource):
        call_count["use"] += 1
        return resource.upper()

    def release(resource):
        call_count["release"] += 1

    # First call
    success1, result1 = safe_resource_use(acquire, use, release)
    assert success1 and result1 == "RESOURCE_1"

    # Second call
    success2, result2 = safe_resource_use(acquire, use, release)
    assert success2 and result2 == "RESOURCE_2"

    assert call_count == {"acquire": 2, "use": 2, "release": 2}

def test_release_always_called():
    release_calls = []

    def acquire():
        return "res"

    def use(resource):
        release_calls.append("before_error")
        raise RuntimeError("Fail")

    def release(resource):
        release_calls.append("release")

    safe_resource_use(acquire, use, release)
    assert "release" in release_calls
