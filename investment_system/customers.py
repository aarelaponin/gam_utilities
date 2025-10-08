from decimal import Decimal
from uuid import uuid4


class Customer:
    """Represents a customer with investments."""

    def __init__(self, name: str, contact_info: str):
        self.id = str(uuid4())
        self.name = name
        self.contact_info = contact_info
        self.cash_balance = Decimal('0')

    def deposit(self, amount: Decimal) -> None:
        """Customer deposits cash into their account."""
        self.cash_balance += amount

    def withdraw(self, amount: Decimal) -> bool:
        """Customer withdraws cash from their account if sufficient balance."""
        if amount <= self.cash_balance:
            self.cash_balance -= amount
            return True
        return False

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id}) - Cash: ${self.cash_balance}"


