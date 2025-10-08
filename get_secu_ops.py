#!/usr/bin/env python
import os
import json
import csv
import re
import argparse
from datetime import datetime
from typing import List, Dict, Any


def extract_ticker_from_description(description: str) -> str:
    """
    Extract ticker symbol from a securities transaction description.

    Args:
        description: The transaction description string

    Returns:
        Ticker symbol if found, empty string otherwise
    """
    # Look for ticker in parentheses
    ticker_match = re.search(r'\(([A-Z0-9]{2,})\)', description)
    if ticker_match:
        return ticker_match.group(1)

    # Look for ISIN
    isin_match = re.search(r'\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b', description)
    if isin_match:
        return isin_match.group(0)

    return ""


def is_security_transaction(description: str) -> bool:
    """
    Determine if a transaction is security-related based on the description.

    Args:
        description: The transaction description string

    Returns:
        True if security-related, False otherwise
    """
    # Convert description to lowercase for case-insensitive matching
    desc_lower = description.lower()

    # Include all security-related transactions
    security_keywords = [
        'securities',
        'stock',
        'fund',
        'dividend',
        'instrument',
        'income tax withheld'  # Add tax withholding for securities
    ]

    # Exclude only currency exchanges
    exclude_keywords = [
        'currency exchange'
    ]

    # Check if description contains any security-related keywords
    if any(keyword in desc_lower for keyword in security_keywords):
        # Exclude if it contains any exclude keywords
        if any(exclude_keyword in desc_lower for exclude_keyword in exclude_keywords):
            return False
        return True

    return False


def process_bank_statement(input_file: str, output_file: str) -> None:
    """
    Process bank statement CSV to extract security transactions.
    If output file exists, append and aggregate transactions with same date, ticker, and description.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output JSON file
    """
    aggregated_transactions = {}

    # Load existing data if output file exists
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as jsonfile:
                existing_data = json.load(jsonfile)
                for transaction in existing_data.get('security_transactions', []):
                    key = (transaction['date'], transaction['ticker'], transaction['description'])
                    # Handle missing operations_count in existing data
                    if 'operations_count' not in transaction:
                        transaction['operations_count'] = 1
                    aggregated_transactions[key] = transaction
        except Exception as e:
            print(f"Warning: Could not read existing output file: {str(e)}")

    try:
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                description = row.get('Selgitus', '')

                if is_security_transaction(description):
                    ticker = extract_ticker_from_description(description)

                    # Only include transactions with extracted tickers
                    if ticker:
                        date = row.get('Kuupäev', '')
                        amount = float(row.get('Summa', 0))
                        key = (date, ticker, description)

                        if key in aggregated_transactions:
                            # Update existing transaction
                            aggregated_transactions[key]['amount'] += amount
                            aggregated_transactions[key]['operations_count'] += 1
                        else:
                            # Create new transaction
                            aggregated_transactions[key] = {
                                'date': date,
                                'ticker': ticker,
                                'amount': amount,
                                'description': description,
                                'type': 'buy' if amount < 0 else 'sell',
                                'operations_count': 1
                            }

        # Convert aggregated transactions back to list
        security_transactions = list(aggregated_transactions.values())

        # Update transaction types based on final amounts and round amounts
        for transaction in security_transactions:
            transaction['amount'] = round(transaction['amount'], 2)
            transaction['type'] = 'buy' if transaction['amount'] < 0 else 'sell'

        # Sort transactions by date
        security_transactions.sort(key=lambda x: x['date'])

        # Write to output JSON file
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'security_transactions': security_transactions,
                'metadata': {
                    'processed_date': datetime.now().isoformat(),
                    'total_transactions': len(security_transactions),
                    'unique_tickers': len(set(t['ticker'] for t in security_transactions)),
                    'total_operations': sum(t['operations_count'] for t in security_transactions)
                }
            }, jsonfile, indent=2, ensure_ascii=False)

        print(f"Successfully processed {len(security_transactions)} unique security transactions")
        print(f"Total operations: {sum(t['operations_count'] for t in security_transactions)}")
        print(f"Output saved to {output_file}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Extract security tickers from bank statement')
    parser.add_argument('--input', '-i', type=str, help='Input CSV file path')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file path')
    parser.add_argument('--data-dir', '-d', type=str, default='data',
                        help='Base data directory (default: data)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set logging level (default: INFO)')
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    # Set up directories following the pattern from get_gaps.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, args.data_dir)

    # Default input and output paths
    input_file = args.input
    output_file = args.output

    # If no input specified, look in data directory
    if not input_file:
        input_file = os.path.join(data_dir, "bank_statements", "statement.csv")

    # If no output specified, create in data directory
    if not output_file:
        output_dir = os.path.join(data_dir, "security_transactions")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "security_transactions.json")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        return

    # Process the bank statement
    process_bank_statement(input_file, output_file)


if __name__ == "__main__":
    main()