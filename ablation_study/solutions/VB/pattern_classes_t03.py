class BankAccount:
    """
    Bank account with transaction history.

    """

    def __init__(self, account_number: str, initial_balance: float = 0):
        """Initialize account with number and optional balance."""
        self._account_number = account_number
        self._balance = initial_balance
        self._transactions = []

    def deposit(self, amount: float) -> bool:
        """Deposit amount. Return True if successful, False if amount <= 0."""
        if amount <= 0:
            return False

        self._balance += amount
        self._transactions.append({
            "type": "deposit",
            "amount": amount,
            "balance": self._balance
        })
        return True

    def withdraw(self, amount: float) -> bool:
        """Withdraw amount. Return True if successful, False if insufficient funds or amount <= 0."""
        if amount <= 0 or amount > self._balance:
            return False

        self._balance -= amount
        self._transactions.append({
            "type": "withdrawal",
            "amount": amount,
            "balance": self._balance
        })
        return True

    @property
    def balance(self) -> float:
        """Get current balance."""
        return self._balance

    @property
    def account_number(self) -> str:
        """Get account number."""
        return self._account_number

    def get_transactions(self) -> list[dict]:
        """Get transaction history as list of dicts with 'type', 'amount', 'balance'."""
        return self._transactions.copy()

    def __str__(self) -> str:
        """Return 'Account {number}: ${balance:.2f}'"""
        return f"Account {self._account_number}: ${self._balance:.2f}"
