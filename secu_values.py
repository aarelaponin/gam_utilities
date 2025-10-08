#!/usr/bin/env python3
import os
import json
import argparse
import yfinance as yf
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Calculate current value of bought assets.')
    parser.add_argument('--input-dir', '-i', type=str, default='data',
                        help='Input directory containing the JSON file (default: data)')
    parser.add_argument('--output-dir', '-o', type=str,
                        help='Output directory for the results (default: same as input-dir)')
    parser.add_argument('--input-file', type=str, default='matched_security_transactions.json',
                        help='Name of the input JSON file')
    parser.add_argument('--output-file', type=str, default='asset_current_values.json',
                        help='Name of the output JSON file')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set logging level (default: INFO)')
    return parser.parse_args()


def setup_logging(level: str):
    """Set up logging with the specified level."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_transaction_data(input_file_path: str) -> Dict:
    """Load the transaction data from the JSON file."""
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading input file: {e}")
        raise


def extract_bought_assets(transaction_data: Dict) -> List[Dict[str, Any]]:
    """Extract the assets that were bought."""
    bought_assets = []

    for transaction in transaction_data.get('security_transactions', []):
        # Check if this is a buy transaction with count and price attributes
        if (transaction.get('type') == 'buy' and
                'count' in transaction and
                'price' in transaction and
                transaction.get('count') is not None and
                transaction.get('price') is not None):
            bought_assets.append({
                'date': transaction.get('date'),
                'ticker': transaction.get('ticker'),
                'description': transaction.get('description'),
                'count': transaction.get('count'),
                'purchase_price': transaction.get('price'),
                'total_cost': transaction.get('amount') * -1  # Convert to positive value
            })

    logger.info(f"Extracted {len(bought_assets)} bought assets from transaction data")
    return bought_assets


def get_current_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    """
    Fetch current prices for the given tickers using yfinance.

    Args:
        tickers: List of ticker symbols

    Returns:
        Dictionary mapping ticker symbols to their current prices
    """
    current_prices = {}

    # Filter out bond tickers (they typically have special formats and aren't on regular exchanges)
    stock_tickers = [ticker for ticker in tickers if not (
            ticker.endswith('FA') or
            ticker.endswith('A') or
            ticker.endswith('T')  # Handle Estonian stocks with T suffix
    )]

    if not stock_tickers:
        logger.warning("No valid stock tickers found to fetch prices for")
        return current_prices

    try:
        # Create a ticker string for yfinance (comma-separated)
        ticker_str = ' '.join(stock_tickers)
        logger.info(f"Fetching current prices for: {ticker_str}")

        # Fetch data using yfinance
        data = yf.download(ticker_str, period="1d")

        # If only one ticker, the data structure is different
        if len(stock_tickers) == 1:
            if not data.empty:
                current_prices[stock_tickers[0]] = data['Close'].iloc[-1]
        else:
            # Extract the latest closing prices
            for ticker in stock_tickers:
                try:
                    if not data.empty and ('Close', ticker) in data.columns:
                        current_prices[ticker] = data[('Close', ticker)].iloc[-1]
                except Exception as e:
                    logger.warning(f"Could not get price for {ticker}: {e}")

        # Handle bonds and other special tickers with a placeholder price or estimation
        for ticker in tickers:
            if ticker not in current_prices:
                if ticker.endswith('FA') or ticker.endswith('A'):
                    logger.info(f"Bond ticker {ticker} - using 100% of purchase price as estimation")
                    current_prices[ticker] = None  # Will use purchase price in calculation
                elif ticker.endswith('T'):  # Estonian stocks
                    logger.info(f"Estonian stock {ticker} - using last known price")
                    current_prices[ticker] = None  # Will use purchase price in calculation

    except Exception as e:
        logger.error(f"Error fetching current prices: {e}")
        traceback.print_exc()

    logger.info(f"Successfully fetched prices for {len(current_prices)} out of {len(tickers)} tickers")
    return current_prices


def calculate_current_values(bought_assets: List[Dict], current_prices: Dict[str, Optional[float]]) -> List[Dict]:
    """
    Calculate the current values of the bought assets.

    Args:
        bought_assets: List of bought assets
        current_prices: Dictionary mapping ticker symbols to their current prices

    Returns:
        List of assets with their current values
    """
    valued_assets = []

    for asset in bought_assets:
        ticker = asset['ticker']
        count = asset['count']
        purchase_price = asset['purchase_price']

        # Get current price, use purchase price as fallback for special instruments
        current_price = current_prices.get(ticker)
        if current_price is None:
            current_price = purchase_price
            price_source = "estimated (using purchase price)"
        else:
            price_source = "market"

        # Calculate current value
        current_value = count * current_price
        purchase_value = count * purchase_price

        # Calculate gain/loss
        absolute_change = current_value - purchase_value
        percent_change = (absolute_change / purchase_value) * 100 if purchase_value else 0

        valued_assets.append({
            'date': asset['date'],
            'ticker': ticker,
            'description': asset['description'],
            'count': count,
            'purchase_price': purchase_price,
            'purchase_value': purchase_value,
            'current_price': current_price,
            'price_source': price_source,
            'current_value': current_value,
            'absolute_change': absolute_change,
            'percent_change': percent_change
        })

    return valued_assets


def save_results(valued_assets: List[Dict], output_file_path: str, original_data: Dict) -> None:
    """
    Save the results to a JSON file.

    Args:
        valued_assets: List of assets with their current values
        output_file_path: Path to the output file
        original_data: Original transaction data
    """
    try:
        # Calculate summary statistics
        total_current_value = sum(asset['current_value'] for asset in valued_assets)
        total_purchase_value = sum(asset['purchase_value'] for asset in valued_assets)
        total_absolute_change = total_current_value - total_purchase_value
        total_percent_change = (total_absolute_change / total_purchase_value) * 100 if total_purchase_value else 0

        # Create output data structure
        output_data = {
            'valued_assets': valued_assets,
            'summary': {
                'total_assets': len(valued_assets),
                'total_purchase_value': total_purchase_value,
                'total_current_value': total_current_value,
                'total_absolute_change': total_absolute_change,
                'total_percent_change': total_percent_change
            },
            'metadata': {
                'processed_date': datetime.now().isoformat(),
                'original_metadata': original_data.get('metadata', {}),
                'unique_tickers': len(set(asset['ticker'] for asset in valued_assets))
            }
        }

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Write output file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {output_file_path}")
        logger.info(f"Total current value: {total_current_value:.2f}")
        logger.info(f"Total absolute change: {total_absolute_change:.2f} ({total_percent_change:.2f}%)")

    except Exception as e:
        logger.error(f"Error saving results: {e}")
        traceback.print_exc()


def main():
    """Main execution function."""
    # Parse command line arguments
    args = parse_arguments()

    # Set up logging
    setup_logging(args.log_level)

    # Set up directories following the pattern from the provided script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, args.input_dir)

    # Default input and output paths
    input_dir = os.path.join(data_dir, "security_transactions")
    input_file_path = os.path.join(input_dir, args.input_file)

    # If no output directory specified, use same as input
    if args.output_dir:
        output_dir = os.path.join(base_dir, args.output_dir)
    else:
        output_dir = os.path.join(data_dir, "security_valuations")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    output_file_path = os.path.join(output_dir, args.output_file)

    try:
        # Load transaction data
        logger.info(f"Loading transaction data from {input_file_path}")
        transaction_data = load_transaction_data(input_file_path)

        # Extract bought assets
        bought_assets = extract_bought_assets(transaction_data)

        if not bought_assets:
            logger.warning("No bought assets found in the transaction data")
            return

        # Get unique tickers
        tickers = list(set(asset['ticker'] for asset in bought_assets))
        logger.info(f"Found {len(tickers)} unique tickers: {', '.join(tickers)}")

        # Get current prices
        current_prices = get_current_prices(tickers)

        # Calculate current values
        valued_assets = calculate_current_values(bought_assets, current_prices)

        # Save results
        save_results(valued_assets, output_file_path, transaction_data)

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()