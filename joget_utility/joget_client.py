#!/usr/bin/env python3
"""
Joget DX8 API Client
Core client for interacting with Joget form APIs
"""

import json
import time
import logging
from typing import Dict, Optional, List, Any
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
import mysql.connector
from mysql.connector import Error as MySQLError


class JogetClient:
    """Client for interacting with Joget DX8 Form API"""

    def __init__(self, base_url: str, api_key: str = None, debug: bool = False):
        """
        Initialize Joget client

        Args:
            base_url: Base URL for Joget API (e.g., http://localhost:8080/jw/api/form)
            api_key: Default API key (can be overridden per request)
            debug: Enable debug logging of all posted fields
        """
        self.base_url = base_url.rstrip('/')
        self.default_api_key = api_key
        self.debug = debug
        self.session = requests.Session()
        self.timeout = 30
        self.retry_count = 3
        self.retry_delay = 2
        self.logger = logging.getLogger('joget_utility.client')

    def _get_headers(self, api_id: str, api_key: str = None) -> Dict[str, str]:
        """
        Prepare headers for API request

        Args:
            api_id: API ID for the specific endpoint
            api_key: API key (uses default if not provided)

        Returns:
            Dictionary of headers
        """
        key = api_key or self.default_api_key
        if not key:
            raise ValueError("API key is required but not provided")

        return {
            'accept': 'application/json',
            'api_id': api_id,
            'api_key': key,
            'Content-Type': 'application/json'
        }

    def post(self, endpoint: str, api_id: str, data: Dict[str, Any],
             api_key: str = None, retry: bool = True) -> Dict[str, Any]:
        """
        Send POST request to Joget endpoint

        Args:
            endpoint: Form endpoint name (e.g., 'maritalStatus') or full URL path
            api_id: API ID for the endpoint
            data: Data to send
            api_key: Optional API key (uses default if not provided)
            retry: Whether to retry on failure

        Returns:
            Response data as dictionary

        Raises:
            JogetAPIError: On API errors
        """
        # Check if endpoint is a full path (contains /)
        if '/' in endpoint:
            # Use full path - replace everything after /jw/api
            # Handle base_url with or without trailing /api or /form
            if '/jw/api' in self.base_url:
                # Extract just the server part (up to and including /jw/api)
                parts = self.base_url.split('/jw/api')
                base = parts[0] + '/jw/api/'
                url = base + endpoint
            else:
                # Fallback: just append to base_url
                url = f"{self.base_url.rstrip('/')}/{endpoint}"
        else:
            # Use standard form endpoint
            url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(api_id, api_key)

        # Debug logging of posted fields
        if self.debug:
            self.logger.debug(f"POST Request to: {url}")
            self.logger.debug(f"API ID: {api_id}")
            self.logger.debug(f"Headers: {headers}")
            self.logger.debug(f"Posted fields:")
            for key, value in data.items():
                # Truncate very long values for readability
                display_value = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                self.logger.debug(f"  - {key}: {display_value}")
            self.logger.debug(f"Full payload:\n{json.dumps(data, indent=2)}")

        attempts = self.retry_count if retry else 1
        last_error = None

        for attempt in range(attempts):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    data=json.dumps(data),
                    timeout=self.timeout
                )

                if response.status_code in [200, 201]:
                    if self.debug:
                        self.logger.debug(f"Response status: {response.status_code}")
                        try:
                            response_data = response.json()
                            self.logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                        except:
                            self.logger.debug(f"Response text: {response.text}")
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"status": "success", "response": response.text}

                error_msg = f"HTTP {response.status_code}: {response.text}"

                if response.status_code == 401:
                    raise JogetAPIError(f"Authentication failed: {error_msg}")
                elif response.status_code == 404:
                    raise JogetAPIError(f"Endpoint not found: {endpoint}")
                elif response.status_code >= 500:
                    last_error = JogetAPIError(f"Server error: {error_msg}")
                else:
                    raise JogetAPIError(f"Request failed: {error_msg}")

            except (Timeout, ConnectionError) as e:
                last_error = JogetAPIError(f"Connection error: {str(e)}")
            except RequestException as e:
                last_error = JogetAPIError(f"Request error: {str(e)}")

            if attempt < attempts - 1 and last_error:
                time.sleep(self.retry_delay)

        if last_error:
            raise last_error

        raise JogetAPIError("Unknown error occurred")

    def batch_post(self, endpoint: str, api_id: str, records: List[Dict[str, Any]],
                   api_key: str = None, stop_on_error: bool = False) -> Dict[str, Any]:
        """
        Post multiple records to the same endpoint

        Args:
            endpoint: Form endpoint name
            api_id: API ID for the endpoint
            records: List of records to post
            api_key: Optional API key
            stop_on_error: Whether to stop on first error

        Returns:
            Dictionary with results summary
        """
        results = {
            "total": len(records),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        if self.debug:
            self.logger.debug(f"Batch POST: {len(records)} records to endpoint '{endpoint}'")

        for idx, record in enumerate(records):
            if self.debug:
                self.logger.debug(f"Processing record {idx + 1}/{len(records)}")
            try:
                self.post(endpoint, api_id, record, api_key, retry=True)
                results["successful"] += 1
            except JogetAPIError as e:
                results["failed"] += 1
                results["errors"].append({
                    "index": idx,
                    "record": record,
                    "error": str(e)
                })

                if stop_on_error:
                    break

        return results

    def post_multipart(self, endpoint: str, api_id: str, data: Dict[str, Any],
                      files: Dict[str, Any], api_key: str = None, retry: bool = True) -> Dict[str, Any]:
        """
        Send multipart POST request to Joget endpoint (for file uploads)

        Args:
            endpoint: Form endpoint name or full URL path
            api_id: API ID for the endpoint
            data: Form data fields
            files: Files to upload (dict with field_name: (filename, file_obj, content_type))
            api_key: Optional API key
            retry: Whether to retry on failure

        Returns:
            Response data as dictionary

        Raises:
            JogetAPIError: On API errors
        """
        # Check if endpoint is a full path (contains /)
        if '/' in endpoint:
            if '/jw/api' in self.base_url:
                parts = self.base_url.split('/jw/api')
                base = parts[0] + '/jw/api/'
                url = base + endpoint
            else:
                url = f"{self.base_url.rstrip('/')}/{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"

        # Prepare headers (without Content-Type - requests will set it for multipart)
        key = api_key or self.default_api_key
        if not key:
            raise ValueError("API key is required but not provided")

        headers = {
            'accept': 'application/json',
            'api_id': api_id,
            'api_key': key,
            'Referer': f'{self.base_url.split("/jw/api")[0]}/jw/web/userview/masterData/v/_/formCreator_crud?_mode=add'
            # Do NOT set Content-Type - requests will set it automatically with boundary
        }

        # Debug logging
        if self.debug:
            self.logger.debug(f"Multipart POST Request to: {url}")
            self.logger.debug(f"API ID: {api_id}")
            self.logger.debug(f"Form data fields: {list(data.keys())}")
            self.logger.debug(f"Files: {list(files.keys())}")

        attempts = self.retry_count if retry else 1
        last_error = None

        for attempt in range(attempts):
            try:
                # Reset file pointers if retrying
                for field_name, file_tuple in files.items():
                    if hasattr(file_tuple[1], 'seek'):
                        file_tuple[1].seek(0)

                response = self.session.post(
                    url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=self.timeout
                )

                if response.status_code in [200, 201]:
                    if self.debug:
                        self.logger.debug(f"Response status: {response.status_code}")
                        try:
                            response_data = response.json()
                            self.logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                        except:
                            self.logger.debug(f"Response text: {response.text}")
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"status": "success", "response": response.text}

                error_msg = f"HTTP {response.status_code}: {response.text}"

                if response.status_code == 401:
                    raise JogetAPIError(f"Authentication failed: {error_msg}")
                elif response.status_code == 404:
                    raise JogetAPIError(f"Endpoint not found: {endpoint}")
                elif response.status_code >= 500:
                    last_error = JogetAPIError(f"Server error: {error_msg}")
                else:
                    raise JogetAPIError(f"Request failed: {error_msg}")

            except (Timeout, ConnectionError) as e:
                last_error = JogetAPIError(f"Connection error: {str(e)}")
            except RequestException as e:
                last_error = JogetAPIError(f"Request error: {str(e)}")

            if attempt < attempts - 1 and last_error:
                time.sleep(self.retry_delay)

        if last_error:
            raise last_error

        raise JogetAPIError("Unknown error occurred")

    def create_form(self, payload: Dict[str, Any], api_id: str,
                   api_key: str = None) -> Dict[str, Any]:
        """
        Create a new form using the formCreator API

        Args:
            payload: Form creation payload dictionary containing:
                - target_app_id: Target application ID
                - target_app_version: Target application version
                - form_id: Form identifier
                - form_name: Form display name
                - table_name: Database table name
                - form_definition_json: Form definition as JSON string
                - create_api_endpoint: Whether to create API endpoint ("yes"/"no")
                - api_name: Name for the API endpoint
            api_id: API ID for the formCreator endpoint
            api_key: Optional API key (uses default if not provided)

        Returns:
            Response data as dictionary

        Raises:
            JogetAPIError: On API errors
        """
        import io

        # Use the formCreator endpoint with addWithFiles path for multipart uploads
        endpoint = 'form/formCreator/addWithFiles'

        if self.debug:
            self.logger.debug(f"Creating form: {payload.get('form_id')}")
            self.logger.debug(f"Target app: {payload.get('target_app_id')}")

        # Extract form_definition_json - it needs to be uploaded as a file
        form_def_json = payload.pop('form_definition_json', '{}')

        # Prepare multipart form data
        # The formCreator expects form_definition_json as a FILE upload
        files = {
            'form_definition_json': ('form.json', io.BytesIO(form_def_json.encode('utf-8')), 'application/json')
        }

        # Other fields as regular form data
        data = payload

        # Make multipart POST request
        return self.post_multipart(endpoint, api_id, data, files, api_key, retry=True)

    def get_api_id_for_form(self, app_id: str, app_version: str, api_name: str,
                            db_config: Dict[str, Any]) -> Optional[str]:
        """
        Query Joget database for API ID by form API name

        Uses Joget's app_builder table to find the API ID for a specific form endpoint.
        This follows the Joget pattern where each form gets its own API with unique ID.

        Args:
            app_id: Application ID (e.g., 'subsidyApplication')
            app_version: Application version (e.g., '1')
            api_name: API endpoint name (e.g., 'api_crops')
            db_config: Database configuration dictionary with keys:
                - host: MySQL host
                - port: MySQL port
                - database: Database name
                - user: Database user
                - password: Database password

        Returns:
            API ID string (e.g., 'API-b81e5d88-b747-476a-92d3-0aac6bb1f0f3') or None if not found

        Raises:
            JogetAPIError: On database connection or query errors
        """
        connection = None
        cursor = None

        try:
            # Connect to MySQL database
            connection = mysql.connector.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                database=db_config.get('database', 'jwdb'),
                user=db_config.get('user'),
                password=db_config.get('password')
            )

            if not connection.is_connected():
                raise JogetAPIError("Failed to connect to Joget database")

            cursor = connection.cursor(buffered=True)

            # Query app_builder table for API ID
            query = """
                SELECT id FROM app_builder
                WHERE appId = %s
                  AND appVersion = %s
                  AND type = 'api'
                  AND name = %s
            """

            cursor.execute(query, (app_id, app_version, api_name))
            result = cursor.fetchone()

            if result:
                api_id = result[0]
                if self.debug:
                    self.logger.debug(f"Found API ID for {api_name}: {api_id}")
                return api_id
            else:
                self.logger.warning(f"No API ID found for: app={app_id}, version={app_version}, name={api_name}")
                return None

        except MySQLError as e:
            error_msg = f"Database error while querying API ID: {str(e)}"
            self.logger.error(error_msg)
            raise JogetAPIError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error querying API ID: {str(e)}"
            self.logger.error(error_msg)
            raise JogetAPIError(error_msg)
        finally:
            # Clean up database resources
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def test_connection(self) -> bool:
        """
        Test connection to Joget server

        Returns:
            True if connection successful
        """
        try:
            # Extract the base server URL from the API path
            server_url = self.base_url.split('/jw/')[0] + '/jw' if '/jw/' in self.base_url else self.base_url
            response = self.session.get(
                server_url,
                timeout=5
            )
            return response.status_code < 500
        except:
            return False


class JogetAPIError(Exception):
    """Custom exception for Joget API errors"""
    pass