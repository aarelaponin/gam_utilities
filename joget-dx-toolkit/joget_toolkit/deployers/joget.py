"""
Joget DX deployer for form deployment.

Deploys forms to Joget DX server via FormCreator API.
"""

import io
import json
import time
import requests
import logging
from pathlib import Path
from typing import Union, Dict, Any, List, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError

from joget_toolkit.deployers.base import BaseDeployer, DeploymentError


class JogetDeployer(BaseDeployer):
    """Deployer for Joget DX platform"""

    def __init__(self, base_url: str, api_key: str, api_id: str = None,
                 logger: logging.Logger = None):
        """
        Initialize Joget deployer.

        Args:
            base_url: Joget server base URL (e.g., http://localhost:8080)
            api_key: API key for authentication
            api_id: Default API ID (can be overridden per request)
            logger: Logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.default_api_id = api_id
        self.logger = logger or logging.getLogger('joget_toolkit.deployers.joget')
        self.session = requests.Session()
        self.timeout = 60  # Form creation can take longer
        self.retry_count = 3
        self.retry_delay = 2

    def deploy_form(self, form_json: Union[Dict[str, Any], str, Path], **kwargs) -> Dict[str, Any]:
        """
        Deploy a single form to Joget server.

        Args:
            form_json: Form JSON dict, JSON string, or path to JSON file
            **kwargs: Options
                app_id: Target application ID (required)
                form_id: Override form ID from JSON
                create_api: Create API endpoint (default: True)
                create_crud: Create CRUD interface (default: True)
                api_id: FormCreator API ID (required if not set in constructor)

        Returns:
            Deployment result dict

        Raises:
            DeploymentError: If deployment fails
        """
        # Load form JSON
        if isinstance(form_json, (str, Path)):
            path = Path(form_json)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    form_data = json.load(f)
            else:
                # Assume it's JSON string
                form_data = json.loads(form_json)
        else:
            form_data = form_json

        # Get required parameters
        app_id = kwargs.get('app_id')
        if not app_id:
            raise DeploymentError("app_id is required for deployment")

        api_id = kwargs.get('api_id', self.default_api_id)
        if not api_id:
            raise DeploymentError("api_id is required (FormCreator API)")

        # Extract form details
        form_id = kwargs.get('form_id') or form_data.get('properties', {}).get('id')
        if not form_id:
            raise DeploymentError("Cannot determine form_id from JSON")

        # Extract form details from JSON
        form_name = form_data.get('properties', {}).get('name', form_id)
        table_name = form_data.get('properties', {}).get('tableName', form_id)

        # Generate API name (if creating API endpoint)
        api_name = f"api_{form_id}"

        # Build deployment payload - must match FormCreator plugin Constants.FieldNames
        payload = {
            'target_app_id': app_id,
            'target_app_version': kwargs.get('app_version', '1'),
            'form_id': form_id,
            'form_name': form_name,
            'table_name': table_name,
            'create_api_endpoint': 'yes' if kwargs.get('create_api', True) else 'no',
            'api_name': api_name,
            'create_crud': 'yes' if kwargs.get('create_crud', True) else 'no'
        }

        # Store form definition separately - will be uploaded as file
        form_definition_json = json.dumps(form_data)

        # Deploy via FormCreator API
        try:
            result = self._call_form_creator_api(api_id, payload, form_definition_json, form_id)
            self.logger.info(f"✓ Deployed form: {form_id}")
            return result

        except Exception as e:
            raise DeploymentError(f"Failed to deploy form '{form_id}': {e}") from e

    def deploy_forms(self, form_files: List[Union[str, Path]], **kwargs) -> Dict[str, Any]:
        """
        Deploy multiple forms to Joget server.

        Args:
            form_files: List of form JSON file paths
            **kwargs: Options (see deploy_form for details)

        Returns:
            Deployment results dict
        """
        results = {
            'total': len(form_files),
            'successful': [],
            'failed': [],
            'errors': []
        }

        for form_file in form_files:
            try:
                self.deploy_form(form_file, **kwargs)
                results['successful'].append(str(form_file))
            except DeploymentError as e:
                results['failed'].append(str(form_file))
                results['errors'].append({
                    'file': str(form_file),
                    'error': str(e)
                })
                self.logger.error(f"✗ Failed: {form_file} - {e}")

                # Stop on error if specified
                if kwargs.get('stop_on_error', False):
                    break

        return results

    def _call_form_creator_api(self, api_id: str, data: Dict[str, Any],
                               form_definition_json: str, form_id: str) -> Dict[str, Any]:
        """
        Call FormCreator API to create form.

        Args:
            api_id: FormCreator API ID
            data: Payload data (form metadata fields)
            form_definition_json: Form definition JSON string (to upload as file)
            form_id: Form ID (for logging)

        Returns:
            API response dict

        Raises:
            DeploymentError: If API call fails
        """
        # FormCreator API endpoint - STATIC path, not based on API ID
        # API ID goes in headers, not URL
        url = f"{self.base_url}/jw/api/form/formCreator/addWithFiles"

        # Extract app_id from payload for Referer header
        app_id = data.get('target_app_id', 'app')

        # Referer header is REQUIRED - FormCreator plugin uses it to extract formDefId
        # Pattern: /jw/web/userview/{appId}/v/_/formCreator_crud?_mode=add
        base_server = self.base_url.split('/jw')[0] if '/jw' in self.base_url else self.base_url
        referer = f'{base_server}/jw/web/userview/{app_id}/v/_/formCreator_crud?_mode=add'

        headers = {
            'accept': 'application/json',
            'api_id': api_id,
            'api_key': self.api_key,
            'Referer': referer,
            # Note: Don't set Content-Type for multipart, requests will set it
        }

        # Prepare multipart data
        # FormCreator expects form_definition_json as a file upload (BytesIO object)
        files = {
            'form_definition_json': (
                f'{form_id}.json',
                io.BytesIO(form_definition_json.encode('utf-8')),
                'application/json'
            )
        }

        # Other fields as regular form data (already in correct format from payload)
        payload = data

        # Make request with retries
        attempts = self.retry_count
        last_error = None

        for attempt in range(attempts):
            try:
                # Reset file pointers if retrying
                for field_name, file_tuple in files.items():
                    if hasattr(file_tuple[1], 'seek'):
                        file_tuple[1].seek(0)

                self.logger.debug(f"Deploying form '{form_id}' (attempt {attempt + 1}/{attempts})")
                self.logger.debug(f"URL: {url}")
                self.logger.debug(f"Headers: {headers}")
                self.logger.debug(f"Payload fields: {list(payload.keys())}")
                self.logger.debug(f"Files: {list(files.keys())}")

                response = self.session.post(
                    url,
                    headers=headers,
                    data=payload,
                    files=files,
                    timeout=self.timeout
                )

                if response.status_code in [200, 201]:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"status": "success", "response": response.text}

                error_msg = f"HTTP {response.status_code}: {response.text}"

                if response.status_code == 401:
                    raise DeploymentError(f"Authentication failed: {error_msg}")
                elif response.status_code == 404:
                    raise DeploymentError(f"FormCreator API not found: {api_id}")
                elif response.status_code >= 500:
                    last_error = DeploymentError(f"Server error: {error_msg}")
                else:
                    raise DeploymentError(f"Request failed: {error_msg}")

            except (Timeout, ConnectionError) as e:
                last_error = DeploymentError(f"Connection error: {str(e)}")
            except RequestException as e:
                last_error = DeploymentError(f"Request error: {str(e)}")

            if attempt < attempts - 1 and last_error:
                self.logger.warning(f"Retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        if last_error:
            raise last_error

        raise DeploymentError("Unknown error occurred")

    def populate_data(self, form_id: str, data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Populate data into a deployed form.

        Args:
            form_id: Target form ID
            data: List of records to insert
            **kwargs: Options
                api_id: Form data API ID
                stop_on_error: Stop on first error (default: False)

        Returns:
            Population results dict
        """
        # This is a placeholder for data population functionality
        # Can be implemented later when needed
        raise NotImplementedError("Data population not yet implemented")
