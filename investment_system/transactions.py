from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4


class Transaction:
    """Represents a buy/sell transaction."""

    TRANSACTION_TYPES = ["BUY", "SELL", "DEPOSIT", "WITHDRAW"]

    def __init__(self, transaction_type: str, customer_id: str,
                 security_id: Optional[str] = None,
                 quantity: Optional[Decimal] = None,
                 price: Optional[Decimal] = None,
                 amount: Optional[Decimal] = None):

        if transaction_type not in self.TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type. Must be one of {self.TRANSACTION_TYPES}")

        self.id = str(uuid4())
        self.transaction_type = transaction_type
        self.customer_id = customer_id
        self.security_id = security_id
        self.quantity = quantity
        self.price = price
        self.amount = amount
        self.timestamp = datetime.now()

        # Validate based on transaction type
        if transaction_type in ["BUY", "SELL"]:
            if not all([security_id, quantity, price]):
                raise ValueError("Security ID, quantity, and price required for BUY/SELL")
            self.amount = quantity * price
        elif transaction_type in ["DEPOSIT", "WITHDRAW"]:
            if not amount:
                raise ValueError("Amount required for DEPOSIT/WITHDRAW")

    def __str__(self) -> str:
        if self.transaction_type in ["BUY", "SELL"]:
            return (f"{self.transaction_type} - Customer ID: {self.customer_id}, "
                    f"Security ID: {self.security_id}, Quantity: {self.quantity}, "
                    f"Price: ${self.price}, Total: ${self.amount}, Time: {self.timestamp}")
        else:
            return (f"{self.transaction_type} - Customer ID: {self.customer_id}, "
                    f"Amount: ${self.amount}, Time: {self.timestamp}")


