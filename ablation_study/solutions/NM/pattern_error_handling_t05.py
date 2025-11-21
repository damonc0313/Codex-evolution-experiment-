from typing import Any, Callable

def safe_resource_use(
    acquire: Callable[[], Any],
    use: Callable[[Any], Any],
    release: Callable[[Any], None]
) -> tuple[bool, Any]:
    """
    Safely acquire, use, and release a resource.

    Critical pattern: Finally block ensures release even on exception.
    """
    resource = None
    try:
        resource = acquire()
        result = use(resource)
        return (True, result)
    except Exception as e:
        return (False, e)
    finally:
        # Release only if resource was successfully acquired
        if resource is not None:
            release(resource)
