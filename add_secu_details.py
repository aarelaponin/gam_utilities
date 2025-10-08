#!/usr/bin/env python
import os
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Any
from io import StringIO


def parse_date(date_str: str) -> str:
    """
    Convert date from DD.MM.YYYY to YYYY-MM-DD format.

    Args:
        date_str: Date string in DD.MM.YYYY format

    Returns:
        Date string in YYYY-MM-DD format
    """
    if not date_str:
        return ""
    try:
        # Remove any whitespace and BOM characters
        date_str = date_str.strip().replace('\ufeff', '')
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        print(f"Length of date_str: {len(date_str)}")
        print(f"ASCII values: {[ord(c) for c in date_str]}")
        return ""


def parse_float(value: str) -> float:
    """
    Parse float from string with comma as decimal separator.

    Args:
        value: String representation of float

    Returns:
        Float value
    """
    if isinstance(value, (int, float)):
        return float(value)
    if value is None or value == '':
        return 0.0
    # Handle string values
    if isinstance(value, str):
        # Replace comma with dot for decimal point
        value = value.replace(',', '.')
        # Remove any spaces
        value = value.strip()
    return float(value)


def match_transactions(json_file: str, csv_file: str, output_file: str) -> None:
    """
    Match transactions from JSON file with CSV file and add count/price fields.

    Args:
        json_file: Path to input JSON file
        csv_file: Path to input CSV file
        output_file: Path to output JSON file
    """
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Load CSV data
        csv_transactions = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Read all content and normalize line endings
            content = f.read().replace('\r\n', '\n').replace('\r', '\n')

        # Parse CSV from string content
        csv_io = StringIO(content)
        reader = csv.reader(csv_io, delimiter=';')

        # Skip header row
        headers = next(reader)
        print("CSV Headers:", headers)

        for row in reader:
            # Use field positions instead of names
            # VÄÄRTUSPÄEV is at index 0
            # SÜMBOL is at index 3
            # KOGUS is at index 5
            # HIND is at index 6
            # NETOSUMMA is at index 8

            if len(row) > 8:  # Make sure row has enough fields
                amount = parse_float(row[8])  # NETOSUMMA
                if amount != 0:
                    date_str = row[0]  # VÄÄRTUSPÄEV
                    ticker = row[3]  # SÜMBOL
                    count = parse_float(row[5])  # KOGUS
                    price = parse_float(row[6])  # HIND

                    date = parse_date(date_str)

                    if not date:  # Debug if date parsing fails
                        print(f"Failed to parse date: '{date_str}' for ticker {ticker}")

                    csv_transactions.append({
                        'date': date,
                        'ticker': ticker,
                        'amount': amount,
                        'count': count,
                        'price': price
                    })

        # Debug: Print some sample CSV transactions
        print(f"Loaded {len(csv_transactions)} transactions from CSV")
        if csv_transactions:
            print("\nFirst 5 CSV transactions:")
            for i, tx in enumerate(csv_transactions[:5]):
                print(f"{i + 1}. Date: {tx['date']}, Ticker: {tx['ticker']}, Amount: {tx['amount']}")

        # Match transactions
        matched_count = 0
        unmatched_count = 0
        matched_indices = set()  # Keep track of matched CSV indices to avoid duplicate matches

        for json_transaction in json_data['security_transactions']:
            # Skip commission fees and tax withholdings
            if ('commission fee' in json_transaction['description'].lower() or
                    'income tax withheld' in json_transaction['description'].lower()):
                continue

            # Skip dividend transactions as they won't have matches in the security statement
            if 'dividends' in json_transaction['description'].lower():
                continue

            matched = False
            for idx, csv_transaction in enumerate(csv_transactions):
                # Skip if already matched
                if idx in matched_indices:
                    continue

                # Check if date, ticker, and amount match
                date_match = json_transaction['date'] == csv_transaction['date']
                ticker_match = json_transaction['ticker'] == csv_transaction['ticker']
                amount_match = abs(json_transaction['amount'] - csv_transaction['amount']) < 0.01

                if date_match and ticker_match and amount_match:
                    # Add count and price to JSON transaction
                    json_transaction['count'] = csv_transaction['count']
                    json_transaction['price'] = csv_transaction['price']
                    matched_count += 1
                    matched = True
                    matched_indices.add(idx)
                    print(
                        f"Match found: {json_transaction['date']} {json_transaction['ticker']} {json_transaction['amount']}")
                    break

            if not matched:
                unmatched_count += 1
                print(
                    f"No match found for: {json_transaction['date']} {json_transaction['ticker']} {json_transaction['amount']}")
                # Find similar transactions for debugging
                similar_transactions = []
                for csv_tx in csv_transactions:
                    if csv_tx['ticker'] == json_transaction['ticker']:
                        similar_transactions.append(csv_tx)
                if similar_transactions:
                    print(f"  Similar transactions in CSV with same ticker:")
                    for tx in similar_transactions[:3]:
                        print(f"    {tx['date']} {tx['ticker']} {tx['amount']}")

        # Update metadata
        json_data['metadata']['matched_transactions'] = matched_count
        json_data['metadata']['unmatched_transactions'] = unmatched_count
        json_data['metadata']['processed_date'] = datetime.now().isoformat()

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\nSummary:")
        print(f"Successfully matched {matched_count} transactions")
        print(f"Unmatched transactions: {unmatched_count}")
        print(f"Output saved to {output_file}")

    except Exception as e:
        print(f"Error processing files: {str(e)}")
        import traceback
        traceback.print_exc()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Match security transactions from JSON and CSV files')
    parser.add_argument('--json-input', '-j', type=str, help='Input JSON file path')
    parser.add_argument('--csv-input', '-c', type=str, help='Input CSV file path')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file path')
    parser.add_argument('--data-dir', '-d', type=str, default='data',
                        help='Base data directory (default: data)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set logging level (default: INFO)')
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    # Set up directories following the pattern from get_secu_ops.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, args.data_dir)

    # Default input and output paths
    json_input = args.json_input
    csv_input = args.csv_input
    output_file = args.output

    # If no JSON input specified, look in data directory
    if not json_input:
        json_input = os.path.join(data_dir, "security_transactions", "security_transactions.json")

    # If no CSV input specified, look in data directory
    if not csv_input:
        csv_input = os.path.join(data_dir, "security_statements", "secu_statement.csv")

    # If no output specified, create in data directory
    if not output_file:
        output_dir = os.path.join(data_dir, "security_transactions")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "matched_security_transactions.json")

    # Check if input files exist
    if not os.path.exists(json_input):
        print(f"Error: JSON file '{json_input}' does not exist")
        return

    if not os.path.exists(csv_input):
        print(f"Error: CSV file '{csv_input}' does not exist")
        return

    # Process the files
    match_transactions(json_input, csv_input, output_file)


if __name__ == "__main__":
    main()