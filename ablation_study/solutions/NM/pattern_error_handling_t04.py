from typing import Callable, Any

def safe_call(
    func: Callable,
    *args,
    on_type_error: Any = "TYPE_ERROR",
    on_value_error: Any = "VALUE_ERROR",
    on_other: Any = "OTHER_ERROR"
) -> Any:
    """
    Call function with args, handling different exceptions.

    """
    try:
        return func(*args)
    except TypeError:
        return on_type_error
    except ValueError:
        return on_value_error
    except Exception:
        return on_other
