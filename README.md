# Security Ticker Extraction Script

This script processes bank statement CSV files to extract security-related transactions and their ticker symbols, creating a JSON output file.

## Features

- Extracts ticker symbols from transaction descriptions
- Identifies buy and sell transactions
- Filters out non-security transactions (like commission fees and currency exchanges)
- Aggregates transactions with same date, ticker, and description
- Tracks operation counts for aggregated transactions
- Creates structured JSON output with metadata

## Usage

### Basic usage (using default directories):
```bash
python extract_security_tickers.py
```

### Specify input and output files:
```bash
python extract_security_tickers.py --input path/to/statement.csv --output path/to/output.json
```

### Use a custom data directory:
```bash
python extract_security_tickers.py --data-dir /path/to/data
```

## Directory Structure

The script follows a similar structure to the get_gaps.py script:

```
project_root/
├── data/
│   ├── bank_statements/
│   │   └── statement.csv
│   └── security_transactions/
│       └── security_transactions.json
└── extract_security_tickers.py
```

## Input Format

The script expects a CSV file with the following columns (as found in Estonian bank statements):
- `Selgitus`: Transaction description
- `Kuupäev`: Transaction date
- `Summa`: Transaction amount
- Other columns (optional)

## Output Format

The script generates a JSON file with:
- List of aggregated security transactions
- Each transaction includes:
  - Date
  - Ticker symbol
  - Amount (aggregated)
  - Description
  - Type (buy/sell, based on final amount)
  - Operations count (number of individual transactions aggregated)
- Metadata about the processing

## Aggregation Logic

The script aggregates transactions with the same:
- Date
- Ticker
- Description

When processing:
1. If the output file already exists, it loads existing data
2. New transactions are either:
   - Added to existing ones (amount summed, count incremented)
   - Created as new entries
3. The type (buy/sell) is determined by the final aggregated amount

## Ticker Extraction Logic

The script extracts tickers by:
1. Looking for symbols in parentheses, e.g., (ADBE)
2. Attempting to find ISIN codes
3. Only includes transactions where a ticker is successfully extracted

## Security Transaction Identification

Transactions are identified as security-related if they:
- Contain keywords like "Securities", "stock", "fund", etc.
- Do not include "Currency exchange" or "commission fee"