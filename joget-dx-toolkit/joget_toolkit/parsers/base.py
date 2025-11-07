"""
Base parser interface for all format parsers.

All parsers should inherit from BaseParser and implement the parse() method.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from joget_toolkit.specs.schema import AppSpec


class BaseParser(ABC):
    """Abstract base class for all parsers"""

    @abstractmethod
    def parse(self, input_path: Union[str, Path], **kwargs) -> AppSpec:
        """
        Parse input file and return canonical AppSpec.

        Args:
            input_path: Path to input file
            **kwargs: Parser-specific options

        Returns:
            AppSpec object in canonical format

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If parsing fails
        """
        pass

    def _read_file(self, path: Union[str, Path]) -> str:
        """Helper to read file contents"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _validate_result(self, spec: AppSpec) -> AppSpec:
        """Validate parsed result"""
        # AppSpec validation happens in Pydantic model
        # This method can add additional validation if needed
        return spec
