#!/usr/bin/env python3
"""
Shared configuration management for Joget tools
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def load_env_file(env_path: str = None) -> Dict[str, str]:
    """
    Load environment variables from .env file

    Args:
        env_path: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}

    # Try multiple locations for .env file
    if env_path:
        env_files = [Path(env_path)]
    else:
        env_files = [
            Path('.env'),
            Path(__file__).parent.parent / '.env',  # Project root
            Path.home() / '.env'  # User home
        ]

    for env_file in env_files:
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            break  # Use first found .env file

    return env_vars


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration file with fallback to default locations

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
            Path(os.path.dirname(__file__)) / '../joget_utility/config/joget.yaml'
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


def load_validation_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load validation-specific configuration

    Args:
        config_path: Path to validation configuration file

    Returns:
        Validation configuration dictionary
    """
    if not config_path:
        config_path = Path('./joget_validator/config/validation.yaml')

    if not Path(config_path).exists():
        raise FileNotFoundError(f"Validation configuration file not found: {config_path}")

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Load environment variables from .env file
    env_vars = load_env_file()

    # Ensure database section exists
    if config is None:
        config = {}
    if 'database' not in config or config['database'] is None:
        config['database'] = {}

    # Apply environment variable overrides (priority: env var > .env file > yaml config)
    if os.environ.get('DB_PASSWORD') or env_vars.get('DB_PASSWORD'):
        config['database']['password'] = os.environ.get('DB_PASSWORD') or env_vars.get('DB_PASSWORD')

    if os.environ.get('DB_HOST') or env_vars.get('DB_HOST'):
        config['database']['host'] = os.environ.get('DB_HOST') or env_vars.get('DB_HOST')

    if os.environ.get('DB_PORT') or env_vars.get('DB_PORT'):
        port_value = os.environ.get('DB_PORT') or env_vars.get('DB_PORT')
        config['database']['port'] = int(port_value) if port_value else 3306

    if os.environ.get('DB_NAME') or env_vars.get('DB_NAME'):
        config['database']['database'] = os.environ.get('DB_NAME') or env_vars.get('DB_NAME')

    if os.environ.get('DB_USER') or env_vars.get('DB_USER'):
        config['database']['user'] = os.environ.get('DB_USER') or env_vars.get('DB_USER')

    # Set validation-specific defaults
    defaults = {
        'database': {
            'host': 'localhost',
            'port': 3306,
            'database': 'jogetdb',
            'user': 'joget',
            'password': 'joget'
        },
        'data_sources': {
            'services_yml': '../shared_data/services.yml',
            'test_data': '../shared_data/test-data.json',
            'metadata_dir': '../shared_data/metadata'
        },
        'validation': {
            'forms_to_validate': [],
            'grids_to_validate': [],
            'ignore_fields': ['dateCreated', 'dateModified', 'createdBy', 'modifiedBy'],
            'case_sensitive': False,
            'trim_strings': True,
            'null_equals_empty': True
        },
        'reporting': {
            'formats': ['console', 'json', 'html'],
            'output_directory': './validation_reports',
            'include_passed_fields': False,
            'max_errors_per_form': 10
        },
        'logging': {
            'level': 'INFO',
            'file': './logs/validation.log'
        }
    }

    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                if subkey not in config[key]:
                    config[key][subkey] = subvalue

    # Resolve relative paths in data_sources
    config_dir = Path(config_path).parent
    if 'data_sources' in config:
        for key, value in config['data_sources'].items():
            if isinstance(value, str) and not Path(value).is_absolute():
                # Resolve relative path from config file location
                resolved_path = (config_dir / value).resolve()
                config['data_sources'][key] = str(resolved_path)

    return config


def setup_logging(config: Dict[str, Any] = None, tool_name: str = 'joget_tool') -> logging.Logger:
    """
    Setup logging configuration

    Args:
        config: Logging configuration dictionary
        tool_name: Name of the tool for logger naming

    Returns:
        Configured logger
    """
    if not config:
        config = {'level': 'INFO'}

    level = getattr(logging, config.get('level', 'INFO').upper())
    format_str = config.get('format', '%(asctime)s - %(levelname)s - %(message)s')

    # Create logger
    logger = logging.getLogger(tool_name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

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


def resolve_path(file_name: str, config: Dict[str, Any],
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