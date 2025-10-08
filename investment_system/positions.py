from decimal import Decimal
from typing import Tuple
from uuid import uuid4


class Position:
    """Represents a customer's ownership position in a security."""

    def __init__(self, customer_id: str, security_id: str):
        self.id = str(uuid4())
        self.customer_id = customer_id
        self.security_id = security_id
        self.quantity = Decimal('0')
        self.cost_basis = Decimal('0')  # Total cost of current position

    def add_shares(self, quantity: Decimal, price_per_share: Decimal) -> None:
        """Add shares to the position with their cost."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        total_cost = quantity * price_per_share

        # Update the weighted average cost basis
        new_total_quantity = self.quantity + quantity
        new_total_cost = self.cost_basis + total_cost

        self.quantity = new_total_quantity
        self.cost_basis = new_total_cost

    def remove_shares(self, quantity: Decimal) -> Tuple[Decimal, Decimal]:
        """Remove shares from the position, return cost basis per share and total cost of removed shares."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.quantity:
            raise ValueError("Not enough shares to remove")

        # Calculate the average cost per share
        cost_per_share = self.cost_basis / self.quantity if self.quantity > 0 else Decimal('0')
        total_cost_removed = cost_per_share * quantity

        # Update position
        self.quantity -= quantity
        self.cost_basis -= total_cost_removed

        return cost_per_share, total_cost_removed

    def market_value(self, current_price: Decimal) -> Decimal:
        """Calculate current market value of the position."""
        return self.quantity * current_price

    def unrealized_pl(self, current_price: Decimal) -> Decimal:
        """Calculate unrealized profit/loss."""
        avg_cost = self.average_cost()
        return self.quantity * (current_price - avg_cost)

    def average_cost(self) -> Decimal:
        """Calculate average cost per share."""
        if self.quantity > 0:
            return self.cost_basis / self.quantity
        return Decimal('0')

    def __str__(self) -> str:
        return f"Position - Quantity: {self.quantity}, Cost Basis: ${self.cost_basis}"


