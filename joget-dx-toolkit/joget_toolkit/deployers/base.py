"""
Base deployer interface for all platform deployers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Dict, Any


class BaseDeployer(ABC):
    """Abstract base class for all deployers"""

    @abstractmethod
    def deploy_form(self, form_json: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Deploy a single form to the platform.

        Args:
            form_json: Platform-specific form JSON
            **kwargs: Deployer-specific options

        Returns:
            Deployment result dictionary

        Raises:
            DeploymentError: If deployment fails
        """
        pass

    @abstractmethod
    def deploy_forms(self, form_files: list, **kwargs) -> Dict[str, Any]:
        """
        Deploy multiple forms to the platform.

        Args:
            form_files: List of form JSON file paths
            **kwargs: Deployer-specific options

        Returns:
            Deployment results dictionary

        Raises:
            DeploymentError: If deployment fails
        """
        pass


class DeploymentError(Exception):
    """Exception raised when deployment fails"""
    pass
