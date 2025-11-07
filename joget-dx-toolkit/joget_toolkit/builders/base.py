"""
Base builder interface for all platform builders.

All builders should inherit from BaseBuilder and implement the build() method.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Dict, Any

from joget_toolkit.specs.schema import AppSpec, FormSpec


class BaseBuilder(ABC):
    """Abstract base class for all builders"""

    @abstractmethod
    def build(self, app_spec: AppSpec, output_dir: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Build platform-specific files from canonical AppSpec.

        Args:
            app_spec: Canonical app specification
            output_dir: Directory to write output files
            **kwargs: Builder-specific options

        Returns:
            Dictionary with build results (e.g., files created)

        Raises:
            ValueError: If build fails
        """
        pass

    @abstractmethod
    def build_form(self, form_spec: FormSpec, **kwargs) -> Dict[str, Any]:
        """
        Build platform-specific form from FormSpec.

        Args:
            form_spec: Canonical form specification
            **kwargs: Builder-specific options

        Returns:
            Platform-specific form definition (e.g., JSON dict)
        """
        pass

    def _ensure_output_dir(self, output_dir: Union[str, Path]) -> Path:
        """Ensure output directory exists"""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
