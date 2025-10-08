from decimal import Decimal
from uuid import uuid4


class Security:
    """Represents a security that can be traded."""

    def __init__(self, symbol: str, name: str):
        self.id = str(uuid4())
        self.symbol = symbol
        self.name = name
        self.current_price = Decimal('0')

    def update_price(self, price: Decimal) -> None:
        """Update the current market price of the security."""
        self.current_price = price

    def __str__(self) -> str:
        return f"{self.symbol} ({self.name}): ${self.current_price}"


