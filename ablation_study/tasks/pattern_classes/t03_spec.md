# Task: Bank Account

Implement a BankAccount class with deposits, withdrawals, and transaction history.

**Class specification:**
```python
class BankAccount:
    """Bank account with transaction history."""

    def __init__(self, account_number: str, initial_balance: float = 0):
        """Initialize account with number and optional balance."""
        pass

    def deposit(self, amount: float) -> bool:
        """Deposit amount. Return True if successful, False if amount <= 0."""
        pass

    def withdraw(self, amount: float) -> bool:
        """Withdraw amount. Return True if successful, False if insufficient funds or amount <= 0."""
        pass

    @property
    def balance(self) -> float:
        """Get current balance."""
        pass

    @property
    def account_number(self) -> str:
        """Get account number."""
        pass

    def get_transactions(self) -> list[dict]:
        """Get transaction history as list of dicts with 'type', 'amount', 'balance'."""
        pass

    def __str__(self) -> str:
        """Return 'Account {number}: ${balance:.2f}'"""
        pass
```

**Requirements:**
- Prevent negative balances
- Prevent negative/zero deposits/withdrawals
- Record each successful transaction with type, amount, and resulting balance
- Properties for balance and account_number (read-only)
