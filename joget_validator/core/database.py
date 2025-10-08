#!/usr/bin/env python3
"""
MySQL Database Connector for Joget Validation
Manages connections and queries to the Joget MySQL database
"""

import logging
import mysql.connector
from mysql.connector import Error, pooling
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager


class DatabaseConnector:
    """
    MySQL database connector for Joget validation queries
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database connector

        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('joget_validator.database')
        self.connection_pool = None
        self._create_connection_pool()

    def _create_connection_pool(self):
        """Create MySQL connection pool"""
        try:
            pool_config = {
                'pool_name': 'joget_validation_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['user'],
                'password': self.config['password'],
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': True
            }

            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            self.logger.info("Database connection pool created successfully")

        except Error as e:
            self.logger.error(f"Error creating connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections

        Yields:
            MySQL connection object
        """
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def test_connection(self) -> bool:
        """
        Test database connectivity

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result[0] == 1
        except Error as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def query_form(self, table_name: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Query single form record by farmer ID

        Args:
            table_name: Name of the form table (e.g., 'app_fd_farmer_basic')
            farmer_id: Farmer identifier

        Returns:
            Dictionary containing form data or None if not found
        """
        # Use id column to match farmer records
        query = f"SELECT * FROM {table_name} WHERE id = %s"

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (farmer_id,))
                result = cursor.fetchone()
                cursor.close()

                if result:
                    self.logger.debug(f"Found form record in {table_name} for farmer {farmer_id}")
                else:
                    self.logger.warning(f"No form record found in {table_name} for farmer {farmer_id}")

                return result

        except Error as e:
            self.logger.error(f"Error querying form {table_name}: {e}")
            return None

    def query_grid(self, table_name: str, parent_field: str, parent_id: str) -> List[Dict[str, Any]]:
        """
        Query grid/sub-form records

        Args:
            table_name: Name of the grid table (e.g., 'app_fd_household_members')
            parent_field: Parent linking field (e.g., 'c_farmer_id')
            parent_id: Parent record identifier

        Returns:
            List of dictionaries containing grid data
        """
        query = f"SELECT * FROM {table_name} WHERE {parent_field} = %s ORDER BY id"

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (parent_id,))
                results = cursor.fetchall()
                cursor.close()

                self.logger.debug(f"Found {len(results)} grid records in {table_name} for {parent_field}={parent_id}")
                return results

        except Error as e:
            self.logger.error(f"Error querying grid {table_name}: {e}")
            return []

    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get list of columns for a table

        Args:
            table_name: Name of the table

        Returns:
            List of column names
        """
        query = """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.config['database'], table_name))
                results = cursor.fetchall()
                cursor.close()

                columns = [row[0] for row in results]
                self.logger.debug(f"Table {table_name} has columns: {columns}")
                return columns

        except Error as e:
            self.logger.error(f"Error getting columns for {table_name}: {e}")
            return []

    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists in database

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.config['database'], table_name))
                result = cursor.fetchone()
                cursor.close()

                exists = result[0] > 0
                self.logger.debug(f"Table {table_name} exists: {exists}")
                return exists

        except Error as e:
            self.logger.error(f"Error checking table existence {table_name}: {e}")
            return False

    def get_farmer_ids(self, table_name: str = 'app_fd_farmer_basic') -> List[str]:
        """
        Get list of all farmer IDs from the database

        Args:
            table_name: Table containing farmer records

        Returns:
            List of farmer IDs
        """
        query = f"SELECT DISTINCT c_farmer_id FROM {table_name} WHERE c_farmer_id IS NOT NULL"

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()

                farmer_ids = [row[0] for row in results]
                self.logger.info(f"Found {len(farmer_ids)} farmers in database")
                return farmer_ids

        except Error as e:
            self.logger.error(f"Error getting farmer IDs: {e}")
            return []

    def execute_custom_query(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """
        Execute custom SQL query

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of result dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results = cursor.fetchall()
                cursor.close()

                self.logger.debug(f"Custom query returned {len(results)} rows")
                return results

        except Error as e:
            self.logger.error(f"Error executing custom query: {e}")
            return []

    def close_pool(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            # MySQL connector doesn't provide a direct way to close pools
            # Connections will be closed automatically when they go out of scope
            self.logger.info("Database connection pool closed")