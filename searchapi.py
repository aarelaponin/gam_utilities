#!/usr/bin/env python
import os
from eodhd import APIClient
import pandas as pd

# Get EODHD API key
api_key = os.getenv('EODHD_API_TOKEN')
if api_key is None:
    raise ValueError("EODHD_API_TOKEN environment variable is not set")

api = APIClient(api_key)

# 1. First, let's get all available exchanges to identify the correct exchange code
print("Fetching available exchanges...")
try:
    exchanges = api.get_exchanges()
    print(f"Found {len(exchanges)} exchanges")

    # Look for exchanges that might be related to Tallinn/Estonia/Baltic
    tallinn_exchanges = exchanges[
        exchanges['Name'].str.contains('Tallinn', case=False) |
        exchanges['Name'].str.contains('Estonia', case=False) |
        exchanges['Name'].str.contains('Baltic', case=False)
        ]

    if not tallinn_exchanges.empty:
        print("\nPossible Tallinn/Baltic exchanges:")
        print(tallinn_exchanges[['Code', 'Name', 'OperatingMIC']])
    else:
        print("\nNo specific Tallinn/Baltic exchanges found. Showing all exchanges:")
        print(exchanges[['Code', 'Name', 'OperatingMIC']].head(10))
        print("...")

    # 2. Now let's check if we can find the LHV1T ticker in any of the exchanges
    search_term = "LHV"  # Using a broader search term

    print(f"\nSearching for '{search_term}' in available exchanges...")
    found_tickers = []

    # Try with some potential exchange codes
    potential_exchanges = ['TL', 'XTAL', 'BALTIC', 'EE']

    # Add Tallinn exchanges if found
    if not tallinn_exchanges.empty:
        potential_exchanges.extend(tallinn_exchanges['Code'].tolist())

    # Make sure we have unique exchange codes
    potential_exchanges = list(set(potential_exchanges))

    for exchange in potential_exchanges:
        try:
            print(f"Checking exchange: {exchange}")
            symbols = api.get_exchange_symbols(exchange)
            matching_symbols = symbols[symbols['Code'].str.contains(search_term, case=False)]

            if not matching_symbols.empty:
                print(f"Found {len(matching_symbols)} matching symbols in {exchange}:")
                print(matching_symbols[['Code', 'Name']])
                found_tickers.extend(matching_symbols['Code'].tolist())
        except Exception as e:
            print(f"Error checking exchange {exchange}: {e}")

    # If we didn't find anything with specific exchanges, try checking a few major ones
    if not found_tickers:
        major_exchanges = ['US', 'LSE', 'XETRA', 'CC']
        print("\nNo matches found in Baltic/Tallinn exchanges. Checking major exchanges...")

        for exchange in major_exchanges:
            try:
                print(f"Checking exchange: {exchange}")
                symbols = api.get_exchange_symbols(exchange)
                matching_symbols = symbols[symbols['Code'].str.contains(search_term, case=False)]

                if not matching_symbols.empty:
                    print(f"Found {len(matching_symbols)} matching symbols in {exchange}:")
                    print(matching_symbols[['Code', 'Name']])
                    found_tickers.extend(matching_symbols['Code'].tolist())
            except Exception as e:
                print(f"Error checking exchange {exchange}: {e}")

    if found_tickers:
        print("\nFound the following potential ticker symbols:")
        for ticker in found_tickers:
            print(ticker)
    else:
        print("\nNo matching tickers found. Consider checking if the API supports this market.")

except Exception as e:
    print(f"An error occurred: {e}")