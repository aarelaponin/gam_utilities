#!/usr/bin/env python
import os

from eodhd import APIClient

# Get EODHD API key
api_key = os.getenv('EODHD_API_TOKEN')
if api_key is None:
    raise ValueError("EODHD_API_TOKEN environment variable is not set")

api = APIClient(api_key)
tallinn_exchange_code = 'TL'
lhv_symbol = f"LHV1T.{tallinn_exchange_code}"

try:
    # Replace "LHV1T.XTAL" with your ticker symbol and its exchange
    data = api.get_eod_historical_stock_market_data(
        symbol="LHV1T.TL",  # Nasdaq Tallinn exchange
        period='d',
        from_date='2025-04-24',
        to_date='2025-04-24'
    )

    # Check if data is a DataFrame
    if hasattr(data, 'empty'):
        if not data.empty:
            last_close_price = data.iloc[-1]['close']
            print(f"Last close price: {last_close_price}")
        else:
            print("No data available for this date.")
    else:
        # Handle case where data is a dictionary (error response)
        print(f"Received error response: {data}")

        # Check common issues
        print("Troubleshooting:")
        print("1. Verify your API token is correct")
        print(f"2. Check if the ticker symbol {lhv_symbol} is valid for this API")
        print(f"3. Confirm the exchange code is correct ({tallinn_exchange_code} for Nasdaq Tallinn)")
        print("4. Ensure the date isn't a holiday or weekend")

except Exception as e:
    print(f"Error occurred: {e}")