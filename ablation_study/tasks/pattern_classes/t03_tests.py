import pytest
from solution import BankAccount

def test_initialization():
    acc = BankAccount("12345")
    assert acc.account_number == "12345"
    assert acc.balance == 0

def test_initialization_with_balance():
    acc = BankAccount("12345", initial_balance=100)
    assert acc.balance == 100

def test_deposit():
    acc = BankAccount("12345")
    result = acc.deposit(50)
    assert result is True
    assert acc.balance == 50

def test_multiple_deposits():
    acc = BankAccount("12345")
    acc.deposit(100)
    acc.deposit(50)
    acc.deposit(25)
    assert acc.balance == 175

def test_withdraw():
    acc = BankAccount("12345", initial_balance=100)
    result = acc.withdraw(30)
    assert result is True
    assert acc.balance == 70

def test_insufficient_funds():
    acc = BankAccount("12345", initial_balance=50)
    result = acc.withdraw(100)
    assert result is False
    assert acc.balance == 50  # Balance unchanged

def test_invalid_deposit():
    acc = BankAccount("12345")
    assert acc.deposit(0) is False
    assert acc.deposit(-10) is False
    assert acc.balance == 0

def test_invalid_withdrawal():
    acc = BankAccount("12345", initial_balance=100)
    assert acc.withdraw(0) is False
    assert acc.withdraw(-10) is False
    assert acc.balance == 100

def test_transaction_history():
    acc = BankAccount("12345")
    acc.deposit(100)
    acc.withdraw(30)
    acc.deposit(50)

    transactions = acc.get_transactions()
    assert len(transactions) == 3

    assert transactions[0] == {"type": "deposit", "amount": 100, "balance": 100}
    assert transactions[1] == {"type": "withdrawal", "amount": 30, "balance": 70}
    assert transactions[2] == {"type": "deposit", "amount": 50, "balance": 120}

def test_failed_transactions_not_recorded():
    acc = BankAccount("12345", initial_balance=50)
    acc.withdraw(100)  # Should fail
    acc.deposit(-10)   # Should fail

    transactions = acc.get_transactions()
    assert len(transactions) == 0  # No successful transactions

def test_string_representation():
    acc = BankAccount("12345", initial_balance=123.45)
    assert str(acc) == "Account 12345: $123.45"

    acc = BankAccount("67890")
    assert str(acc) == "Account 67890: $0.00"

def test_properties_readonly():
    acc = BankAccount("12345", initial_balance=100)

    with pytest.raises(AttributeError):
        acc.balance = 200

    with pytest.raises(AttributeError):
        acc.account_number = "99999"

def test_exact_balance_withdrawal():
    acc = BankAccount("12345", initial_balance=100)
    result = acc.withdraw(100)
    assert result is True
    assert acc.balance == 0
