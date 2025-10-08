#!/usr/bin/env python
import os
import json
import argparse
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from investment_system.assets import Security
from investment_system.customers import Customer
from investment_system.positions import Position
from investment_system.transactions import Transaction


class InvestmentSystem:
    """Main system for managing customers, securities, positions and transactions."""

    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.securities: Dict[str, Security] = {}
        self.positions: Dict[str, Position] = {}  # Key: customer_id + "_" + security_id
        self.transactions: List[Transaction] = []

    def add_customer(self, name: str, contact_info: str) -> Customer:
        """Add a new customer to the system."""
        customer = Customer(name, contact_info)
        self.customers[customer.id] = customer
        return customer

    def add_security(self, symbol: str, name: str) -> Security:
        """Add a new security to the system."""
        security = Security(symbol, name)
        self.securities[security.id] = security
        return security

    def update_security_price(self, security_id: str, price: Decimal) -> None:
        """Update current price for a security."""
        if security_id in self.securities:
            self.securities[security_id].update_price(price)
        else:
            raise ValueError(f"Security with ID {security_id} not found")

    def customer_deposit(self, customer_id: str, amount: Decimal) -> Transaction:
        """Process a cash deposit from a customer."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        customer = self.customers[customer_id]
        customer.deposit(amount)

        # Record transaction
        transaction = Transaction("DEPOSIT", customer_id, amount=amount)
        self.transactions.append(transaction)

        return transaction

    def customer_withdraw(self, customer_id: str, amount: Decimal) -> Optional[Transaction]:
        """Process a cash withdrawal for a customer if sufficient balance."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        customer = self.customers[customer_id]
        if customer.withdraw(amount):
            # Record transaction
            transaction = Transaction("WITHDRAW", customer_id, amount=amount)
            self.transactions.append(transaction)
            return transaction
        else:
            raise ValueError(f"Insufficient funds for withdrawal of ${amount}")

    def _get_position_key(self, customer_id: str, security_id: str) -> str:
        """Generate a unique key for positions dictionary."""
        return f"{customer_id}_{security_id}"

    def _get_or_create_position(self, customer_id: str, security_id: str) -> Position:
        """Get existing position or create a new one."""
        key = self._get_position_key(customer_id, security_id)

        if key not in self.positions:
            position = Position(customer_id, security_id)
            self.positions[key] = position

        return self.positions[key]

    def buy_security(self, customer_id: str, security_id: str,
                     quantity: Decimal, price: Decimal) -> Transaction:
        """Process a security purchase for a customer."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        if security_id not in self.securities:
            raise ValueError(f"Security with ID {security_id} not found")

        total_cost = quantity * price
        customer = self.customers[customer_id]

        # Check if customer has enough cash
        if customer.cash_balance < total_cost:
            raise ValueError(f"Insufficient funds. Required: ${total_cost}, Available: ${customer.cash_balance}")

        # Update customer's cash balance
        customer.withdraw(total_cost)

        # Update position
        position = self._get_or_create_position(customer_id, security_id)
        position.add_shares(quantity, price)

        # Record transaction
        transaction = Transaction("BUY", customer_id, security_id, quantity, price)
        self.transactions.append(transaction)

        return transaction

    def sell_security(self, customer_id: str, security_id: str,
                      quantity: Decimal, price: Decimal) -> Tuple[Transaction, Decimal]:
        """Process a security sale for a customer. Returns transaction and realized P/L."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        if security_id not in self.securities:
            raise ValueError(f"Security with ID {security_id} not found")

        key = self._get_position_key(customer_id, security_id)
        if key not in self.positions:
            raise ValueError(f"Customer does not own this security")

        position = self.positions[key]
        if position.quantity < quantity:
            raise ValueError(f"Insufficient shares. Requested: {quantity}, Available: {position.quantity}")

        # Calculate sale proceeds and cost basis
        total_proceeds = quantity * price
        cost_per_share, total_cost = position.remove_shares(quantity)

        # Update customer's cash balance
        customer = self.customers[customer_id]
        customer.deposit(total_proceeds)

        # Calculate realized profit/loss
        realized_pl = total_proceeds - total_cost

        # Record transaction
        transaction = Transaction("SELL", customer_id, security_id, quantity, price)
        self.transactions.append(transaction)

        # Remove position if quantity is zero
        if position.quantity == 0:
            del self.positions[key]

        return transaction, realized_pl

    def get_customer_portfolio(self, customer_id: str) -> Dict:
        """Get a summary of a customer's portfolio including cash and positions."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        customer = self.customers[customer_id]
        positions_data = []
        total_market_value = Decimal('0')
        total_cost_basis = Decimal('0')

        # Find all positions for this customer
        for key, position in self.positions.items():
            if position.customer_id == customer_id:
                security = self.securities[position.security_id]
                current_price = security.current_price
                market_value = position.market_value(current_price)
                unrealized_pl = position.unrealized_pl(current_price)

                positions_data.append({
                    "security_symbol": security.symbol,
                    "security_name": security.name,
                    "quantity": float(position.quantity),
                    "average_cost": float(position.average_cost()),
                    "current_price": float(current_price),
                    "cost_basis": float(position.cost_basis),
                    "market_value": float(market_value),
                    "unrealized_pl": float(unrealized_pl),
                    "unrealized_pl_percent": float(
                        unrealized_pl / position.cost_basis * 100) if position.cost_basis > 0 else 0
                })

                total_market_value += market_value
                total_cost_basis += position.cost_basis

        # Calculate total portfolio value and performance
        cash_balance = customer.cash_balance
        total_portfolio_value = cash_balance + total_market_value
        total_unrealized_pl = total_market_value - total_cost_basis

        return {
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "contact_info": customer.contact_info
            },
            "cash_balance": float(cash_balance),
            "positions": positions_data,
            "portfolio_summary": {
                "total_cost_basis": float(total_cost_basis),
                "total_market_value": float(total_market_value),
                "total_unrealized_pl": float(total_unrealized_pl),
                "total_unrealized_pl_percent": float(
                    total_unrealized_pl / total_cost_basis * 100) if total_cost_basis > 0 else 0,
                "total_portfolio_value": float(total_portfolio_value)
            }
        }

    def get_customer_transactions(self, customer_id: str) -> List[Dict]:
        """Get all transactions for a specific customer."""
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        customer_transactions = []
        for transaction in self.transactions:
            if transaction.customer_id == customer_id:
                tx_data = {
                    "id": transaction.id,
                    "type": transaction.transaction_type,
                    "timestamp": transaction.timestamp.isoformat(),
                    "amount": float(transaction.amount) if transaction.amount else None
                }

                if transaction.transaction_type in ["BUY", "SELL"]:
                    security = self.securities[transaction.security_id]
                    tx_data.update({
                        "security_symbol": security.symbol,
                        "security_name": security.name,
                        "quantity": float(transaction.quantity),
                        "price": float(transaction.price)
                    })

                customer_transactions.append(tx_data)

        return customer_transactions

    def calculate_allocation_change(self, customer_id: str, target_allocation: Dict[str, float]) -> Dict:
        """
        Calculate trades needed to reach target allocation.
        Target allocation format: {security_id: percentage as decimal (e.g., 0.25 for 25%)}
        """
        if customer_id not in self.customers:
            raise ValueError(f"Customer with ID {customer_id} not found")

        portfolio = self.get_customer_portfolio(customer_id)
        total_portfolio_value = Decimal(str(portfolio["portfolio_summary"]["total_portfolio_value"]))

        # Verify allocation adds up to 1.0 (100%)
        total_allocation = sum(target_allocation.values())
        if not (0.99 <= total_allocation <= 1.01):  # Allow small rounding errors
            raise ValueError(f"Target allocation must sum to 1.0 (100%). Current sum: {total_allocation}")

        # Calculate target value for each security
        trades = []
        for security_id, target_percent in target_allocation.items():
            if security_id not in self.securities:
                raise ValueError(f"Security with ID {security_id} not found")

            security = self.securities[security_id]
            target_value = total_portfolio_value * Decimal(str(target_percent))

            # Find current position if exists
            key = self._get_position_key(customer_id, security_id)
            current_quantity = Decimal('0')
            current_value = Decimal('0')

            if key in self.positions:
                position = self.positions[key]
                current_quantity = position.quantity
                current_value = position.market_value(security.current_price)

            # Calculate difference
            value_difference = target_value - current_value

            if abs(value_difference) < Decimal('0.01'):  # Ignore very small differences
                continue

            # Calculate quantity to buy/sell
            quantity_change = value_difference / security.current_price
            rounded_quantity = quantity_change.quantize(Decimal('0.0001'))  # Round to 4 decimal places

            if rounded_quantity == 0:
                continue

            action = "BUY" if rounded_quantity > 0 else "SELL"
            trades.append({
                "security_id": security_id,
                "security_symbol": security.symbol,
                "action": action,
                "quantity": abs(float(rounded_quantity)),
                "current_price": float(security.current_price),
                "estimated_value": float(abs(value_difference))
            })

        # Calculate how much cash will be needed or generated
        cash_needed = sum(trade["estimated_value"] for trade in trades if trade["action"] == "BUY")
        cash_generated = sum(trade["estimated_value"] for trade in trades if trade["action"] == "SELL")
        net_cash_impact = cash_generated - cash_needed

        return {
            "trades": trades,
            "cash_summary": {
                "current_cash": float(portfolio["cash_balance"]),
                "cash_needed": float(cash_needed),
                "cash_generated": float(cash_generated),
                "net_cash_impact": float(net_cash_impact),
                "final_cash_position": float(portfolio["cash_balance"] + net_cash_impact)
            }
        }

    def rebalance_portfolio(self, customer_id: str, target_allocation: Dict[str, float]) -> List[Transaction]:
        """
        Re-balance a customer's portfolio to match target allocation.
        Executes the necessary buy and sell trades.
        Returns list of executed transactions.
        """
        allocation_changes = self.calculate_allocation_change(customer_id, target_allocation)
        executed_transactions = []

        # First do all sells to generate cash
        for trade in allocation_changes["trades"]:
            if trade["action"] == "SELL":
                security_id = trade["security_id"]
                quantity = Decimal(str(trade["quantity"]))
                price = Decimal(str(trade["current_price"]))

                transaction, _ = self.sell_security(customer_id, security_id, quantity, price)
                executed_transactions.append(transaction)

        # Then do all buys with available cash
        for trade in allocation_changes["trades"]:
            if trade["action"] == "BUY":
                security_id = trade["security_id"]
                quantity = Decimal(str(trade["quantity"]))
                price = Decimal(str(trade["current_price"]))

                try:
                    transaction = self.buy_security(customer_id, security_id, quantity, price)
                    executed_transactions.append(transaction)
                except ValueError as e:
                    # Handle insufficient funds
                    print(f"Could not complete buy: {e}")

        return executed_transactions

    def export_data(self, filepath: str) -> None:
        """Export all system data to a JSON file."""
        data = {
            "customers": {id: {
                "id": customer.id,
                "name": customer.name,
                "contact_info": customer.contact_info,
                "cash_balance": float(customer.cash_balance)
            } for id, customer in self.customers.items()},

            "securities": {id: {
                "id": security.id,
                "symbol": security.symbol,
                "name": security.name,
                "current_price": float(security.current_price)
            } for id, security in self.securities.items()},

            "positions": {id: {
                "id": position.id,
                "customer_id": position.customer_id,
                "security_id": position.security_id,
                "quantity": float(position.quantity),
                "cost_basis": float(position.cost_basis)
            } for id, position in self.positions.items()},

            "transactions": [{
                "id": tx.id,
                "type": tx.transaction_type,
                "customer_id": tx.customer_id,
                "security_id": tx.security_id,
                "quantity": float(tx.quantity) if tx.quantity else None,
                "price": float(tx.price) if tx.price else None,
                "amount": float(tx.amount) if tx.amount else None,
                "timestamp": tx.timestamp.isoformat()
            } for tx in self.transactions]
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Data exported to {filepath}")

    def import_data(self, filepath: str) -> None:
        """Import system data from a JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Clear current data
        self.customers = {}
        self.securities = {}
        self.positions = {}
        self.transactions = []

        # Import customers
        for id, customer_data in data["customers"].items():
            customer = Customer(customer_data["name"], customer_data["contact_info"])
            customer.id = customer_data["id"]
            customer.cash_balance = Decimal(str(customer_data["cash_balance"]))
            self.customers[customer.id] = customer

        # Import securities
        for id, security_data in data["securities"].items():
            security = Security(security_data["symbol"], security_data["name"])
            security.id = security_data["id"]
            security.current_price = Decimal(str(security_data["current_price"]))
            self.securities[security.id] = security

        # Import positions
        for id, position_data in data["positions"].items():
            position = Position(position_data["customer_id"], position_data["security_id"])
            position.id = position_data["id"]
            position.quantity = Decimal(str(position_data["quantity"]))
            position.cost_basis = Decimal(str(position_data["cost_basis"]))
            key = self._get_position_key(position.customer_id, position.security_id)
            self.positions[key] = position

        # Import transactions
        for tx_data in data["transactions"]:
            tx = Transaction(
                tx_data["type"],
                tx_data["customer_id"],
                tx_data.get("security_id"),
                Decimal(str(tx_data["quantity"])) if tx_data.get("quantity") else None,
                Decimal(str(tx_data["price"])) if tx_data.get("price") else None,
                Decimal(str(tx_data["amount"])) if tx_data.get("amount") else None
            )
            tx.id = tx_data["id"]
            tx.timestamp = datetime.fromisoformat(tx_data["timestamp"])
            self.transactions.append(tx)

        print(f"Imported {len(self.customers)} customers, {len(self.securities)} securities, "
              f"{len(self.positions)} positions, and {len(self.transactions)} transactions from {filepath}")

    def get_system_summary(self) -> Dict:
        """Get a summary of the entire investment system."""
        total_customers = len(self.customers)
        total_securities = len(self.securities)
        total_positions = len(self.positions)
        total_transactions = len(self.transactions)

        total_aum = Decimal('0')  # Assets under management
        total_cash = Decimal('0')

        for customer in self.customers.values():
            total_cash += customer.cash_balance

        for position in self.positions.values():
            security = self.securities[position.security_id]
            total_aum += position.market_value(security.current_price)

        # Add cash to AUM
        total_aum += total_cash

        return {
            "customers": total_customers,
            "securities": total_securities,
            "positions": total_positions,
            "transactions": total_transactions,
            "total_aum": float(total_aum),
            "total_cash": float(total_cash),
            "total_invested": float(total_aum - total_cash),
            "cash_percentage": float(total_cash / total_aum * 100) if total_aum > 0 else 0
        }


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Investment banking system')

    # File paths
    parser.add_argument('--data-dir', '-d', type=str, default='data',
                        help='Base data directory (default: data)')
    parser.add_argument('--test-data', '-t', type=str,
                        help='Test data JSON file path (relative to data directory)')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file path for exported data (relative to data directory)')

    # Actions
    parser.add_argument('--import-data', '-i', action='store_true',
                        help='Import test data from the specified file')
    parser.add_argument('--export-data', '-e', action='store_true',
                        help='Export system data to a file')
    parser.add_argument('--summary', '-s', action='store_true',
                        help='Print summary of the investment system')
    parser.add_argument('--customer', type=str,
                        help='Display portfolio for a specific customer ID')

    return parser.parse_args()


def main() -> None:
    """Main function to run the investment system."""
    args = parse_arguments()

    # Set up directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, args.data_dir)

    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Initialize the investment system
    system = InvestmentSystem()

    # Import test data if specified
    if args.import_data:
        if args.test_data:
            test_data_path = os.path.join(data_dir, args.test_data)
        else:
            # Default test data path
            test_data_dir = os.path.join(data_dir, "test_data")
            os.makedirs(test_data_dir, exist_ok=True)
            test_data_path = os.path.join(test_data_dir, "testdata.json")

        if os.path.exists(test_data_path):
            system.import_data(test_data_path)
        else:
            print(f"Test data file not found: {test_data_path}")
            if not args.test_data:
                print("Please create a test data file or specify one with --test-data")
            return

    # Print system summary if requested
    if args.summary:
        summary = system.get_system_summary()
        print("\nInvestment System Summary:")
        print(f"Customers: {summary['customers']}")
        print(f"Securities: {summary['securities']}")
        print(f"Positions: {summary['positions']}")
        print(f"Transactions: {summary['transactions']}")
        print(f"Total AUM: ${summary['total_aum']:,.2f}")
        print(f"Total Cash: ${summary['total_cash']:,.2f}")
        print(f"Total Invested: ${summary['total_invested']:,.2f}")
        print(f"Cash %: {summary['cash_percentage']:.2f}%")

    # Display customer portfolio if requested
    if args.customer:
        try:
            portfolio = system.get_customer_portfolio(args.customer)
            customer = portfolio['customer']

            print(f"\nPortfolio for {customer['name']} (ID: {customer['id']}):")
            print(f"Contact: {customer['contact_info']}")
            print(f"Cash balance: ${portfolio['cash_balance']:,.2f}")

            if portfolio['positions']:
                print("\nPositions:")
                for position in portfolio['positions']:
                    print(f"  {position['security_symbol']} ({position['security_name']}): "
                          f"{position['quantity']:,.4f} shares, "
                          f"Cost: ${position['average_cost']:,.2f}, "
                          f"Current: ${position['current_price']:,.2f}, "
                          f"Market Value: ${position['market_value']:,.2f}, "
                          f"P/L: ${position['unrealized_pl']:,.2f} ({position['unrealized_pl_percent']:.2f}%)")

            summary = portfolio['portfolio_summary']
            print("\nPortfolio Summary:")
            print(f"Total Cost: ${summary['total_cost_basis']:,.2f}")
            print(f"Total Market Value: ${summary['total_market_value']:,.2f}")
            print(f"Unrealized P/L: ${summary['total_unrealized_pl']:,.2f} "
                  f"({summary['total_unrealized_pl_percent']:.2f}%)")
            print(f"Total Portfolio Value: ${summary['total_portfolio_value']:,.2f}")

        except ValueError as e:
            print(f"Error: {str(e)}")

    # Export data if requested
    if args.export_data:
        if args.output:
            output_path = os.path.join(data_dir, args.output)
        else:
            # Default output path
            output_dir = os.path.join(data_dir, "test_transactions")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"investment_data_{timestamp}.json")

        system.export_data(output_path)


if __name__ == "__main__":
    main()