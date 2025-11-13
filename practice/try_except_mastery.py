"""
Try-Except Mastery - ACE Practice Task (Iteration 4)
=====================================================

Task: ace_practice_try_except_20251107_063421
Objective: Master exception handling from 24.4% → 80%

Exception handling patterns for robust, production-ready code:
- Graceful error recovery
- Resource cleanup (finally, context managers)
- Custom exceptions for domain logic
- Retry logic with exponential backoff
- Logging and monitoring integration

Current: 24.4% → Target: 80% → Gap: 55.6% (priority rank: 4/5)
"""

from typing import Any, Callable, Optional, TypeVar, List, Dict
import time
import logging
from functools import wraps
from contextlib import contextmanager

T = TypeVar('T')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Exercise 1: Handle multiple exception types appropriately
# =========================================================

def safe_divide(a: float, b: float) -> Optional[float]:
    """
    Safe division with specific exception handling.

    Demonstrates: Multiple except clauses, specific before general
    """
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        logger.warning(f"Division by zero: {a} / {b}")
        return None
    except TypeError as e:
        logger.error(f"Type error in division: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def parse_json_safe(json_string: str) -> Optional[Dict]:
    """
    Parse JSON with comprehensive error handling.

    Demonstrates: Specific exceptions for different failure modes
    """
    import json

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}")
        return None
    except TypeError:
        logger.error("Input must be string")
        return None
    except Exception as e:
        logger.error(f"Unexpected JSON parsing error: {e}")
        return None


def robust_file_operation(filepath: str, mode: str = 'r') -> Optional[str]:
    """
    File operations with comprehensive error handling.

    Demonstrates: Multiple exception types for file I/O
    """
    try:
        with open(filepath, mode) as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except PermissionError:
        logger.error(f"Permission denied: {filepath}")
        return None
    except IsADirectoryError:
        logger.error(f"Expected file, got directory: {filepath}")
        return None
    except IOError as e:
        logger.error(f"I/O error: {e}")
        return None


# Exercise 2: Use finally for cleanup
# ===================================

def process_with_cleanup(data: Any) -> bool:
    """
    Ensure cleanup with finally block.

    Demonstrates: finally executes whether exception occurs or not
    """
    resource = None
    try:
        resource = acquire_resource()
        process_resource(resource, data)
        return True
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return False
    finally:
        if resource:
            release_resource(resource)
            logger.info("Resource released")


def acquire_resource():
    """Simulate resource acquisition"""
    return {"handle": "resource_123"}


def process_resource(resource: Dict, data: Any):
    """Simulate resource processing"""
    if not data:
        raise ValueError("Invalid data")


def release_resource(resource: Dict):
    """Simulate resource release"""
    pass


def database_transaction(queries: List[str]) -> bool:
    """
    Database transaction with rollback in finally.

    Demonstrates: Transactional pattern with cleanup
    """
    connection = None
    transaction = None

    try:
        connection = connect_database()
        transaction = connection.begin_transaction()

        for query in queries:
            execute_query(connection, query)

        transaction.commit()
        return True

    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        if transaction:
            transaction.rollback()
        return False

    finally:
        if connection:
            connection.close()


def connect_database():
    """Simulate database connection"""
    return type('Connection', (), {
        'begin_transaction': lambda: type('Transaction', (), {
            'commit': lambda: None,
            'rollback': lambda: None
        })(),
        'close': lambda: None
    })()


def execute_query(conn, query):
    """Simulate query execution"""
    if 'INVALID' in query:
        raise ValueError(f"Invalid query: {query}")


# Exercise 3: Create custom exception classes
# ===========================================

class ValidationError(Exception):
    """Base exception for validation errors"""
    pass


class SchemaValidationError(ValidationError):
    """Schema validation failed"""
    def __init__(self, field: str, expected: str, actual: str):
        self.field = field
        self.expected = expected
        self.actual = actual
        super().__init__(f"Field '{field}': expected {expected}, got {actual}")


class BusinessRuleViolation(Exception):
    """Business rule violated"""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"Rule '{rule}': {message}")


class RetryableError(Exception):
    """Error that should trigger retry"""
    pass


class NonRetryableError(Exception):
    """Error that should not be retried"""
    pass


def validate_user_data(data: Dict[str, Any]) -> None:
    """
    Validate user data with custom exceptions.

    Demonstrates: Domain-specific exceptions for clear error handling
    """
    if 'email' not in data:
        raise SchemaValidationError('email', 'string', 'missing')

    if not isinstance(data['email'], str):
        raise SchemaValidationError('email', 'string', type(data['email']).__name__)

    if 'age' in data and data['age'] < 0:
        raise BusinessRuleViolation('age_positive', 'Age must be positive')

    if data.get('role') == 'admin' and not data.get('verified'):
        raise BusinessRuleViolation('admin_verified', 'Admins must be verified')


def process_with_custom_exceptions(user_data: Dict) -> bool:
    """
    Process data handling custom exceptions specifically.

    Demonstrates: Exception hierarchy for specific handling
    """
    try:
        validate_user_data(user_data)
        return True

    except SchemaValidationError as e:
        logger.error(f"Schema error: {e}")
        return False

    except BusinessRuleViolation as e:
        logger.warning(f"Business rule violated: {e}")
        return False

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return False


# Exercise 4: Implement retry logic with exception handling
# =========================================================

def retry_with_exponential_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Optional[T]:
    """
    Retry function with exponential backoff.

    Demonstrates: Retry pattern for transient failures
    """
    delay = initial_delay

    for attempt in range(max_attempts):
        try:
            return func()

        except RetryableError as e:
            if attempt == max_attempts - 1:
                logger.error(f"Max retries ({max_attempts}) exceeded: {e}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed (retrying in {delay}s): {e}")
            time.sleep(delay)
            delay *= backoff_factor

        except NonRetryableError as e:
            logger.error(f"Non-retryable error: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error (not retrying): {e}")
            raise

    return None


def api_call_with_retry(endpoint: str, max_retries: int = 3) -> Optional[Dict]:
    """
    API call with automatic retry on failure.

    Demonstrates: Real-world retry pattern
    """
    def make_request():
        # Simulate API call
        import random
        if random.random() < 0.3:  # 30% failure rate
            raise RetryableError("Network timeout")
        return {"status": "success", "data": []}

    try:
        return retry_with_exponential_backoff(make_request, max_attempts=max_retries)
    except RetryableError:
        logger.error(f"API call to {endpoint} failed after {max_retries} retries")
        return None


# Exercise 5: Use context managers to avoid try-finally
# =====================================================

@contextmanager
def managed_resource(resource_id: str):
    """
    Context manager for automatic resource cleanup.

    Demonstrates: Context manager pattern (replaces try-finally)
    """
    resource = None
    try:
        logger.info(f"Acquiring resource: {resource_id}")
        resource = {"id": resource_id, "handle": f"handle_{resource_id}"}
        yield resource
    finally:
        if resource:
            logger.info(f"Releasing resource: {resource_id}")


def use_context_manager(resource_id: str) -> bool:
    """
    Use context manager for clean resource handling.

    BEFORE (with try-finally):
        resource = acquire()
        try:
            process(resource)
        finally:
            release(resource)

    AFTER (with context manager):
        with managed_resource(resource_id) as resource:
            process(resource)

    Benefits: Automatic cleanup, less boilerplate, exception-safe
    """
    try:
        with managed_resource(resource_id) as resource:
            if not resource:
                raise ValueError("Resource acquisition failed")
            # Process resource
            return True
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False


class FileProcessor:
    """
    File processor using context manager protocol.

    Demonstrates: __enter__/__exit__ pattern
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = None

    def __enter__(self):
        try:
            self.file = open(self.filepath, 'r')
            return self.file
        except Exception as e:
            logger.error(f"Failed to open {self.filepath}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        if exc_type:
            logger.error(f"Exception during processing: {exc_val}")
        return False  # Don't suppress exceptions


# Decorator for automatic exception handling
def handle_exceptions(default_return=None, log_errors=True):
    """
    Decorator for automatic exception handling.

    Demonstrates: Decorator pattern for consistent error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


@handle_exceptions(default_return=0, log_errors=True)
def safe_calculation(a: int, b: int) -> int:
    """
    Calculation with automatic error handling via decorator.

    Demonstrates: Decorator-based exception handling
    """
    return a / b  # Can raise ZeroDivisionError


"""
EXCEPTION HANDLING - BEST PRACTICES
===================================

EXCEPTION HIERARCHY:
1. Catch specific exceptions before general ones
2. Use custom exceptions for domain logic
3. Inherit from appropriate base classes

RESOURCE CLEANUP:
1. Prefer context managers over try-finally
2. Always clean up in finally or __exit__
3. Handle cleanup failures gracefully

RETRY LOGIC:
1. Only retry transient/retryable errors
2. Use exponential backoff
3. Set maximum retry limits
4. Log retry attempts

LOGGING:
1. Log at appropriate levels (error/warning/info)
2. Include context in log messages
3. Log exceptions with traceback
4. Avoid logging sensitive data

ANTI-PATTERNS TO AVOID:
- Bare except: (catches KeyboardInterrupt, SystemExit)
- Swallowing exceptions silently
- Generic exception messages
- Not cleaning up resources
- Infinite retry loops
- Catching but not handling

PERFORMANCE CONSIDERATIONS:
- Exception handling is expensive (~100x slower than if-check)
- Use for exceptional cases, not control flow
- Validate input before expensive operations
- Consider EAFP vs LBYL based on use case
"""


# Test suite
def test_exception_handling_mastery():
    """Test all exception handling patterns."""

    # Test Exercise 1
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) is None

    # Test Exercise 2
    result = process_with_cleanup({"valid": "data"})
    assert result is True

    # Test Exercise 3
    try:
        validate_user_data({})
        assert False, "Should have raised SchemaValidationError"
    except SchemaValidationError:
        pass

    try:
        validate_user_data({"email": "test@test.com", "age": -5})
        assert False, "Should have raised BusinessRuleViolation"
    except BusinessRuleViolation:
        pass

    # Test Exercise 4
    # (Retry tests would require more complex mocking)

    # Test Exercise 5
    result = use_context_manager("test_resource")
    assert result is True

    result = safe_calculation(10, 2)
    assert result == 5

    result = safe_calculation(10, 0)
    assert result == 0  # Default return on error

    print("✅ All exception handling tests passed!")
    return True


if __name__ == "__main__":
    print("Try-Except Mastery - ACE Practice Task (Iteration 4)")
    print("=" * 60)
    print("\nExecuting test suite...\n")
    test_exception_handling_mastery()
    print("\n✅ Practice task complete!")
    print("Exception handling proficiency: 24.4% → [measuring...]")
