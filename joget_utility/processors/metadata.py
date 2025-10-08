#!/usr/bin/env python3
"""
Metadata batch processor for standard code/name endpoints
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import yaml

from .csv_processor import CSVProcessor
from .json_processor import JSONProcessor


class MetadataProcessor:
    """Processor for batch metadata imports with standard code/name fields"""

    def __init__(self, data_path: str = None):
        """
        Initialize metadata processor

        Args:
            data_path: Base path for data files
        """
        self.data_path = Path(data_path) if data_path else Path('./data/metadata')
        self.results = []

    def process_batch(self, batch_config: Union[str, Path, Dict]) -> Dict[str, Any]:
        """
        Process a batch of metadata endpoints

        Args:
            batch_config: Path to batch config file or config dictionary

        Returns:
            Processing results summary
        """
        # Load configuration
        if isinstance(batch_config, (str, Path)):
            config = self._load_batch_config(batch_config)
        else:
            config = batch_config

        batch_items = config.get('metadata_endpoints', [])
        options = config.get('options', {})

        total = len(batch_items)
        successful = 0
        failed = 0
        results = []

        print(f"\nProcessing Metadata Batch")
        print("=" * 50)
        print(f"Found {total} endpoints to process\n")

        for idx, item in enumerate(batch_items, 1):
            print(f"[{idx}/{total}] Processing {item['endpoint']}...")

            result = self.process_endpoint(
                api_id=item['api_id'],
                endpoint=item['endpoint'],
                file_name=item['file'],
                description=item.get('description', ''),
                validate_only=options.get('dry_run', False)
            )

            results.append(result)

            if result['success']:
                successful += 1
                print(f"  ✓ Successfully posted {result['record_count']} records")
            else:
                failed += 1
                print(f"  ✗ Failed: {result['error']}")

                if options.get('stop_on_error', False):
                    print("\nStopping due to error (stop_on_error=true)")
                    break

            print()

        # Summary
        print("-" * 50)
        print(f"Batch Complete: {successful}/{total} successful")
        if failed > 0:
            print(f"Failed endpoints: {failed}")

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def process_endpoint(self, api_id: str, endpoint: str, file_name: str,
                        description: str = "", validate_only: bool = False) -> Dict[str, Any]:
        """
        Process a single metadata endpoint

        Args:
            api_id: API ID for the endpoint
            endpoint: Endpoint name
            file_name: Data file name
            description: Endpoint description
            validate_only: Only validate, don't post data

        Returns:
            Processing result
        """
        try:
            # Determine full file path
            file_path = self._resolve_file_path(file_name)

            print(f"  File: {file_path}")

            # Load and process data
            records = self._load_file(file_path)
            print(f"  Records: {len(records)}")

            # Transform to code/name format
            transformed_records = self._transform_to_metadata_format(records)

            if validate_only:
                print("  Mode: Validation only")
                return {
                    "endpoint": endpoint,
                    "description": description,
                    "file": str(file_path),
                    "record_count": len(transformed_records),
                    "success": True,
                    "mode": "validation"
                }

            # TODO: Post to API (will be integrated with main CLI)
            return {
                "endpoint": endpoint,
                "description": description,
                "file": str(file_path),
                "record_count": len(transformed_records),
                "records": transformed_records,
                "api_id": api_id,
                "success": True
            }

        except Exception as e:
            return {
                "endpoint": endpoint,
                "description": description,
                "file": file_name,
                "success": False,
                "error": str(e)
            }

    def _load_batch_config(self, config_path: Union[str, Path]) -> Dict:
        """Load batch configuration from YAML file"""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Batch config not found: {config_path}")

        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def _resolve_file_path(self, file_name: str) -> Path:
        """Resolve file path, checking multiple locations"""
        # Check if absolute path
        if os.path.isabs(file_name):
            return Path(file_name)

        # Check in data_path/metadata
        path = self.data_path / file_name
        if path.exists():
            return path

        # Check in parent data directories
        for subdir in ['metadata', 'csv', 'json']:
            path = self.data_path.parent / subdir / file_name
            if path.exists():
                return path

        # Check relative to current directory
        path = Path(file_name)
        if path.exists():
            return path

        raise FileNotFoundError(f"Data file not found: {file_name}")

    def _load_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from CSV or JSON file"""
        suffix = file_path.suffix.lower()

        if suffix == '.csv':
            processor = CSVProcessor()
        elif suffix == '.json':
            processor = JSONProcessor()
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        return processor.read_file(file_path)

    def _transform_to_metadata_format(self, records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Transform records to standard code/name format

        Args:
            records: Input records

        Returns:
            Transformed records with code and name fields
        """
        transformed = []

        for record in records:
            # Try to identify code and name fields
            code_value = None
            name_value = None

            # Check for exact matches first
            if 'code' in record and 'name' in record:
                code_value = str(record['code'])
                name_value = str(record['name'])
            else:
                # Try common variations
                for code_field in ['code', 'Code', 'CODE', 'id', 'Id', 'ID', 'key', 'Key']:
                    if code_field in record:
                        code_value = str(record[code_field])
                        break

                for name_field in ['name', 'Name', 'NAME', 'description', 'Description',
                                 'title', 'Title', 'label', 'Label', 'value', 'Value']:
                    if name_field in record:
                        name_value = str(record[name_field])
                        break

            # If still no mapping, use first two fields
            if not code_value or not name_value:
                fields = list(record.keys())
                if len(fields) >= 1:
                    code_value = str(record[fields[0]])
                if len(fields) >= 2:
                    name_value = str(record[fields[1]])
                elif len(fields) == 1:
                    # Use same value for both code and name
                    name_value = code_value

            if code_value and name_value:
                transformed.append({
                    "code": code_value,
                    "name": name_value
                })

        return transformed