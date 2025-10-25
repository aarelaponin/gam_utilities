#!/usr/bin/env python3
"""
Form Discovery
Discovers forms and API endpoints in a running Joget instance.

SINGLE RESPONSIBILITY: Query Joget instance for existing forms
Does NOT: Create forms, compare, or deploy

Uses both database queries and API calls to discover:
- Existing forms in application
- Form definitions
- API endpoints
- Form table names
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from joget_client import JogetClient


@dataclass
class FormInfo:
    """Information about a form in Joget"""
    form_id: str
    form_name: str
    table_name: str
    app_id: str
    app_version: str
    api_endpoint: Optional[str] = None
    api_id: Optional[str] = None
    form_definition: Optional[Dict[str, Any]] = None


class FormDiscovery:
    """
    Discover forms in running Joget instance.

    Uses combination of:
    - Database queries (app_form, app_builder tables)
    - Joget API calls
    """

    def __init__(self,
                 client: JogetClient,
                 db_config: Dict[str, Any],
                 logger: Optional[logging.Logger] = None):
        """
        Initialize form discovery.

        Args:
            client: JogetClient instance
            db_config: Database configuration for direct queries
            logger: Logger instance
        """
        self.client = client
        self.db_config = db_config
        self.logger = logger or logging.getLogger('joget_utility.form_discovery')

    def discover_all_forms(self, app_id: str, app_version: str) -> List[FormInfo]:
        """
        Discover all forms in application.

        Args:
            app_id: Application ID
            app_version: Application version

        Returns:
            List of FormInfo objects
        """
        import mysql.connector
        from mysql.connector import Error as MySQLError

        self.logger.info(f"Discovering forms in app: {app_id} v{app_version}")

        forms = []
        connection = None
        cursor = None

        try:
            # Connect to database
            connection = mysql.connector.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 3306),
                database=self.db_config.get('database', 'jwdb'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password')
            )

            if not connection.is_connected():
                raise Exception("Failed to connect to Joget database")

            cursor = connection.cursor(dictionary=True, buffered=True)

            # Query app_form table
            query = """
                SELECT id, name, tableName
                FROM app_form
                WHERE appId = %s AND appVersion = %s
                ORDER BY name
            """

            cursor.execute(query, (app_id, app_version))
            results = cursor.fetchall()

            self.logger.info(f"Found {len(results)} forms in database")

            for row in results:
                form_info = FormInfo(
                    form_id=row['id'],
                    form_name=row['name'],
                    table_name=row['tableName'],
                    app_id=app_id,
                    app_version=app_version
                )

                # Try to find associated API endpoint
                api_info = self._find_api_endpoint(cursor, app_id, app_version, row['id'])
                if api_info:
                    form_info.api_endpoint = api_info['name']
                    form_info.api_id = api_info['id']

                forms.append(form_info)

        except MySQLError as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error discovering forms: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

        return forms

    def _find_api_endpoint(self,
                          cursor,
                          app_id: str,
                          app_version: str,
                          form_id: str) -> Optional[Dict[str, str]]:
        """
        Find API endpoint associated with form.

        Args:
            cursor: Database cursor
            app_id: Application ID
            app_version: Application version
            form_id: Form ID

        Returns:
            Dictionary with 'name' and 'id' keys, or None
        """
        try:
            # Common API naming patterns
            api_name_patterns = [
                f"api_{form_id}",
                form_id,
                f"{form_id}API"
            ]

            for api_name in api_name_patterns:
                query = """
                    SELECT id, name
                    FROM app_builder
                    WHERE appId = %s
                      AND appVersion = %s
                      AND type = 'api'
                      AND name = %s
                """

                cursor.execute(query, (app_id, app_version, api_name))
                result = cursor.fetchone()

                if result:
                    return {
                        'id': result['id'],
                        'name': result['name']
                    }

            return None

        except Exception as e:
            self.logger.debug(f"Error finding API endpoint for {form_id}: {e}")
            return None

    def get_form_definition(self, app_id: str, app_version: str, form_id: str) -> Optional[Dict[str, Any]]:
        """
        Get form JSON definition from Joget.

        Note: This may require additional API access or database queries
        depending on Joget version and configuration.

        Args:
            app_id: Application ID
            app_version: Application version
            form_id: Form ID

        Returns:
            Form definition as dictionary, or None if not found
        """
        import mysql.connector
        from mysql.connector import Error as MySQLError

        connection = None
        cursor = None

        try:
            # Connect to database
            connection = mysql.connector.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 3306),
                database=self.db_config.get('database', 'jwdb'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password')
            )

            if not connection.is_connected():
                raise Exception("Failed to connect to Joget database")

            cursor = connection.cursor(buffered=True)

            # Query app_form table for JSON definition
            query = """
                SELECT json
                FROM app_form
                WHERE appId = %s AND appVersion = %s AND id = %s
            """

            cursor.execute(query, (app_id, app_version, form_id))
            result = cursor.fetchone()

            if result and result[0]:
                # Parse JSON
                form_json = json.loads(result[0])
                return form_json

            return None

        except MySQLError as e:
            self.logger.error(f"Database error getting form definition: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing form JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting form definition: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def check_form_exists(self, app_id: str, app_version: str, form_id: str) -> bool:
        """
        Check if form exists in Joget instance.

        Args:
            app_id: Application ID
            app_version: Application version
            form_id: Form ID to check

        Returns:
            True if form exists, False otherwise
        """
        import mysql.connector

        connection = None
        cursor = None

        try:
            connection = mysql.connector.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 3306),
                database=self.db_config.get('database', 'jwdb'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password')
            )

            if not connection.is_connected():
                return False

            cursor = connection.cursor(buffered=True)

            query = """
                SELECT COUNT(*) as count
                FROM app_form
                WHERE appId = %s AND appVersion = %s AND id = %s
            """

            cursor.execute(query, (app_id, app_version, form_id))
            result = cursor.fetchone()

            return result[0] > 0 if result else False

        except Exception as e:
            self.logger.debug(f"Error checking form existence: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def check_table_exists(self, table_name: str) -> bool:
        """
        Check if database table exists for form.

        Args:
            table_name: Database table name (e.g., app_fd_maritalStatus)

        Returns:
            True if table exists, False otherwise
        """
        import mysql.connector

        connection = None
        cursor = None

        try:
            connection = mysql.connector.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 3306),
                database=self.db_config.get('database', 'jwdb'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password')
            )

            if not connection.is_connected():
                return False

            cursor = connection.cursor(buffered=True)

            # Query information_schema
            query = """
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
            """

            cursor.execute(query, (self.db_config.get('database', 'jwdb'), table_name))
            result = cursor.fetchone()

            return result[0] > 0 if result else False

        except Exception as e:
            self.logger.debug(f"Error checking table existence: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
