#!/usr/bin/env python3
"""
Generic Joget CSV Importer
Configurable importer for multiple Joget endpoints with automatic field mapping
"""

import csv
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import time
import sys
import argparse
import os
from abc import ABC, abstractmethod

# Base configuration
BASE_URL = "http://localhost:9999/jw/api/form"
DEFAULT_API_KEY = "8c04d5332aa34484a62fe1fb1e6e5900"


class DataProcessor(ABC):
    """Abstract base class for endpoint-specific data processing"""

    @abstractmethod
    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        pass

    @abstractmethod
    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        pass

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records if needed (default: no sorting)"""
        return records

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate record data. Returns error message if invalid, None if valid"""
        return None


class GLAccountProcessor(DataProcessor):
    """Processor for GL Account Master data"""

    def determine_parent_account(self, account_code: str) -> str:
        """Determine parent account based on account code ranges"""
        code = int(account_code)
        if 1000 <= code < 2000:
            return "1000"  # Assets
        elif 2000 <= code < 3000:
            return "2000"  # Liabilities
        elif 3000 <= code < 4000:
            return "3000"  # Income
        elif 4000 <= code < 5000:
            return "4000"  # Expenses
        elif 5000 <= code < 6000:
            return "5000"  # Equity
        else:
            return ""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        account_code = row['accountCode']
        current_date = datetime.now().strftime("%Y-%m-%d")
        is_parent = account_code in ['1000', '2000', '3000', '4000', '5000']

        return {
            "createdByName": "Admin Admin",
            "accountCode": account_code,
            "currencyRequired": row['currencyRequired'],
            "accountName": f"{account_code} - {row['accountName']}",
            "accountCategory": row['accountCategory'],
            "isReconcilable": row['isReconcilable'],
            "accountType": row['accountType'],
            "dateModified": current_date,
            "normalBalance": row['normalBalance'],
            "parentAccount": "" if is_parent else self.determine_parent_account(account_code),
            "dateCreated": current_date,
            "createdBy": "admin",
            "allowChildren": row['allowChildren'],
            "status": "Active"
        }

    def get_identifier(self, data: Dict[str, str]) -> str:
        return f"{data['accountCode']} - {data['accountName']}"

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        parent_accounts = [acc for acc in records if acc['accountCode'] in ['1000', '2000', '3000', '4000', '5000']]
        child_accounts = [acc for acc in records if acc['accountCode'] not in ['1000', '2000', '3000', '4000', '5000']]

        if len(parent_accounts) > 0:
            print(f"\nFound {len(parent_accounts)} parent accounts and {len(child_accounts)} child accounts")

        return parent_accounts + child_accounts


class GLFunctionProcessor(DataProcessor):
    """Processor for GL Business Function data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        payload = {
            "functionId": row.get('functionId', ''),
            "functionCode": row.get('functionCode', ''),
            "functionName": row.get('functionName', ''),
            "description": row.get('description', ''),
            "accountType": row.get('accountType', ''),
            "accountCategory": row.get('accountCategory', ''),
            "displayOrder": row.get('displayOrder', ''),
            "isActive": row.get('isActive', 'true'),
            "currencySpecific": row.get('currencySpecific', 'N'),
            "assetSpecific": row.get('assetSpecific', 'N'),
            "counterpartyRequired": row.get('counterpartyRequired', 'N'),
            "settlementType": row.get('settlementType', ''),
            "reconciliationRequired": row.get('reconciliationRequired', 'N'),
            "primaryYieldType": row.get('primaryYieldType', ''),
            "secondaryYieldType": row.get('secondaryYieldType', ''),
            "assetCategory": row.get('assetCategory', ''),
            "assetClass": row.get('assetClass', ''),
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin"
        }

        # Remove empty string values
        return {k: v for k, v in payload.items() if v != ''}

    def get_identifier(self, data: Dict[str, str]) -> str:
        return f"{data['functionCode']} - {data['functionName']}"


class TransactionMappingProcessor(DataProcessor):
    """Processor for Transaction Type Mapping data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Generate mapping ID from source info
        mapping_id = f"{row['sourceSystem']}_{row['sourceName']}_{row['externalCode']}".replace(" ", "_")

        payload = {
            "mappingId": mapping_id,
            "sourceSystem": row.get('sourceSystem', ''),
            "sourceName": row.get('sourceName', ''),
            "externalCode": row.get('externalCode', ''),
            "internalType": row.get('internalType', ''),
            "description": row.get('description', ''),
            "glDebitPattern": row.get('glDebitPattern', ''),
            "glCreditPattern": row.get('glCreditPattern', ''),
            "feePattern": row.get('feePattern', ''),
            "customerImpact": row.get('customerImpact', ''),
            "positionImpact": row.get('positionImpact', ''),
            "settlementDays": row.get('settlementDays', '0'),
            "status": row.get('status', 'Active'),
            "effectiveDate": row.get('effectiveDate', current_date),
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['feePattern']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def get_identifier(self, data: Dict[str, str]) -> str:
        return f"{data['sourceSystem']}/{data['sourceName']}/{data['externalCode']} - {data['description']}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate transaction mapping data"""
        # Check required fields
        required_fields = ['sourceSystem', 'sourceName', 'externalCode', 'internalType',
                           'description', 'glDebitPattern', 'glCreditPattern']
        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate enum values
        if row.get('customerImpact') and row['customerImpact'] not in ['Debit', 'Credit', 'None']:
            return f"Invalid customerImpact value: {row['customerImpact']}"

        if row.get('positionImpact') and row['positionImpact'] not in ['Increase', 'Decrease', 'None']:
            return f"Invalid positionImpact value: {row['positionImpact']}"

        if row.get('status') and row['status'] not in ['Active', 'Inactive']:
            return f"Invalid status value: {row['status']}"

        # Validate settlement days
        try:
            settlement_days = int(row.get('settlementDays', '0'))
            if settlement_days < 0 or settlement_days > 3:
                return f"Invalid settlementDays value: {settlement_days} (must be 0-3)"
        except ValueError:
            return f"Invalid settlementDays value: {row.get('settlementDays')} (must be a number)"

        return None


class CounterpartyMappingProcessor(DataProcessor):
    """Processor for Counterparty Transaction Mapping data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Generate mapping ID from counterparty and mapping info
        mapping_id = f"{row['counterpartyId']}_{row['sourceType']}_{row['mappingName']}".replace(" ", "_")

        # Convert boolean string to lowercase
        case_sensitive = 'true' if row.get('caseSensitive', 'false').lower() == 'true' else 'false'

        payload = {
            "mappingId": mapping_id,
            "counterpartyId": row.get('counterpartyId', ''),
            "sourceType": row.get('sourceType', ''),
            "mappingName": row.get('mappingName', ''),
            "matchingField": row.get('matchingField', ''),
            "matchOperator": row.get('matchOperator', ''),
            "matchValue": row.get('matchValue', ''),
            "caseSensitive": case_sensitive,
            "internalType": row.get('internalType', ''),
            "priority": row.get('priority', '1'),
            "status": row.get('status', 'Active'),
            "effectiveDate": row.get('effectiveDate', current_date),
            "ruleExpression": "",  # Optional field
            "descriptionOverride": "",  # Optional field
            "processingInstructions": "",  # Optional field
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['ruleExpression', 'descriptionOverride', 'processingInstructions']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def get_identifier(self, data: Dict[str, str]) -> str:
        return f"{data['counterpartyId']}/{data['sourceType']}/{data['mappingName']}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate counterparty mapping data"""
        # Check required fields
        required_fields = ['counterpartyId', 'sourceType', 'mappingName',
                           'matchingField', 'matchOperator', 'matchValue', 'internalType']
        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate match operator
        valid_operators = ['equals', 'contains', 'startsWith', 'endsWith', 'regex']
        if row.get('matchOperator') and row['matchOperator'] not in valid_operators:
            return f"Invalid matchOperator: {row['matchOperator']}. Must be one of: {', '.join(valid_operators)}"

        # Validate status
        if row.get('status') and row['status'] not in ['Active', 'Inactive']:
            return f"Invalid status value: {row['status']}"

        # Validate priority (should be numeric)
        try:
            priority = int(row.get('priority', '1'))
            if priority < 1 or priority > 999:
                return f"Invalid priority value: {priority} (must be 1-999)"
        except ValueError:
            return f"Invalid priority value: {row.get('priority')} (must be a number)"

        # Validate boolean fields
        if row.get('caseSensitive') and row['caseSensitive'].lower() not in ['true', 'false']:
            return f"Invalid caseSensitive value: {row['caseSensitive']} (must be true/false)"

        # Validate effectiveDate format if provided
        if row.get('effectiveDate'):
            try:
                datetime.strptime(row['effectiveDate'], "%Y-%m-%d")
            except ValueError:
                return f"Invalid date format for effectiveDate: {row['effectiveDate']} (must be YYYY-MM-DD)"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by counterpartyId and priority"""
        return sorted(records, key=lambda x: (x.get('counterpartyId', ''), int(x.get('priority', '999'))))


class BankTransactionProcessor(DataProcessor):
    """Processor for Bank Total Transaction data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Generate a unique transaction ID from TID
        transaction_id = str(row.get('TID', ''))

        # Get D/C indicator directly from CSV
        d_c = row.get('DC', 'D')

        # Format payment date
        payment_date = self.format_date(row.get('Date', ''))

        # Convert amount to string and ensure it's positive
        amount = float(row.get('Amount', '0'))
        payment_amount = str(abs(amount))

        # Extract customer ID (handle float conversion)
        customer_id = ''
        if row.get('Customer ID'):
            try:
                # Convert float to int then to string to remove decimal
                customer_id = str(int(float(row['Customer ID'])))
            except:
                customer_id = str(row['Customer ID'])

        # Build reference number from Reference field
        reference_number = row.get('Reference', '')

        # Handle internal type (INT column might be float)
        internal_type = ''
        if row.get('INT'):
            try:
                internal_type = str(int(float(row['INT'])))
            except:
                internal_type = str(row['INT'])

        # Handle type field (might be float)
        type_value = ''
        if row.get('Type'):
            try:
                type_value = str(int(float(row['Type'])))
            except:
                type_value = str(row['Type'])

        payload = {
            # Required fields from form
            "account_number": "",  # Not in CSV, will need to be set
            "payment_date": payment_date,
            "other_side_account": row.get('OS-Account', ''),
            "d_c": d_c,
            "payment_amount": payment_amount,
            "currency": row.get('CRR', 'EUR'),  # Default to EUR if not specified

            # Transaction identification
            "transaction_id": transaction_id,
            "document_nr": "",  # Not in CSV
            "reference_number": reference_number,
            "transaction_reference": reference_number,  # Use reference as transaction reference
            "provider_reference": "",  # Not in CSV
            "archival_number": "",  # Not in CSV
            "statement_reference": f"STMT.{transaction_id}",  # Generate from TID

            # Counterparty information
            "other_side_name": row.get('OS-Name', ''),
            "other_side_bank": "",  # Not in CSV
            "other_side_bic": row.get('OS-BIC', ''),

            # Transaction details
            "payment_description": row.get('Description', ''),
            "transaction_fee": "0",  # Not in CSV, default to 0
            "customer_id": customer_id,
            "initiator": "",  # Not in CSV

            # Type and categorization
            "internal_type": internal_type,
            "type": type_value,  # Cash flow type
            "transaction_type": "",  # Will be set by recognition process

            # System fields
            "status": "new",  # Default status for new transactions
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin",

            # Hidden fields - set as empty strings
            "statement_id": "",
            "account_type": "bank",  # Default to bank
            "trx_account_id": "",
            "allocated_amount": "0",
            "acc_post_id": "",
            "main_bank_total_trx": "",
        }

        # For bank transactions, we need to set account number based on your business logic
        # This is a placeholder - you'll need to adjust based on your requirements
        if not payload["account_number"]:
            # You might want to derive this from customer ID or have a mapping
            payload["account_number"] = f"ACC{customer_id}" if customer_id else "DEFAULT_ACC"

        # Remove empty string values except for optional fields
        optional_fields = ['statement_id', 'account_type', 'trx_account_id',
                           'allocated_amount', 'acc_post_id', 'main_bank_total_trx',
                           'transaction_fee', 'customer_id', 'initiator',
                           'internal_type', 'type', 'transaction_type', 'document_nr',
                           'provider_reference', 'archival_number', 'other_side_bank']

        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # Clean the date string
        date_str = date_str.strip()

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y%m%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If no format matches, return current date
        print(f"  ⚠️  Warning: Could not parse date '{date_str}', using current date")
        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        tid = data.get('transaction_id', 'N/A')
        account = data.get('account_number', 'N/A')
        amount = data.get('payment_amount', '0')
        currency = data.get('currency', 'EUR')
        d_c = data.get('d_c', '?')
        return f"TRX-{tid}: {account} {d_c} {amount} {currency}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate bank transaction data"""
        # Check required fields based on actual CSV structure
        required_fields = {
            'TID': 'Transaction ID',
            'Date': 'Date',
            'DC': 'Debit/Credit indicator',
            'Amount': 'Amount',
            'CRR': 'Currency'
        }

        for csv_field, display_name in required_fields.items():
            if not row.get(csv_field):
                return f"Missing required field: {display_name} ({csv_field})"

        # Validate numeric fields
        numeric_fields = {
            'TID': 'transaction ID',
            'Amount': 'amount'
        }

        for csv_field, display_name in numeric_fields.items():
            if row.get(csv_field):
                try:
                    float(row[csv_field])
                except ValueError:
                    return f"Invalid numeric value for {display_name}: {row[csv_field]}"

        # Validate currency code (should be 3 letters)
        currency = row.get('CRR', '')
        if currency and (len(currency) != 3 or not currency.isalpha()):
            return f"Invalid currency code: {currency} (must be 3 letters)"

        # Validate D/C indicator
        dc = row.get('DC', '')
        if dc and dc.upper() not in ['D', 'C']:
            return f"Invalid D/C value: {dc} (must be D or C)"

        # Validate date
        if row.get('Date'):
            try:
                self.format_date(row['Date'])
            except:
                return f"Invalid date format: {row['Date']}"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by date and transaction ID"""

        def sort_key(record):
            # Sort by date, then by TID
            date_str = self.format_date(record.get('Date', ''))
            try:
                tid = int(float(record.get('TID', '0')))
            except:
                tid = 0
            return (date_str, tid)

        return sorted(records, key=sort_key)


class SecurityTransactionProcessor(DataProcessor):
    """Processor for Security Total Transaction data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Generate a unique ID if not provided
        transaction_id = row.get('TID', '')

        # Convert numeric values to strings (API expects strings)
        quantity = str(row.get('Qnt', '0'))
        price = str(row.get('Price', '0'))
        amount = str(row.get('Amount', '0'))
        fee = str(row.get('Fee', '0'))
        total_amount = str(row.get('TAmount', '0'))

        # Map transaction type (handle Estonian or English)
        transaction_type = row.get('Type', '')
        type_lower = transaction_type.lower()

        if type_lower in ['müük', 'sell']:
            transaction_type = 'SELL'
        elif type_lower in ['ost', 'buy']:
            transaction_type = 'BUY'
        elif type_lower == 'split+':
            transaction_type = 'SPLIT_IN'
        elif type_lower == 'split-':
            transaction_type = 'SPLIT_OUT'
        elif type_lower in ['dividend', 'div']:
            transaction_type = 'DIVIDEND'
        elif type_lower in ['deposit', 'dep']:
            transaction_type = 'DEPOSIT'
        elif type_lower in ['withdrawal', 'wd']:
            transaction_type = 'WITHDRAWAL'
        else:
            # Keep original type in uppercase
            transaction_type = transaction_type.upper()

        payload = {
            "transaction_id": transaction_id,
            "value_date": self.format_date(row.get('VDate', '')),
            "transaction_date": self.format_date(row.get('TDate', '')),
            "type": transaction_type,
            "ticker": row.get('Ticker', ''),
            "quantity": quantity,
            "price": price,
            "currency": row.get('Curr', ''),
            "amount": amount,
            "fee": fee,
            "total_amount": total_amount,
            "internal_type": row.get('INT', ''),
            "description": row.get('Description', ''),
            "statement_reference": row.get('STRef', ''),
            "transaction_type": transaction_type,  # Duplicate field in API
            "status": "PENDING",  # Default status
            "reference": f"SEC-{transaction_id}",  # Generate reference
            "allocated_amount": "0",  # Default to 0
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin",
            # Optional fields - set as empty strings
            "trx_account_id": "",
            "bank_payment_trx_id": "",
            "bank_fee_trx_id": "",
            "acc_post_id": "",
            "statement_id": "",
            "comment": ""
        }

        # Remove empty string values except for optional fields
        optional_fields = ['trx_account_id', 'bank_payment_trx_id', 'bank_fee_trx_id',
                           'acc_post_id', 'statement_id', 'comment', 'allocated_amount']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from YYYY-MM-DD or other formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If no format matches, return current date
        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        return f"TRX-{data['transaction_id']}: {data['type']} {data['quantity']} {data['ticker']} @ {data['price']} {data['currency']}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate security transaction data"""
        # Check required fields
        required_fields = ['TID', 'VDate', 'TDate', 'Type', 'Ticker', 'Qnt', 'Price', 'Curr', 'Amount']
        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate numeric fields
        numeric_fields = {
            'Qnt': 'quantity',
            'Price': 'price',
            'Amount': 'amount',
            'Fee': 'fee',
            'TAmount': 'total_amount'
        }

        for csv_field, display_name in numeric_fields.items():
            if row.get(csv_field):
                try:
                    float(row[csv_field])
                except ValueError:
                    return f"Invalid numeric value for {display_name}: {row[csv_field]}"

        # Validate currency code (should be 3 letters)
        currency = row.get('Curr', '')
        if currency and (len(currency) != 3 or not currency.isalpha()):
            return f"Invalid currency code: {currency} (must be 3 letters)"

        # Validate transaction type
        valid_types = ['müük', 'sell', 'ost', 'buy', 'SELL', 'BUY', 'split+', 'split-',
                       'dividend', 'div', 'deposit', 'dep', 'withdrawal', 'wd']
        if row.get('Type'):
            type_lower = row['Type'].lower()
            if type_lower not in [t.lower() for t in valid_types]:
                # Allow any type but show a warning for unknown types
                print(
                    f"  ⚠️  Warning: Unknown transaction type '{row['Type']}' in row {row.get('TID', 'unknown')}. Will use as-is.")
                # Don't return an error - just proceed

        # Validate dates
        for date_field in ['VDate', 'TDate']:
            if row.get(date_field):
                try:
                    self.format_date(row[date_field])
                except:
                    return f"Invalid date format for {date_field}: {row[date_field]}"

        # Validate quantity is not zero
        try:
            quantity = float(row.get('Qnt', '0'))
            if quantity == 0:
                return "Quantity cannot be zero"
        except ValueError:
            pass  # Already validated above

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by transaction date and ID"""

        def sort_key(record):
            # Sort by transaction date, then by transaction ID
            date_str = self.format_date(record.get('TDate', ''))
            tid = int(record.get('TID', '0'))
            return (date_str, tid)

        return sorted(records, key=sort_key)


class AssetProcessor(DataProcessor):
    """Processor for Asset Master data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Convert numeric values to appropriate format
        # Handle lot size - convert to int if it's a number
        lot_size = row.get('lotSize', '1')
        if lot_size:
            try:
                lot_size = str(int(float(lot_size)))
            except (ValueError, TypeError):
                lot_size = '1'

        # Handle price decimals - convert to int
        price_decimals = row.get('priceDecimals', '2')
        if price_decimals:
            try:
                price_decimals = int(float(price_decimals))
            except (ValueError, TypeError):
                price_decimals = 2

        # Handle tick size - keep as string but ensure it's a valid decimal
        tick_size = row.get('tickSize', '0.01')
        if tick_size:
            try:
                tick_size = str(float(tick_size))
            except (ValueError, TypeError):
                tick_size = '0.01'

        # Handle yield percentages - convert to string
        primary_yield_pct = row.get('primaryYieldPct', '')
        if primary_yield_pct:
            try:
                primary_yield_pct = str(float(primary_yield_pct))
            except (ValueError, TypeError):
                primary_yield_pct = ''

        secondary_yield_pct = row.get('secondaryYieldPct', '')
        if secondary_yield_pct:
            try:
                secondary_yield_pct = str(float(secondary_yield_pct))
            except (ValueError, TypeError):
                secondary_yield_pct = ''

        # Handle ex-dividend days - convert to string
        ex_dividend_days = row.get('exDividendDays', '')
        if ex_dividend_days:
            try:
                # Check if it's a number
                ex_dividend_days = str(int(float(ex_dividend_days)))
            except (ValueError, TypeError):
                # If it's not a number, it might be a GL pattern (data issue in row 2)
                # In that case, leave it empty
                if '.' in str(ex_dividend_days) and '{' in str(ex_dividend_days):
                    ex_dividend_days = ''
                else:
                    ex_dividend_days = str(ex_dividend_days) if ex_dividend_days else ''

        # Handle SEDOL - ensure it's a string
        sedol = row.get('sedol', '')
        if sedol:
            sedol = str(sedol)

        # Handle CUSIP - ensure it's a string
        cusip = row.get('cusip', '')
        if cusip:
            cusip = str(cusip)

        # Convert assetSpecificGL to string (true/false)
        asset_specific_gl = row.get('assetSpecificGL', '')
        if asset_specific_gl:
            if isinstance(asset_specific_gl, bool):
                asset_specific_gl = 'true' if asset_specific_gl else 'false'
            elif str(asset_specific_gl).lower() in ['true', '1', 'yes']:
                asset_specific_gl = 'true'
            elif str(asset_specific_gl).lower() in ['false', '0', 'no']:
                asset_specific_gl = 'false'
            else:
                asset_specific_gl = ''

        payload = {
            # Required identifiers
            "assetId": row.get('assetId', ''),
            "ticker": row.get('ticker', ''),
            "assetName": row.get('assetName', ''),
            "shortName": row.get('shortName', ''),

            # Security identifiers
            "isin": row.get('isin', ''),
            "cusip": cusip,
            "sedol": sedol,

            # Classification
            "categoryCode": row.get('categoryCode', ''),
            "asset_class": row.get('asset_class', ''),
            "riskCategory": row.get('riskCategory', ''),

            # Trading information
            "primaryExchange": row.get('primaryExchange', ''),
            "tradingCurrency": row.get('tradingCurrency', ''),
            "tradingStatus": row.get('tradingStatus', 'Active'),
            "lotSize": lot_size,
            "priceDecimals": price_decimals,
            "tickSize": tick_size,

            # Investment characteristics
            "liquidityProfile": row.get('liquidityProfile', ''),
            "taxTreatment": row.get('taxTreatment', ''),
            "holdingPeriod": row.get('holdingPeriod', ''),

            # Yield information
            "primaryYieldType": row.get('primaryYieldType', ''),
            "primaryYieldPct": primary_yield_pct,
            "secondaryYieldType": row.get('secondaryYieldType', ''),
            "secondaryYieldPct": secondary_yield_pct,

            # Dividend/Income information
            "dividendFrequency": row.get('dividendFrequency', ''),
            "exDividendDays": ex_dividend_days,
            "paymentFrequency": row.get('dividendFrequency', ''),  # Map from dividendFrequency

            # GL Account patterns
            "glAccountPattern": row.get('glAccountPattern', ''),
            "incomeGLPattern": row.get('incomeGLPattern', ''),
            "unrealizedGLPattern": row.get('unrealizedGLPattern', ''),
            "assetSpecificGL": asset_specific_gl,

            # Bond-specific fields (will be empty for equities)
            "maturityDate": '',  # Not in CSV, would need to be added for bonds
            "couponRate": '',  # Not in CSV, would need to be added for bonds
            "callableFlag": '',  # Not in CSV
            "putFlag": '',  # Not in CSV
            "dayCountConvention": '',  # Not in CSV

            # System fields
            "dateCreated": current_date,
            "dateModified": current_date,
            "createdBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedBy": "admin",
            "modifiedByName": "Admin Admin",

            # ID field (might be auto-generated, but including for completeness)
            "id": row.get('assetId', '')  # Using assetId as the id
        }

        # Remove empty string values except for optional fields
        # Keep all fields that might legitimately be empty
        optional_fields = [
            'maturityDate', 'couponRate', 'callableFlag', 'putFlag',
            'dayCountConvention', 'primaryYieldPct', 'secondaryYieldPct',
            'secondaryYieldType', 'dividendFrequency', 'exDividendDays',
            'paymentFrequency', 'assetSpecificGL'
        ]

        # Clean up the payload
        cleaned_payload = {}
        for key, value in payload.items():
            # Keep the field if it has a value or if it's an optional field
            if value != '' or key in optional_fields:
                cleaned_payload[key] = value

        return cleaned_payload

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        asset_id = data.get('assetId', 'N/A')
        ticker = data.get('ticker', 'N/A')
        name = data.get('shortName', data.get('assetName', 'N/A'))
        return f"{asset_id}: {ticker} - {name}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate asset data"""
        # Check required fields
        required_fields = ['assetId', 'ticker', 'assetName', 'shortName',
                           'categoryCode', 'asset_class', 'tradingCurrency']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate currency code (should be 3 letters)
        currency = row.get('tradingCurrency', '')
        if currency and (len(currency) != 3 or not currency.isalpha()):
            return f"Invalid currency code: {currency} (must be 3 letters)"

        # Validate trading status
        if row.get('tradingStatus'):
            valid_statuses = ['Active', 'Inactive', 'Suspended', 'Delisted']
            if row['tradingStatus'] not in valid_statuses:
                return f"Invalid trading status: {row['tradingStatus']}. Must be one of: {', '.join(valid_statuses)}"

        # Validate numeric fields
        numeric_fields = {
            'lotSize': 'lot size',
            'priceDecimals': 'price decimals',
            'tickSize': 'tick size'
        }

        for csv_field, display_name in numeric_fields.items():
            if row.get(csv_field):
                try:
                    float(row[csv_field])
                except (ValueError, TypeError):
                    # Special handling for data issues (like GL patterns in wrong fields)
                    if '{' in str(row[csv_field]):
                        # This is likely a data error - GL pattern in wrong field
                        continue
                    return f"Invalid numeric value for {display_name}: {row[csv_field]}"

        # Validate yield percentages if present
        yield_fields = ['primaryYieldPct', 'secondaryYieldPct']
        for field in yield_fields:
            if row.get(field) and row[field] != '':
                try:
                    yield_val = float(row[field])
                    if yield_val < 0 or yield_val > 100:
                        return f"Invalid {field}: {yield_val} (must be between 0 and 100)"
                except (ValueError, TypeError):
                    if row[field] is not None:  # None is acceptable
                        return f"Invalid numeric value for {field}: {row[field]}"

        # Validate ISIN format (2 letters + 10 alphanumeric)
        isin = row.get('isin', '')
        if isin:
            if len(isin) != 12:
                return f"Invalid ISIN length: {isin} (must be 12 characters)"
            if not isin[:2].isalpha():
                return f"Invalid ISIN format: {isin} (must start with 2 letters)"

        # Validate asset class format
        asset_class = row.get('asset_class', '')
        if asset_class:
            # Expected format: XX_N (e.g., EQ_1, FI_2)
            if '_' not in asset_class:
                return f"Invalid asset_class format: {asset_class} (expected format: XX_N)"

        # Check for data consistency issues
        # If exDividendDays contains a GL pattern, it's a data error
        ex_div = row.get('exDividendDays', '')
        if ex_div and '{' in str(ex_div):
            # This is a known data issue in the CSV - don't fail validation, we'll handle it in prepare_data
            print(
                f"  ⚠️  Warning: GL pattern found in exDividendDays field for {row.get('assetId', 'unknown')}, will clear this field")

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by asset class and then by assetId"""

        def sort_key(record):
            # Sort by asset_class first, then by assetId
            asset_class = record.get('asset_class', 'ZZ_9')  # Put unknown at end
            asset_id = record.get('assetId', 'ZZZ999999')
            return (asset_class, asset_id)

        sorted_records = sorted(records, key=sort_key)

        # Print summary of records by asset class
        asset_class_counts = {}
        for record in sorted_records:
            asset_class = record.get('asset_class', 'UNKNOWN')
            asset_class_counts[asset_class] = asset_class_counts.get(asset_class, 0) + 1

        if len(asset_class_counts) > 1:
            print(f"\nAsset distribution:")
            for asset_class, count in sorted(asset_class_counts.items()):
                class_name = {
                    'EQ_1': 'Equities (Tier 1)',
                    'EQ_2': 'Equities (Tier 2)',
                    'FI_1': 'Fixed Income (Tier 1)',
                    'FI_2': 'Fixed Income (Tier 2)',
                    'FD_1': 'Funds (Tier 1)',
                    'FD_2': 'Funds (Tier 2)'
                }.get(asset_class, asset_class)
                print(f"  {class_name}: {count} assets")

        return sorted_records


class FxRatesProcessor(DataProcessor):
    """Processor for FX Rates Management data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Convert numeric values to strings (API expects strings)
        exchange_rate = str(row.get('exchangeRate', ''))
        previous_rate = str(row.get('previousRate', ''))
        change_percent = str(row.get('changePercent', ''))
        bid_rate = str(row.get('bidRate', ''))
        ask_rate = str(row.get('askRate', ''))
        mid_rate = str(row.get('midRate', ''))
        spread = str(row.get('spread', ''))

        # Format dates
        effective_date = self.format_date(row.get('effectiveDate', ''))
        last_import_date = self.format_date(row.get('lastImportDate', '')) if row.get('lastImportDate') else ''

        payload = {
            # Rate identification
            "rateId": row.get('rateId', ''),
            "id": row.get('rateId', ''),  # API might expect 'id' field

            # Currency pair
            "baseCurrency": row.get('baseCurrency', 'EUR'),
            "targetCurrency": row.get('targetCurrency', ''),

            # Exchange rates
            "exchangeRate": exchange_rate,
            "previousRate": previous_rate,
            "changePercent": change_percent,

            # Bid/Ask/Mid rates
            "bidRate": bid_rate,
            "askRate": ask_rate,
            "midRate": mid_rate,
            "spread": spread,

            # Rate metadata
            "rateType": row.get('rateType', 'spot'),
            "effectiveDate": effective_date,
            "effectiveTime": row.get('effectiveTime', '09:00:00'),

            # Import configuration
            "importSource": row.get('importSource', 'manual'),
            "importFrequency": row.get('importFrequency', 'daily'),
            "importStatus": row.get('importStatus', 'completed'),
            "lastImportDate": last_import_date,
            "lastImportTime": row.get('lastImportTime', ''),

            # API configuration
            "apiEndpoint": row.get('apiEndpoint', ''),
            "apiKey": row.get('apiKey', ''),

            # Settings and status
            "settings": row.get('settings', ''),
            "status": row.get('status', 'active'),

            # System fields
            "dateCreated": row.get('dateCreated', current_date),
            "dateModified": row.get('dateModified', current_date),
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": row.get('modifiedBy', 'admin'),
            "createdByName": row.get('createdByName', 'Admin Admin'),
            "modifiedByName": row.get('modifiedByName', 'Admin Admin'),

            # Additional fields from API that might be needed
            "importFile": "",  # Empty for API imports
        }

        # Remove empty string values except for optional fields
        optional_fields = ['importFile', 'apiEndpoint', 'apiKey', 'settings',
                           'lastImportTime', 'previousRate', 'changePercent',
                           'bidRate', 'askRate', 'midRate', 'spread']

        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # Clean the date string
        date_str = date_str.strip()

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y%m%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If no format matches, return current date
        print(f"  ⚠️  Warning: Could not parse date '{date_str}', using current date")
        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        rate_id = data.get('rateId', 'N/A')
        base = data.get('baseCurrency', 'N/A')
        target = data.get('targetCurrency', 'N/A')
        rate = data.get('exchangeRate', 'N/A')
        date = data.get('effectiveDate', 'N/A')
        return f"{rate_id}: {base}/{target} @ {rate} ({date})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate FX rate data"""
        # Check required fields
        required_fields = ['rateId', 'baseCurrency', 'targetCurrency',
                           'exchangeRate', 'effectiveDate']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate currency codes (should be 3 letters)
        for currency_field in ['baseCurrency', 'targetCurrency']:
            currency = row.get(currency_field, '')
            if currency and (len(currency) != 3 or not currency.isalpha()):
                return f"Invalid currency code for {currency_field}: {currency} (must be 3 letters)"

        # Validate that base and target currencies are different
        if row.get('baseCurrency') == row.get('targetCurrency'):
            return "Base currency and target currency cannot be the same"

        # Validate numeric fields
        numeric_fields = {
            'exchangeRate': 'exchange rate',
            'previousRate': 'previous rate',
            'changePercent': 'change percent',
            'bidRate': 'bid rate',
            'askRate': 'ask rate',
            'midRate': 'mid rate',
            'spread': 'spread'
        }

        for csv_field, display_name in numeric_fields.items():
            if row.get(csv_field):  # Only validate if field is present
                try:
                    value = float(row[csv_field])
                    # Exchange rates should be positive
                    if csv_field in ['exchangeRate', 'bidRate', 'askRate', 'midRate'] and value <= 0:
                        return f"Invalid {display_name}: {value} (must be positive)"
                    # Spread should be non-negative
                    if csv_field == 'spread' and value < 0:
                        return f"Invalid {display_name}: {value} (must be non-negative)"
                except ValueError:
                    return f"Invalid numeric value for {display_name}: {row[csv_field]}"

        # Validate rate type
        valid_rate_types = ['spot', 'forward', 'fixing', 'closing', 'opening']
        if row.get('rateType'):
            if row['rateType'] not in valid_rate_types:
                return f"Invalid rate type: {row['rateType']}. Must be one of: {', '.join(valid_rate_types)}"

        # Validate status
        valid_statuses = ['active', 'inactive', 'pending', 'archived']
        if row.get('status'):
            if row['status'] not in valid_statuses:
                return f"Invalid status: {row['status']}. Must be one of: {', '.join(valid_statuses)}"

        # Validate import frequency
        valid_frequencies = ['realtime', 'hourly', 'daily', 'weekly', 'manual']
        if row.get('importFrequency'):
            if row['importFrequency'] not in valid_frequencies:
                return f"Invalid import frequency: {row['importFrequency']}. Must be one of: {', '.join(valid_frequencies)}"

        # Validate import status
        valid_import_statuses = ['pending', 'processing', 'completed', 'failed']
        if row.get('importStatus'):
            if row['importStatus'] not in valid_import_statuses:
                return f"Invalid import status: {row['importStatus']}. Must be one of: {', '.join(valid_import_statuses)}"

        # Validate import source
        valid_sources = ['ecb', 'reuters', 'bloomberg', 'api', 'file', 'manual']
        if row.get('importSource'):
            if row['importSource'] not in valid_sources:
                return f"Invalid import source: {row['importSource']}. Must be one of: {', '.join(valid_sources)}"

        # Validate date format
        if row.get('effectiveDate'):
            try:
                self.format_date(row['effectiveDate'])
            except:
                return f"Invalid date format for effectiveDate: {row['effectiveDate']}"

        if row.get('lastImportDate'):
            try:
                self.format_date(row['lastImportDate'])
            except:
                return f"Invalid date format for lastImportDate: {row['lastImportDate']}"

        # Validate time format (HH:MM:SS)
        for time_field in ['effectiveTime', 'lastImportTime']:
            if row.get(time_field):
                time_str = row[time_field]
                if time_str:  # Only validate if not empty
                    parts = time_str.split(':')
                    if len(parts) != 3:
                        return f"Invalid time format for {time_field}: {time_str} (expected HH:MM:SS)"
                    try:
                        hours, minutes, seconds = map(int, parts)
                        if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                            return f"Invalid time values for {time_field}: {time_str}"
                    except ValueError:
                        return f"Invalid time format for {time_field}: {time_str}"

        # Validate bid/ask spread consistency
        if row.get('bidRate') and row.get('askRate'):
            try:
                bid = float(row['bidRate'])
                ask = float(row['askRate'])
                if bid > ask:
                    return f"Bid rate ({bid}) cannot be higher than ask rate ({ask})"

                # If mid rate is provided, validate it's between bid and ask
                if row.get('midRate'):
                    mid = float(row['midRate'])
                    if not (bid <= mid <= ask):
                        return f"Mid rate ({mid}) must be between bid ({bid}) and ask ({ask})"

                # If spread is provided, validate it matches bid-ask difference
                if row.get('spread'):
                    spread = float(row['spread'])
                    calculated_spread = round((ask - bid) * 10000, 0)  # Convert to pips
                    if abs(spread - calculated_spread) > 1:  # Allow 1 pip tolerance
                        return f"Spread ({spread}) doesn't match bid-ask difference ({calculated_spread} pips)"
            except ValueError:
                pass  # Already validated above

        # Validate change percent is reasonable (e.g., not more than 50% daily change)
        if row.get('changePercent'):
            try:
                change = float(row['changePercent'])
                if abs(change) > 50:
                    return f"Unusually large change percent: {change}% (more than 50%)"
            except ValueError:
                pass  # Already validated above

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by effective date and currency pair"""

        def sort_key(record):
            # Sort by effective date (newest first), then by currency pair
            date_str = self.format_date(record.get('effectiveDate', ''))
            base = record.get('baseCurrency', '')
            target = record.get('targetCurrency', '')
            return (date_str, base, target)

        sorted_records = sorted(records, key=sort_key, reverse=True)

        # Print summary of records by currency pair
        currency_pairs = {}
        for record in sorted_records:
            pair = f"{record.get('baseCurrency', 'N/A')}/{record.get('targetCurrency', 'N/A')}"
            currency_pairs[pair] = currency_pairs.get(pair, 0) + 1

        if len(currency_pairs) > 0:
            print(f"\nFX Rate distribution:")
            for pair, count in sorted(currency_pairs.items()):
                print(f"  {pair}: {count} rates")

        # Get date range
        if sorted_records:
            dates = [self.format_date(r.get('effectiveDate', '')) for r in sorted_records]
            min_date = min(dates)
            max_date = max(dates)
            print(f"\nDate range: {min_date} to {max_date}")

        return sorted_records


class CustomerProcessor(DataProcessor):
    """Processor for Customer Master data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Determine customer type based on available data
        customer_type = row.get('customerType', '')
        if not customer_type:
            # Infer type from available fields
            if row.get('personalId'):
                customer_type = 'Individual'
            elif row.get('registrationNumber'):
                customer_type = 'Corporate'

        # Generate customer ID if not provided
        customer_id = row.get('customerId', '')
        if not customer_id:
            # Generate based on type and timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            if customer_type == 'Individual':
                customer_id = f"CUST-IND{timestamp}"
            elif customer_type == 'Corporate':
                customer_id = f"CUST-CRP{timestamp}"
            else:
                customer_id = f"CUST-{timestamp}"

        # Format KYC expiry date if provided
        kyc_expiry = row.get('kycExpiryDate', '')
        if kyc_expiry:
            kyc_expiry = self.format_date(kyc_expiry)

        payload = {
            # System fields
            "createdByName": row.get('createdByName', 'Admin Admin'),
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedByName": row.get('modifiedByName', 'Admin Admin'),
            "modifiedBy": row.get('modifiedBy', 'admin'),
            "dateCreated": row.get('dateCreated', current_date),
            "dateModified": row.get('dateModified', current_date),

            # Basic Information
            "customerId": customer_id,
            "customerType": customer_type,
            "id": row.get('id', customer_id),  # Use customerId as id if not provided

            # Individual fields (only if Individual type)
            "customerFirstName": row.get('customerFirstName', ''),
            "customerLastName": row.get('customerLastName', ''),
            "personalId": row.get('personalId', ''),

            # Corporate fields (only if Corporate type)
            "customerName": row.get('customerName', ''),
            "registrationNumber": row.get('registrationNumber', ''),
            "vatNumber": row.get('vatNumber', ''),
            "incorporationCountry": row.get('incorporationCountry', ''),

            # KYC Information
            "kycStatus": row.get('kycStatus', 'pending'),
            "kycExpiryDate": kyc_expiry,
            "riskCategory": row.get('riskCategory', ''),
            "relationshipManager": row.get('relationshipManager', ''),
        }

        # Clean up fields based on customer type
        if customer_type == 'Individual':
            # Remove corporate-specific fields for individuals
            fields_to_remove = ['customerName', 'registrationNumber', 'vatNumber', 'incorporationCountry']
            for field in fields_to_remove:
                payload.pop(field, None)
        elif customer_type == 'Corporate':
            # Remove individual-specific fields for corporates
            fields_to_remove = ['customerFirstName', 'customerLastName', 'personalId']
            for field in fields_to_remove:
                payload.pop(field, None)

        # Remove empty string values except for optional fields
        optional_fields = ['vatNumber', 'kycExpiryDate']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return ""

        # Clean the date string
        date_str = date_str.strip()

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y%m%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If no format matches, return empty string
        print(f"  ⚠️  Warning: Could not parse date '{date_str}'")
        return ""

    def get_identifier(self, data: Dict[str, str]) -> str:
        customer_id = data.get('customerId', 'N/A')
        customer_type = data.get('customerType', 'N/A')

        if customer_type == 'Individual':
            first_name = data.get('customerFirstName', '')
            last_name = data.get('customerLastName', '')
            name = f"{first_name} {last_name}".strip() or 'N/A'
        elif customer_type == 'Corporate':
            name = data.get('customerName', 'N/A')
        else:
            name = 'Unknown'

        return f"{customer_id}: {name} ({customer_type})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate customer data"""
        # Determine customer type
        customer_type = row.get('customerType', '')
        if not customer_type:
            # Try to infer from data
            if row.get('personalId') or row.get('customerFirstName') or row.get('customerLastName'):
                customer_type = 'Individual'
            elif row.get('registrationNumber') or row.get('customerName'):
                customer_type = 'Corporate'
            else:
                return "Cannot determine customer type (Individual/Corporate)"

        # Validate customer type value
        if customer_type not in ['Individual', 'Corporate']:
            return f"Invalid customer type: {customer_type}. Must be 'Individual' or 'Corporate'"

        # Validate Individual-specific required fields
        if customer_type == 'Individual':
            required_fields = ['customerFirstName', 'customerLastName', 'personalId']
            for field in required_fields:
                if not row.get(field):
                    return f"Missing required field for Individual customer: {field}"

        # Validate Corporate-specific required fields
        elif customer_type == 'Corporate':
            required_fields = ['customerName', 'registrationNumber', 'incorporationCountry']
            for field in required_fields:
                if not row.get(field):
                    return f"Missing required field for Corporate customer: {field}"

        # Validate KYC Status
        if row.get('kycStatus'):
            valid_statuses = ['pending', 'inprogress', 'completed', 'expired']
            if row['kycStatus'] not in valid_statuses:
                return f"Invalid KYC status: {row['kycStatus']}. Must be one of: {', '.join(valid_statuses)}"

        # Validate Risk Category
        if row.get('riskCategory'):
            valid_categories = ['low', 'medium', 'high']
            if row['riskCategory'] not in valid_categories:
                return f"Invalid risk category: {row['riskCategory']}. Must be one of: {', '.join(valid_categories)}"

        # Validate Incorporation Country (for Corporate)
        if customer_type == 'Corporate' and row.get('incorporationCountry'):
            valid_countries = ['EE', 'FI', 'US', 'UK', 'SG', 'HK', 'CH', 'LU', 'OTHER']
            if row['incorporationCountry'] not in valid_countries:
                return f"Invalid incorporation country: {row['incorporationCountry']}. Must be one of: {', '.join(valid_countries)}"

        # Validate Relationship Manager
        if row.get('relationshipManager'):
            valid_managers = ['rm001', 'rm002', 'rm003', 'rm004']
            if row['relationshipManager'] not in valid_managers:
                # Allow any value but show a warning
                print(f"  ⚠️  Warning: Unknown relationship manager code: {row['relationshipManager']}")

        # Validate date format if provided
        if row.get('kycExpiryDate'):
            formatted_date = self.format_date(row['kycExpiryDate'])
            if not formatted_date:
                return f"Invalid date format for kycExpiryDate: {row['kycExpiryDate']}"

        # Validate VAT Number format (optional, but if provided should be valid)
        if row.get('vatNumber'):
            vat = row['vatNumber'].strip()
            # Basic VAT validation - typically starts with country code followed by numbers
            if len(vat) < 4:
                return f"Invalid VAT number format: {vat} (too short)"

        # Validate Personal ID format (for Individual)
        if customer_type == 'Individual' and row.get('personalId'):
            personal_id = row['personalId'].strip()
            if len(personal_id) < 5:
                return f"Invalid personal ID format: {personal_id} (too short)"

        # Validate Registration Number format (for Corporate)
        if customer_type == 'Corporate' and row.get('registrationNumber'):
            reg_num = row['registrationNumber'].strip()
            if len(reg_num) < 3:
                return f"Invalid registration number format: {reg_num} (too short)"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by customer type and then by name/ID"""

        def sort_key(record):
            # Determine customer type
            customer_type = record.get('customerType', '')
            if not customer_type:
                if record.get('personalId'):
                    customer_type = 'Individual'
                elif record.get('registrationNumber'):
                    customer_type = 'Corporate'
                else:
                    customer_type = 'Unknown'

            # Get name for sorting
            if customer_type == 'Individual':
                name = f"{record.get('customerLastName', '')} {record.get('customerFirstName', '')}"
            elif customer_type == 'Corporate':
                name = record.get('customerName', '')
            else:
                name = ''

            # Sort by type first (Corporate before Individual), then by name
            type_order = {'Corporate': 0, 'Individual': 1, 'Unknown': 2}
            return (type_order.get(customer_type, 3), name.lower())

        sorted_records = sorted(records, key=sort_key)

        # Print summary
        type_counts = {'Individual': 0, 'Corporate': 0, 'Unknown': 0}
        for record in sorted_records:
            customer_type = record.get('customerType', '')
            if not customer_type:
                if record.get('personalId'):
                    customer_type = 'Individual'
                elif record.get('registrationNumber'):
                    customer_type = 'Corporate'
                else:
                    customer_type = 'Unknown'
            type_counts[customer_type] = type_counts.get(customer_type, 0) + 1

        if sum(type_counts.values()) > 0:
            print(f"\nCustomer distribution:")
            for ctype, count in sorted(type_counts.items()):
                if count > 0:
                    print(f"  {ctype}: {count} customers")

        return sorted_records


class CustomerAccountProcessor(DataProcessor):
    """Processor for Customer Account data"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Determine which customer ID field to use based on customer type
        customer_type = row.get('customerType', '')
        if customer_type == 'Individual':
            customer_id_value = row.get('individualCustomerId', '')
        else:  # Corporate or Institution
            customer_id_value = row.get('corporateCustomerId', '')

        # Build the payload
        payload = {
            # Account identification
            "accountId": row.get('accountId', ''),
            "id": row.get('accountId', ''),  # Some APIs expect 'id' field
            "accountNumber": row.get('accountNumber', ''),

            # Customer information
            "customerId": row.get('customerId', ''),
            "customerType": customer_type,
            "individualCustomerId": row.get('individualCustomerId', ''),
            "corporateCustomerId": row.get('corporateCustomerId', ''),

            # Account configuration
            "service_type": row.get('service_type', 'Trading'),
            "primaryCurrency": row.get('primaryCurrency', 'EUR'),
            "status": row.get('status', 'Active'),
            "openingDate": self.format_date(row.get('openingDate', current_date)),

            # Counterparty relationships
            "primaryBankId": row.get('primaryBankId', ''),
            "primaryBrokerId": row.get('primaryBrokerId', ''),
            "primaryCustodianId": row.get('primaryCustodianId', ''),

            # GL Configuration
            "glTemplate": row.get('glTemplate', ''),

            # System fields
            "dateCreated": self.format_date(row.get('dateCreated', current_date)),
            "dateModified": current_date,
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['primaryBrokerId', 'primaryCustodianId', 'glTemplate',
                           'individualCustomerId', 'corporateCustomerId']

        # Only include broker/custodian for relevant service types
        service_type = row.get('service_type', '')
        if service_type == 'CashOnly':
            # Cash only accounts don't need broker or custodian
            payload.pop('primaryBrokerId', None)
            payload.pop('primaryCustodianId', None)
        elif service_type == 'CustodyOnly':
            # Custody only accounts don't need broker
            payload.pop('primaryBrokerId', None)

        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If no format matches, return current date
        print(f"  ⚠️  Warning: Could not parse date '{date_str}', using current date")
        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        account_id = data.get('accountId', 'N/A')
        customer_id = data.get('customerId', 'N/A')
        account_number = data.get('accountNumber', 'N/A')
        service_type = data.get('service_type', 'N/A')
        currency = data.get('primaryCurrency', 'N/A')
        return f"{account_id}: {customer_id} - {account_number} ({service_type}/{currency})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate customer account data"""
        # Check required fields
        required_fields = ['accountId', 'customerId', 'customerType',
                           'accountNumber', 'service_type', 'primaryCurrency']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate customer type
        valid_customer_types = ['Individual', 'Corporate', 'Institution']
        if row.get('customerType') not in valid_customer_types:
            return f"Invalid customer type: {row['customerType']}. Must be one of: {', '.join(valid_customer_types)}"

        # Validate that appropriate customer ID is provided
        customer_type = row.get('customerType')
        if customer_type == 'Individual':
            if not row.get('individualCustomerId'):
                return "Individual customer type requires individualCustomerId"
            if row.get('corporateCustomerId'):
                return "Individual customer should not have corporateCustomerId"
        elif customer_type in ['Corporate', 'Institution']:
            if not row.get('corporateCustomerId'):
                return f"{customer_type} customer type requires corporateCustomerId"
            if row.get('individualCustomerId'):
                return f"{customer_type} customer should not have individualCustomerId"

        # Validate service type
        valid_service_types = ['Trading', 'CashOnly', 'CustodyOnly', 'PrimeBrokerage']
        if row.get('service_type') not in valid_service_types:
            return f"Invalid service type: {row['service_type']}. Must be one of: {', '.join(valid_service_types)}"

        # Validate currency code (should be 3 letters)
        currency = row.get('primaryCurrency', '')
        if currency and (len(currency) != 3 or not currency.isalpha()):
            return f"Invalid currency code: {currency} (must be 3 letters)"

        # Validate status
        valid_statuses = ['Active', 'Dormant', 'Closed']
        if row.get('status') and row['status'] not in valid_statuses:
            return f"Invalid status: {row['status']}. Must be one of: {', '.join(valid_statuses)}"

        # Validate required counterparties based on service type
        service_type = row.get('service_type')
        if service_type in ['Trading', 'PrimeBrokerage']:
            if not row.get('primaryBankId'):
                return f"{service_type} accounts require a primary bank"

        # Validate account number format (basic check)
        account_number = row.get('accountNumber', '')
        if account_number:
            # Check for reasonable length
            if len(account_number) < 10 or len(account_number) > 34:
                return f"Account number length seems invalid: {len(account_number)} characters"

        # Validate date format
        if row.get('openingDate'):
            try:
                self.format_date(row['openingDate'])
            except:
                return f"Invalid date format for openingDate: {row['openingDate']}"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by customer ID and then by account ID"""

        def sort_key(record):
            customer_id = record.get('customerId', 'ZZZ')
            account_id = record.get('accountId', 'ZZZ')
            return (customer_id, account_id)

        sorted_records = sorted(records, key=sort_key)

        # Print summary
        customer_counts = {}
        service_type_counts = {}
        currency_counts = {}

        for record in sorted_records:
            customer_id = record.get('customerId', 'Unknown')
            service_type = record.get('service_type', 'Unknown')
            currency = record.get('primaryCurrency', 'Unknown')

            customer_counts[customer_id] = customer_counts.get(customer_id, 0) + 1
            service_type_counts[service_type] = service_type_counts.get(service_type, 0) + 1
            currency_counts[currency] = currency_counts.get(currency, 0) + 1

        print(f"\nAccount distribution summary:")
        print(f"  Total customers with accounts: {len(customer_counts)}")
        print(f"  Customers with multiple accounts: {sum(1 for count in customer_counts.values() if count > 1)}")

        print(f"\n  Service types:")
        for service_type, count in sorted(service_type_counts.items()):
            print(f"    {service_type}: {count} accounts")

        print(f"\n  Currencies:")
        for currency, count in sorted(currency_counts.items()):
            print(f"    {currency}: {count} accounts")

        return sorted_records


class MatchingRulesProcessor(DataProcessor):
    """Processor for F14 Matching Rules (cp_txn_mapping)"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Handle case sensitivity as boolean string
        case_sensitive = 'true' if row.get('caseSensitive', 'false').lower() == 'true' else 'false'

        payload = {
            # Rule identification
            "mapping_id": row.get('mapping_id', ''),
            "id": row.get('mapping_id', ''),  # API might expect 'id' field
            "mappingName": row.get('mappingName', ''),

            # Matching configuration
            "counterpartyId": row.get('counterpartyId', ''),
            "sourceType": row.get('sourceType', ''),
            "matchingField": row.get('matchingField', ''),
            "matchOperator": row.get('matchOperator', ''),
            "matchValue": row.get('matchValue', ''),
            "caseSensitive": case_sensitive,

            # Output configuration
            "internalType": row.get('internalType', ''),
            "priority": row.get('priority', '3'),

            # Control fields
            "status": row.get('status', 'Active'),
            "effectiveDate": self.format_date(row.get('effectiveDate', current_date)),

            # System fields
            "dateCreated": self.format_date(row.get('dateCreated', current_date)),
            "dateModified": current_date,
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['caseSensitive']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        mapping_id = data.get('mapping_id', 'N/A')
        name = data.get('mappingName', 'N/A')
        cp = data.get('counterpartyId', 'N/A')
        internal_type = data.get('internalType', 'N/A')
        return f"{mapping_id}: {name} ({cp} -> {internal_type})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate matching rule data"""
        # Check required fields
        required_fields = ['mapping_id', 'mappingName', 'counterpartyId',
                           'sourceType', 'matchingField', 'matchOperator',
                           'matchValue', 'internalType']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate source type
        valid_source_types = ['bank', 'secu']
        if row['sourceType'] not in valid_source_types:
            return f"Invalid source type: {row['sourceType']}. Must be one of: {', '.join(valid_source_types)}"

        # Validate matching field
        valid_matching_fields = ['type', 'd_c', 'description', 'reference',
                                 'other_side_name', 'other_side_bic', 'ticker', 'combined']
        if row['matchingField'] not in valid_matching_fields:
            return f"Invalid matching field: {row['matchingField']}. Must be one of: {', '.join(valid_matching_fields)}"

        # Validate match operator
        valid_operators = ['equals', 'contains', 'startsWith', 'endsWith', 'regex']
        if row['matchOperator'] not in valid_operators:
            return f"Invalid match operator: {row['matchOperator']}. Must be one of: {', '.join(valid_operators)}"

        # Validate priority
        try:
            priority = int(row.get('priority', '3'))
            if priority < 1 or priority > 5:
                return f"Invalid priority: {priority}. Must be between 1 and 5"
        except ValueError:
            return f"Invalid priority value: {row.get('priority')}"

        # Validate status
        valid_statuses = ['Active', 'Inactive', 'Testing']
        if row.get('status', 'Active') not in valid_statuses:
            return f"Invalid status: {row.get('status')}. Must be one of: {', '.join(valid_statuses)}"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by counterparty and priority"""

        def sort_key(record):
            cp = record.get('counterpartyId', 'ZZZ')
            priority = int(record.get('priority', '999'))
            return (cp, priority)

        sorted_records = sorted(records, key=sort_key)

        # Print summary
        cp_counts = {}
        source_counts = {}
        priority_counts = {}

        for record in sorted_records:
            cp = record.get('counterpartyId', 'Unknown')
            source = record.get('sourceType', 'Unknown')
            priority = record.get('priority', 'Unknown')

            cp_counts[cp] = cp_counts.get(cp, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        print(f"\nMatching Rules Summary:")
        print(f"  Total rules: {len(sorted_records)}")
        print(f"\n  By Counterparty:")
        for cp, count in sorted(cp_counts.items()):
            print(f"    {cp}: {count} rules")
        print(f"\n  By Source Type:")
        for source, count in sorted(source_counts.items()):
            print(f"    {source}: {count} rules")
        print(f"\n  By Priority:")
        for priority, count in sorted(priority_counts.items()):
            print(f"    Priority {priority}: {count} rules")

        return sorted_records


class TransactionTypeProcessor(DataProcessor):
    """Processor for F15 Transaction Types (transaction_type_map)"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        payload = {
            # Type identification
            "mappingId": row.get('mappingId', ''),
            "id": row.get('mappingId', ''),  # API might expect 'id' field
            "internalType": row.get('internalType', ''),
            "description": row.get('description', ''),

            # GL Posting patterns
            "glDebitPattern": row.get('glDebitPattern', ''),
            "glCreditPattern": row.get('glCreditPattern', ''),
            "feePattern": row.get('feePattern', ''),

            # Business rules
            "customerImpact": row.get('customerImpact', ''),
            "positionImpact": row.get('positionImpact', ''),
            "settlementDays": row.get('settlementDays', '0'),
            "fxConversion": row.get('fxConversion', 'TradeDate'),

            # Control fields
            "status": row.get('status', 'Active'),
            "effectiveDate": self.format_date(row.get('effectiveDate', current_date)),
            "expiryDate": self.format_date(row.get('expiryDate', '')) if row.get('expiryDate') else '',

            # System fields
            "dateCreated": self.format_date(row.get('dateCreated', current_date)),
            "dateModified": current_date,
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['feePattern', 'expiryDate']
        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return ""

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return ""

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        mapping_id = data.get('mappingId', 'N/A')
        internal_type = data.get('internalType', 'N/A')
        description = data.get('description', 'N/A')
        return f"{mapping_id}: {internal_type} - {description}"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate transaction type data"""
        # Check required fields
        required_fields = ['mappingId', 'internalType', 'description',
                           'glDebitPattern', 'glCreditPattern',
                           'customerImpact', 'positionImpact']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate customer impact
        valid_impacts = ['Debit', 'Credit', 'None']
        if row['customerImpact'] not in valid_impacts:
            return f"Invalid customer impact: {row['customerImpact']}. Must be one of: {', '.join(valid_impacts)}"

        # Validate position impact
        valid_position_impacts = ['Increase', 'Decrease', 'None']
        if row['positionImpact'] not in valid_position_impacts:
            return f"Invalid position impact: {row['positionImpact']}. Must be one of: {', '.join(valid_position_impacts)}"

        # Validate settlement days
        try:
            days = int(row.get('settlementDays', '0'))
            if days < 0 or days > 3:
                return f"Invalid settlement days: {days}. Must be between 0 and 3"
        except ValueError:
            return f"Invalid settlement days value: {row.get('settlementDays')}"

        # Validate FX conversion timing
        valid_fx_timings = ['TradeDate', 'SettlementDate', 'PaymentDate']
        if row.get('fxConversion', 'TradeDate') not in valid_fx_timings:
            return f"Invalid FX conversion timing: {row.get('fxConversion')}. Must be one of: {', '.join(valid_fx_timings)}"

        # Validate status
        valid_statuses = ['Active', 'Inactive']
        if row.get('status', 'Active') not in valid_statuses:
            return f"Invalid status: {row.get('status')}. Must be one of: {', '.join(valid_statuses)}"

        # Validate GL patterns contain required placeholders
        debit_pattern = row.get('glDebitPattern', '')
        credit_pattern = row.get('glCreditPattern', '')

        if '|' not in debit_pattern or '|' not in credit_pattern:
            return "GL patterns must include pipe separators for account|amount|currency format"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by internal type"""
        sorted_records = sorted(records, key=lambda x: x.get('internalType', 'ZZZ'))

        # Print summary
        impact_counts = {'Debit': 0, 'Credit': 0, 'None': 0}
        position_counts = {'Increase': 0, 'Decrease': 0, 'None': 0}
        settlement_counts = {}

        for record in sorted_records:
            customer_impact = record.get('customerImpact', 'None')
            position_impact = record.get('positionImpact', 'None')
            settlement = record.get('settlementDays', '0')

            impact_counts[customer_impact] = impact_counts.get(customer_impact, 0) + 1
            position_counts[position_impact] = position_counts.get(position_impact, 0) + 1
            settlement_counts[settlement] = settlement_counts.get(settlement, 0) + 1

        print(f"\nTransaction Types Summary:")
        print(f"  Total types: {len(sorted_records)}")
        print(f"\n  Customer Impact:")
        for impact, count in sorted(impact_counts.items()):
            print(f"    {impact}: {count} types")
        print(f"\n  Position Impact:")
        for impact, count in sorted(position_counts.items()):
            print(f"    {impact}: {count} types")
        print(f"\n  Settlement Days:")
        for days, count in sorted(settlement_counts.items()):
            print(f"    T+{days}: {count} types")

        return sorted_records


class BankProcessor(DataProcessor):
    """Processor for Bank Master data (F01.02)"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        payload = {
            # Bank identification
            "name": row.get('name', ''),
            "swift_code_bic": row.get('swift_code_bic', '').upper(),

            # Location
            "country": row.get('country', ''),
            "city": row.get('city', ''),
            "bank_address": row.get('bank_address', ''),

            # System fields
            "dateCreated": self.format_date(row.get('dateCreated', current_date)),
            "dateModified": current_date,
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedByName": "Admin Admin",

            # ID field - using SWIFT code as unique identifier
            "id": row.get('swift_code_bic', '').upper()
        }

        # Remove empty string values
        return {k: v for k, v in payload.items() if v != ''}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        name = data.get('name', 'N/A')
        swift = data.get('swift_code_bic', 'N/A')
        country = data.get('country', 'N/A')
        return f"{swift}: {name} ({country})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate bank data"""
        # Check required fields
        required_fields = ['name', 'swift_code_bic', 'country', 'bank_address']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate SWIFT/BIC code format
        swift = row.get('swift_code_bic', '').upper()
        if swift:
            # SWIFT codes are 8 or 11 characters
            if len(swift) not in [8, 11]:
                return f"Invalid SWIFT code length: {swift} (must be 8 or 11 characters)"
            # Check format: 4 letters (bank code) + 2 letters (country) + 2 alphanumeric (location)
            if len(swift) >= 8:
                if not swift[:4].isalpha():
                    return f"Invalid SWIFT code: first 4 characters must be letters"
                if not swift[4:6].isalpha():
                    return f"Invalid SWIFT code: characters 5-6 must be country code"

        # Validate country code (ISO 2-letter)
        country = row.get('country', '')
        if country and (len(country) != 2 or not country.isalpha()):
            return f"Invalid country code: {country} (must be 2 letters)"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by country and then by name"""
        sorted_records = sorted(records, key=lambda x: (x.get('country', ''), x.get('name', '')))

        # Print summary
        country_counts = {}
        for record in sorted_records:
            country = record.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1

        print(f"\nBank distribution by country:")
        for country, count in sorted(country_counts.items()):
            print(f"  {country}: {count} banks")

        return sorted_records


class CounterpartyProcessor(DataProcessor):
    """Processor for Counterparty Master data (F02.11)"""

    def prepare_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Convert CSV row to API payload format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Handle boolean for isActive
        is_active = 'true' if row.get('isActive', 'true').lower() == 'true' else 'false'

        payload = {
            # Counterparty identification
            "counterpartyId": row.get('counterpartyId', ''),
            "id": row.get('counterpartyId', ''),  # API might expect 'id' field
            "counterpartyType": row.get('counterpartyType', ''),
            "shortCode": row.get('shortCode', '').upper(),

            # Entity linking (only one should be populated based on type)
            "bankId": row.get('bankId', ''),
            "brokerId": row.get('brokerId', ''),
            "custodianId": row.get('custodianId', ''),

            # Status and dates
            "isActive": is_active,
            "relationshipStartDate": self.format_date(row.get('relationshipStartDate', current_date)),

            # Operational settings
            "settlementCycle": row.get('settlementCycle', 'T+2'),
            "reconciliationFrequency": row.get('reconciliationFrequency', 'Daily'),
            "ourAccountPrefix": row.get('ourAccountPrefix', ''),

            # Relationship management
            "relationshipManager": row.get('relationshipManager', ''),
            "operationsContact": row.get('operationsContact', ''),
            "notes": row.get('notes', ''),

            # System fields
            "dateCreated": self.format_date(row.get('dateCreated', current_date)),
            "dateModified": current_date,
            "createdBy": row.get('createdBy', 'admin'),
            "modifiedBy": "admin",
            "createdByName": "Admin Admin",
            "modifiedByName": "Admin Admin"
        }

        # Remove empty string values except for optional fields
        optional_fields = ['bankId', 'brokerId', 'custodianId', 'ourAccountPrefix',
                           'relationshipManager', 'operationsContact', 'notes']

        # Remove entity IDs that don't match the counterparty type
        cp_type = row.get('counterpartyType', '')
        if cp_type == 'Bank':
            payload.pop('brokerId', None)
            payload.pop('custodianId', None)
        elif cp_type == 'Broker':
            payload.pop('bankId', None)
            payload.pop('custodianId', None)
        elif cp_type == 'Custodian':
            payload.pop('bankId', None)
            payload.pop('brokerId', None)

        return {k: v for k, v in payload.items() if v != '' or k in optional_fields}

    def format_date(self, date_str: str) -> str:
        """Convert date from various formats to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If already in correct format, return as is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%Y/%m/%d"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return datetime.now().strftime("%Y-%m-%d")

    def get_identifier(self, data: Dict[str, str]) -> str:
        """Get human-readable identifier for logging"""
        cp_id = data.get('counterpartyId', 'N/A')
        short_code = data.get('shortCode', 'N/A')
        cp_type = data.get('counterpartyType', 'N/A')
        return f"{cp_id}: {short_code} ({cp_type})"

    def validate_record(self, row: Dict[str, str]) -> Optional[str]:
        """Validate counterparty data"""
        # Check required fields
        required_fields = ['counterpartyId', 'counterpartyType', 'shortCode']

        for field in required_fields:
            if not row.get(field):
                return f"Missing required field: {field}"

        # Validate counterparty type
        valid_types = ['Bank', 'Broker', 'Custodian']
        if row['counterpartyType'] not in valid_types:
            return f"Invalid counterparty type: {row['counterpartyType']}. Must be one of: {', '.join(valid_types)}"

        # Validate short code (3-6 uppercase alphanumeric)
        short_code = row.get('shortCode', '').upper()
        if short_code:
            if len(short_code) < 3 or len(short_code) > 6:
                return f"Invalid short code length: {short_code} (must be 3-6 characters)"
            if not short_code.isalnum():
                return f"Invalid short code: {short_code} (must be alphanumeric)"

        # Validate that appropriate entity ID is provided based on type
        cp_type = row.get('counterpartyType')
        if cp_type == 'Bank':
            if not row.get('bankId'):
                return "Bank counterparty requires bankId (SWIFT/BIC code)"
            if row.get('brokerId') or row.get('custodianId'):
                return "Bank counterparty should not have brokerId or custodianId"
        elif cp_type == 'Broker':
            if not row.get('brokerId'):
                return "Broker counterparty requires brokerId"
            if row.get('bankId') or row.get('custodianId'):
                return "Broker counterparty should not have bankId or custodianId"
        elif cp_type == 'Custodian':
            if not row.get('custodianId'):
                return "Custodian counterparty requires custodianId"
            if row.get('bankId') or row.get('brokerId'):
                return "Custodian counterparty should not have bankId or brokerId"

        # Validate settlement cycle
        valid_cycles = ['T+0', 'T+1', 'T+2', 'T+3']
        if row.get('settlementCycle') and row['settlementCycle'] not in valid_cycles:
            return f"Invalid settlement cycle: {row['settlementCycle']}. Must be one of: {', '.join(valid_cycles)}"

        # Validate reconciliation frequency
        valid_frequencies = ['Daily', 'Weekly', 'Monthly']
        if row.get('reconciliationFrequency') and row['reconciliationFrequency'] not in valid_frequencies:
            return f"Invalid reconciliation frequency: {row['reconciliationFrequency']}. Must be one of: {', '.join(valid_frequencies)}"

        # Validate boolean fields
        if row.get('isActive') and row['isActive'].lower() not in ['true', 'false']:
            return f"Invalid isActive value: {row['isActive']} (must be true/false)"

        return None

    def sort_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort records by type and then by short code"""

        def sort_key(record):
            # Sort order: Bank -> Broker -> Custodian
            type_order = {'Bank': 0, 'Broker': 1, 'Custodian': 2}
            cp_type = record.get('counterpartyType', 'Unknown')
            short_code = record.get('shortCode', 'ZZZ')
            return (type_order.get(cp_type, 3), short_code)

        sorted_records = sorted(records, key=sort_key)

        # Print summary
        type_counts = {}
        active_counts = {'true': 0, 'false': 0}
        settlement_counts = {}

        for record in sorted_records:
            cp_type = record.get('counterpartyType', 'Unknown')
            is_active = record.get('isActive', 'true')
            settlement = record.get('settlementCycle', 'T+2')

            type_counts[cp_type] = type_counts.get(cp_type, 0) + 1
            active_counts[is_active] = active_counts.get(is_active, 0) + 1
            settlement_counts[settlement] = settlement_counts.get(settlement, 0) + 1

        print(f"\nCounterparty Summary:")
        print(f"  Total counterparties: {len(sorted_records)}")
        print(f"\n  By Type:")
        for cp_type, count in sorted(type_counts.items()):
            print(f"    {cp_type}: {count}")
        print(f"\n  Active: {active_counts.get('true', 0)}, Inactive: {active_counts.get('false', 0)}")
        print(f"\n  Settlement Cycles:")
        for cycle, count in sorted(settlement_counts.items()):
            print(f"    {cycle}: {count}")

        return sorted_records


# Endpoint configurations
ENDPOINTS = {
    "gl_account": {
        "name": "GL Account Master",
        "url": f"{BASE_URL}/glAccountMaster",
        "csv_file": "data/gl_config/01-accounts.csv",
        "api_id": "API-f4fa99e7-1116-410f-ae16-26438fcd680a",
        "api_key": DEFAULT_API_KEY,
        "processor": GLAccountProcessor(),
        "id_field": "accountCode"
    },
    "gl_function": {
        "name": "GL Business Function",
        "url": f"{BASE_URL}/glBusinessFunction",
        "csv_file": "data/gl_config/01-acc-function.csv",
        "api_id": "API-fe629ac6-9e56-4a86-a7b6-67c5347bd8e1",
        "api_key": DEFAULT_API_KEY,
        "processor": GLFunctionProcessor(),
        "id_field": "functionCode"
    },
    "trx_mapping": {
        "name": "Transaction Type Mapping",
        "url": f"{BASE_URL}/transactionTypeMappingForm",
        "csv_file": "data/gl_config/F12-trx-mappings.csv",
        "api_id": "API-cc0d13ed-9bf3-46c3-8aa9-faade571afc6",
        "api_key": DEFAULT_API_KEY,
        "processor": TransactionMappingProcessor(),
        "id_field": "mappingId"
    },
    "cp_mapping": {
        "name": "Counterparty Transaction Mapping",
        "url": f"{BASE_URL}/counterpartyTxnMappingForm",
        "csv_file": "data/gl_config/F13-cp-mappings.csv",
        "api_id": "API-b67f41e7-5f6c-4e52-bd4d-a8472d6cbe09",
        "api_key": DEFAULT_API_KEY,
        "processor": CounterpartyMappingProcessor(),
        "id_field": "mappingId"
    },
    "secu_transaction": {
        "name": "Security Transaction",
        "url": f"{BASE_URL}/secuTotalTransaction",
        "csv_file": "data/gl_config/F03-rows-secu.csv",
        "api_id": "API-6212bc9d-9c63-4df3-9ec5-43f302c3df21",
        "api_key": DEFAULT_API_KEY,
        "processor": SecurityTransactionProcessor(),
        "id_field": "mappingId"
    },
    "bank_transaction": {
        "name": "Bank Transaction",
        "url": f"{BASE_URL}/bankTotalTransaction",
        "csv_file": "data/gl_config/F02-rows-bank.csv",
        "api_id": "API-b3c744ae-2915-4229-a7bb-7b7d72ee3d80",
        "api_key": DEFAULT_API_KEY,
        "processor": BankTransactionProcessor(),
        "id_field": "TID"
    },
    "asset": {
        "name": "Asset",
        "url": f"{BASE_URL}/assetMasterForm",
        "csv_file": "data/gl_config/F02.12-asset2.csv",
        "api_id": "API-4598f05c-abc0-4494-ac77-bc5c2526fd13",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": AssetProcessor(),
        "id_field": "assetId",
    },
    "fx_rates": {
        "name": "Fx Rates (EUR-based)",
        "url": f"{BASE_URL}/fxRatesManagementForm",
        "csv_file": "data/gl_config/fx-rates.csv",
        "api_id": "API-1703deea-2cf7-442b-b12d-e75b001b1744",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": FxRatesProcessor(),
        "id_field": "rateId",
    },
    "customer": {
        "name": "Customer Master",
        "url": f"{BASE_URL}/customerForm",
        "csv_file": "data/gl_config/F01.06-customer.csv",
        "api_id": "API-5b08df3d-aa8a-43be-a526-d461a8f404dd",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": CustomerProcessor(),
        "id_field": "customerId",
    },
    "customer_account": {
        "name": "Customer Account",
        "url": f"{BASE_URL}/customerAccount",
        "csv_file": "data/gl_config/F02.10-customer-account.csv",
        "api_id": "API-6edbe109-fefd-4911-a4f9-1b615ef13b42",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": CustomerAccountProcessor(),
        "id_field": "accountId",
    },
    "matching_rules": {
        "name": "F14 Matching Rules",
        "url": f"{BASE_URL}/cpTxnMappingForm",
        "csv_file": "data/gl_config/F02.14-matching-rules2.csv",
        "api_id": "API-2052b208-b2c9-4c58-bef1-5b4539516237",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": MatchingRulesProcessor(),
        "id_field": "mapping_id"
    },
    "transaction_types": {
        "name": "F15 Transaction Types",
        "url": f"{BASE_URL}/transactionTypeMapForm",
        "csv_file": "data/gl_config/F02.15-transaction-types.csv",
        "api_id": "API-0be04a98-2f1b-4d20-bb4c-118a6aa3ee42",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": TransactionTypeProcessor(),
        "id_field": "mappingId"
    },
    "bank": {
        "name": "Bank Master",
        "url": f"{BASE_URL}/bank",
        "csv_file": "data/gl_config/F01.02-bank.csv",
        "api_id": "API-659e8909-eb10-425b-95b7-b8b5e9fc97a4",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": BankProcessor(),
        "id_field": "swift_code_bic"
    },
    "counterparty": {
        "name": "Counterparty Master",
        "url": f"{BASE_URL}/counterpartyMaster",
        "csv_file": "data/gl_config/F02.11-counterparty.csv",
        "api_id": "API-9f147f54-286c-47ad-b2cf-bec8e9488022",
        "api_key": "8c04d5332aa34484a62fe1fb1e6e5900",
        "processor": CounterpartyProcessor(),
        "id_field": "counterpartyId"
    }
}


def get_headers(endpoint_key: str) -> Dict[str, str]:
    """Get headers for specific endpoint"""
    config = ENDPOINTS[endpoint_key]
    return {
        'accept': 'application/json',
        'api_id': config['api_id'],
        'api_key': config['api_key'],
        'Content-Type': 'application/json'
    }


def post_record(endpoint_key: str, data: Dict[str, str], retry_count: int = 3) -> bool:
    """Post record to Joget API with retry logic"""
    config = ENDPOINTS[endpoint_key]
    headers = get_headers(endpoint_key)
    processor = config['processor']
    identifier = processor.get_identifier(data)

    for attempt in range(retry_count):
        try:
            response = requests.post(
                config['url'],
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )

            if response.status_code in [200, 201]:
                print(f"✓ Successfully posted {identifier}")
                return True
            else:
                print(f"✗ Failed to post {identifier}: HTTP {response.status_code}")
                print(f"  Response: {response.text}")

                if attempt < retry_count - 1:
                    print(f"  Retrying... (attempt {attempt + 2}/{retry_count})")
                    time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"✗ Error posting {identifier}: {str(e)}")
            if attempt < retry_count - 1:
                print(f"  Retrying... (attempt {attempt + 2}/{retry_count})")
                time.sleep(2)

    return False


def process_csv_file(endpoint_key: str, dry_run: bool = False, validate_only: bool = False):
    """Process CSV file for the specified endpoint"""
    config = ENDPOINTS[endpoint_key]
    csv_file = config['csv_file']
    processor = config['processor']

    print(f"\n{config['name']} CSV to Joget API Importer")
    print("=" * 70)
    print(f"Endpoint: {config['url']}")
    print(f"CSV File: {csv_file}")
    if dry_run:
        print("Mode: DRY RUN (no data will be posted)")
    elif validate_only:
        print("Mode: VALIDATE ONLY (checking data integrity)")
    print("=" * 70)

    # Read CSV file
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            records = list(reader)
            print(f"\nFound {len(records)} records in CSV file")
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found")
        return
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

    # Validate records
    if hasattr(processor, 'validate_record'):
        print("\nValidating records...")
        validation_errors = []
        for i, record in enumerate(records):
            error = processor.validate_record(record)
            if error:
                validation_errors.append(f"Row {i + 2}: {error}")

        if validation_errors:
            print(f"\n❌ Found {len(validation_errors)} validation errors:")
            for error in validation_errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(validation_errors) > 10:
                print(f"  ... and {len(validation_errors) - 10} more errors")

            if validate_only or input("\nContinue anyway? (y/N): ").lower() != 'y':
                return

    if validate_only:
        print("\n✅ Validation complete!")
        return

    # Sort records if needed
    sorted_records = processor.sort_records(records)

    # Process records
    success_count = 0
    failed_records = []
    skipped_records = []

    print(f"\nProcessing {len(sorted_records)} records...")
    print("-" * 70)

    for i, record in enumerate(sorted_records):
        # Prepare data
        try:
            record_data = processor.prepare_data(record)
            identifier = record.get(config['id_field'], f"Record {i + 1}")
        except Exception as e:
            print(f"✗ Error preparing data for row {i + 2}: {str(e)}")
            skipped_records.append(identifier)
            continue

        if dry_run:
            print(f"[DRY RUN] Would post: {processor.get_identifier(record_data)}")
            if i < 3:  # Show full data for first 3 records
                print(f"  Data: {json.dumps(record_data, indent=2)}")
            success_count += 1
        else:
            if post_record(endpoint_key, record_data):
                success_count += 1
            else:
                failed_records.append(identifier)

            # Small delay between requests
            time.sleep(0.5)

    # Summary
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Total records: {len(records)}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {len(failed_records)}")
    print(f"Skipped: {len(skipped_records)}")

    if failed_records and not dry_run:
        print(f"\nFailed identifiers: {', '.join(failed_records[:10])}")
        if len(failed_records) > 10:
            print(f"... and {len(failed_records) - 10} more")
        print("\nYou may want to retry these records manually or check the API logs.")

        # Save failed records to a file
        failed_file = f"failed_{endpoint_key}_records.json"
        failed_data = []
        for record in records:
            identifier = record.get(config['id_field'], '')
            if identifier in failed_records:
                try:
                    failed_data.append(processor.prepare_data(record))
                except:
                    pass

        if failed_data:
            with open(failed_file, 'w') as f:
                json.dump(failed_data, f, indent=2)
            print(f"\nFailed records saved to '{failed_file}' for manual review.")


def add_endpoint(args):
    """Interactive endpoint configuration"""
    print("\nAdd New Endpoint Configuration")
    print("=" * 50)

    # Collect endpoint information
    endpoint_key = input("Endpoint key (e.g., 'customer_master'): ").strip()
    name = input("Endpoint name (e.g., 'Customer Master'): ").strip()
    form_name = input("Joget form name (e.g., 'customerMasterForm'): ").strip()
    csv_file = input("Default CSV file path: ").strip()
    api_id = input(f"API ID (press Enter for default): ").strip() or ENDPOINTS['gl_account']['api_id']
    api_key = input(f"API Key (press Enter for default): ").strip() or DEFAULT_API_KEY
    id_field = input("Primary identifier field in CSV (e.g., 'customerId'): ").strip()

    # Generate configuration
    config = {
        "name": name,
        "url": f"{BASE_URL}/{form_name}",
        "csv_file": csv_file,
        "api_id": api_id,
        "api_key": api_key,
        "processor": "GenericProcessor()",  # Placeholder
        "id_field": id_field
    }

    print("\nGenerated configuration:")
    print(f'"{endpoint_key}": {{')
    for key, value in config.items():
        if key != "processor":
            print(f'    "{key}": "{value}",')
        else:
            print(f'    "{key}": {value},')
    print("}")

    print("\nTo use this endpoint, you'll need to:")
    print("1. Add this configuration to the ENDPOINTS dictionary")
    print("2. Create a processor class if custom logic is needed")
    print("3. Run: python submit_config.py --endpoint", endpoint_key)


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Import CSV data to Joget API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s --endpoint gl_account               # Import GL accounts
  python %(prog)s --endpoint trx_mapping              # Import transaction mappings
  python %(prog)s --endpoint gl_function --dry-run    # Test without posting
  python %(prog)s --endpoint trx_mapping --validate   # Validate data only
  python %(prog)s --list                              # List available endpoints
  python %(prog)s --add-endpoint                      # Configure new endpoint
        """
    )

    parser.add_argument(
        '--endpoint', '-e',
        choices=list(ENDPOINTS.keys()),
        help='Endpoint to import data to'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Test run without posting data'
    )

    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validate data without importing'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available endpoints'
    )

    parser.add_argument(
        '--csv-file', '-f',
        help='Override default CSV file path'
    )

    parser.add_argument(
        '--add-endpoint',
        action='store_true',
        help='Interactive endpoint configuration helper'
    )

    args = parser.parse_args()

    # Handle special actions
    if args.add_endpoint:
        add_endpoint(args)
        return

    if args.list:
        print("\nAvailable endpoints:")
        print("-" * 70)
        for key, config in ENDPOINTS.items():
            print(f"  {key:15} - {config['name']}")
            print(f"  {'':15}   CSV: {config['csv_file']}")
            print(f"  {'':15}   URL: {config['url']}")
            print()
        return

    # Validate endpoint selection
    if not args.endpoint:
        parser.print_help()
        print("\nError: Please specify an endpoint using --endpoint")
        print("Use --list to see available endpoints")
        sys.exit(1)

    # Override CSV file if specified
    if args.csv_file:
        if not os.path.exists(args.csv_file):
            print(f"Error: CSV file '{args.csv_file}' not found")
            sys.exit(1)
        ENDPOINTS[args.endpoint]['csv_file'] = args.csv_file

    # Process the selected endpoint
    process_csv_file(args.endpoint, args.dry_run, args.validate)


if __name__ == "__main__":
    main()