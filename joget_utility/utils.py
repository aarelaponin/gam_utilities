#!/usr/bin/env python3
"""
Utility functions for Joget utility
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load main configuration file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if not config_path:
        # Try default locations
        default_paths = [
            Path('./config/joget.yaml'),
            Path('./joget.yaml'),
            Path(os.path.dirname(__file__)) / 'config' / 'joget.yaml'
        ]

        for path in default_paths:
            if path.exists():
                config_path = path
                break

    if not config_path or not Path(config_path).exists():
        raise FileNotFoundError("Configuration file not found. Please create config/joget.yaml")

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Set defaults if not specified
    defaults = {
        'connection': {
            'timeout': 30,
            'retry_count': 3,
            'retry_delay': 2
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'data_paths': {
            'default': './data',
            'metadata': './data/metadata',
            'csv': './data/csv',
            'json': './data/json'
        }
    }

    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                if subkey not in config[key]:
                    config[key][subkey] = subvalue

    return config


def setup_logging(config: Dict[str, Any] = None) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        config: Logging configuration dictionary

    Returns:
        Configured logger
    """
    if not config:
        config = {'level': 'INFO'}

    level = getattr(logging, config.get('level', 'INFO').upper())
    format_str = config.get('format', '%(asctime)s - %(levelname)s - %(message)s')

    # Create logger
    logger = logging.getLogger('joget_utility')
    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_str)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if 'file' in config:
        log_file = Path(config['file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)

    return logger


def resolve_data_path(file_name: str, config: Dict[str, Any],
                     data_type: str = 'default') -> Path:
    """
    Resolve data file path based on configuration

    Args:
        file_name: File name or path
        config: Configuration dictionary
        data_type: Type of data (default, metadata, csv, json)

    Returns:
        Resolved file path
    """
    # If absolute path, return as-is
    if os.path.isabs(file_name):
        return Path(file_name)

    # Get data paths from config
    data_paths = config.get('data_paths', {})
    base_path = Path(data_paths.get(data_type, './data'))

    # Try different locations
    possible_paths = [
        Path(file_name),  # Current directory
        base_path / file_name,  # Configured data path
    ]

    # Also check in all configured data paths
    for path_type, path_value in data_paths.items():
        possible_paths.append(Path(path_value) / file_name)

    # Return first existing path
    for path in possible_paths:
        if path.exists():
            return path

    # If not found, return path in configured location
    return base_path / file_name


def print_summary(results: Dict[str, Any], verbose: bool = False):
    """
    Print processing summary

    Args:
        results: Results dictionary
        verbose: Whether to print detailed information
    """
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    total = results.get('total', 0)
    successful = results.get('successful', 0)
    failed = results.get('failed', 0)

    print(f"Total records: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if successful > 0:
        success_rate = (successful / total) * 100
        print(f"Success rate: {success_rate:.1f}%")

    if verbose and 'errors' in results and results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")

    print("=" * 60)


def confirm_action(message: str) -> bool:
    """
    Ask for user confirmation

    Args:
        message: Confirmation message

    Returns:
        True if user confirms, False otherwise
    """
    response = input(f"\n{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


def format_record_for_display(record: Dict[str, Any], max_width: int = 80) -> str:
    """
    Format a record for display

    Args:
        record: Record to format
        max_width: Maximum width for values

    Returns:
        Formatted string
    """
    lines = []
    for key, value in record.items():
        value_str = str(value)
        if len(value_str) > max_width:
            value_str = value_str[:max_width-3] + "..."
        lines.append(f"  {key}: {value_str}")
    return "\n".join(lines)


def match_forms_to_data(forms_dir: str, data_dir: str,
                       form_pattern: str = "md*.json") -> List[tuple]:
    """
    Match form definition files with their corresponding data files

    Args:
        forms_dir: Directory containing form definition files
        data_dir: Directory containing data files
        form_pattern: Glob pattern for form files (default: "md*.json")

    Returns:
        List of tuples (form_file_path, data_file_path)
        data_file_path may be None if no matching data file found
    """
    import glob

    forms_path = Path(forms_dir)
    data_path = Path(data_dir)

    if not forms_path.exists():
        raise FileNotFoundError(f"Forms directory not found: {forms_dir}")

    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Get all form files
    pattern_path = forms_path / form_pattern
    form_files = sorted(glob.glob(str(pattern_path)))

    matches = []

    for form_file in form_files:
        form_path = Path(form_file)
        base_name = form_path.stem  # e.g., "md01maritalStatus"

        # Look for corresponding data file
        # Try CSV first, then JSON
        data_file = None
        for ext in ['.csv', '.json', '.CSV', '.JSON']:
            candidate = data_path / f"{base_name}{ext}"
            if candidate.exists():
                data_file = candidate
                break

        matches.append((form_path, data_file))

    return matches