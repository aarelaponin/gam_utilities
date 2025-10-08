#!/usr/bin/env python3
"""
Main Registry Validator
Orchestrates the validation process between parsers, validators, and database
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .database import DatabaseConnector
from .models import (
    ValidationReport, FarmerValidationResult, ValidationStatus
)
from ..parsers.services_parser import ServicesParser
from ..parsers.test_data_parser import TestDataParser
from ..validators.form_validator import FormValidator
from ..validators.grid_validator import GridValidator


class RegistryValidator:
    """
    Main orchestrator for validation process
    Coordinates between parsers, validators, and reporters
    """

    def __init__(self, services_config: str, test_data: str, db_config: Dict[str, Any],
                 validation_config: Dict[str, Any]):
        """
        Initialize registry validator

        Args:
            services_config: Path to services.yml file
            test_data: Path to test-data.json file
            db_config: Database configuration
            validation_config: Validation settings
        """
        self.logger = logging.getLogger('joget_validator.registry_validator')
        self.validation_config = validation_config

        # Initialize components
        try:
            self.services = ServicesParser(services_config)
            self.test_data = TestDataParser(test_data)
            self.db = DatabaseConnector(db_config)
            self.form_validator = FormValidator(validation_config)
            self.grid_validator = GridValidator(validation_config)

            self.logger.info("Registry validator initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize registry validator: {e}")
            raise

    def validate_all(self) -> ValidationReport:
        """
        Validate all farmers in test data

        Returns:
            Complete validation report
        """
        start_time = datetime.now()
        start_timestamp = time.time()

        self.logger.info("Starting complete validation process")

        # Get all farmers from test data
        farmers = self.test_data.get_farmers()
        if not farmers:
            self.logger.warning("No farmers found in test data")
            return self._create_empty_report(start_time, time.time() - start_timestamp)

        # Initialize counters
        passed = 0
        failed = 0
        skipped = 0
        farmer_results = []

        # Validate each farmer
        for idx, farmer_data in enumerate(farmers):
            self.logger.info(f"Validating farmer {idx + 1}/{len(farmers)}")

            try:
                result = self.validate_farmer(farmer_data)
                farmer_results.append(result)

                # Update counters
                if result.status == ValidationStatus.PASSED:
                    passed += 1
                elif result.status == ValidationStatus.FAILED:
                    failed += 1
                else:
                    skipped += 1

            except Exception as e:
                self.logger.error(f"Error validating farmer {idx + 1}: {e}")
                skipped += 1

        # Create final report
        duration = time.time() - start_timestamp
        report = ValidationReport(
            total_farmers=len(farmers),
            passed=passed,
            failed=failed,
            skipped=skipped,
            validation_time=start_time,
            duration_seconds=duration,
            farmer_results=farmer_results
        )

        self.logger.info(f"Validation completed in {duration:.2f} seconds")
        self.logger.info(f"Results: {passed} passed, {failed} failed, {skipped} skipped")

        return report

    def validate_farmer(self, farmer_data: Dict[str, Any]) -> FarmerValidationResult:
        """
        Validate single farmer across all forms and grids

        Args:
            farmer_data: Farmer data from test file

        Returns:
            Farmer validation result
        """
        start_time = datetime.now()
        start_timestamp = time.time()

        # Extract farmer identifier
        farmer_id = self.test_data.get_farmer_identifier(farmer_data)
        if not farmer_id:
            self.logger.error("No farmer identifier found in farmer data")
            return FarmerValidationResult(
                farmer_id="unknown",
                national_id=None,
                status=ValidationStatus.ERROR,
                validation_time=start_time,
                duration_seconds=time.time() - start_timestamp
            )

        national_id = self.test_data.get_national_id(farmer_data)

        self.logger.debug(f"Validating farmer {farmer_id}")

        # Initialize result
        result = FarmerValidationResult(
            farmer_id=farmer_id,
            national_id=national_id,
            status=ValidationStatus.PASSED,
            validation_time=start_time
        )

        overall_status = ValidationStatus.PASSED

        # Validate forms
        forms_to_validate = self.validation_config.get('validation', {}).get('forms_to_validate', [])
        if not forms_to_validate:
            forms_to_validate = self.services.get_forms()

        for form_name in forms_to_validate:
            try:
                form_result = self.validate_form(farmer_id, farmer_data, form_name)
                result.form_results[form_name] = form_result

                if form_result.status == ValidationStatus.FAILED:
                    overall_status = ValidationStatus.FAILED
                elif form_result.status == ValidationStatus.ERROR and overall_status == ValidationStatus.PASSED:
                    overall_status = ValidationStatus.ERROR

            except Exception as e:
                self.logger.error(f"Error validating form {form_name} for farmer {farmer_id}: {e}")
                overall_status = ValidationStatus.ERROR

        # Validate grids
        grids_to_validate = self.validation_config.get('validation', {}).get('grids_to_validate', [])
        if not grids_to_validate:
            grids_to_validate = self.services.get_grids()

        for grid_name in grids_to_validate:
            try:
                grid_result = self.validate_grid(farmer_id, farmer_data, grid_name)
                result.grid_results[grid_name] = grid_result

                if grid_result.status == ValidationStatus.FAILED:
                    overall_status = ValidationStatus.FAILED
                elif grid_result.status == ValidationStatus.ERROR and overall_status == ValidationStatus.PASSED:
                    overall_status = ValidationStatus.ERROR

            except Exception as e:
                self.logger.error(f"Error validating grid {grid_name} for farmer {farmer_id}: {e}")
                overall_status = ValidationStatus.ERROR

        result.status = overall_status
        result.duration_seconds = time.time() - start_timestamp

        return result

    def validate_form(self, farmer_id: str, farmer_data: Dict[str, Any], form_name: str):
        """
        Validate a specific form for a farmer

        Args:
            farmer_id: Farmer identifier
            farmer_data: Test data for the farmer
            form_name: Name of the form to validate

        Returns:
            Form validation result
        """
        # Get form configuration
        form_config = self.services.get_form_mappings(form_name)
        if not form_config:
            self.logger.warning(f"No configuration found for form {form_name}")
            return None

        # Query database for form data
        table_name = form_config['table_name']
        db_data = self.db.query_form(table_name, farmer_id)

        # Validate using form validator
        return self.form_validator.validate(
            test_data=farmer_data,
            db_data=db_data,
            mappings=form_config,
            form_name=form_name
        )

    def validate_grid(self, farmer_id: str, farmer_data: Dict[str, Any], grid_name: str):
        """
        Validate a specific grid for a farmer

        Args:
            farmer_id: Farmer identifier
            farmer_data: Test data for the farmer
            grid_name: Name of the grid to validate

        Returns:
            Grid validation result
        """
        # Get grid configuration
        grid_config = self.services.get_grid_config(grid_name)
        if not grid_config:
            self.logger.warning(f"No configuration found for grid {grid_name}")
            return None

        # Query database for grid data
        table_name = grid_config['table_name']
        parent_field = grid_config['parent_field']
        db_data = self.db.query_grid(table_name, parent_field, farmer_id)

        # Validate using grid validator
        return self.grid_validator.validate(
            test_data=farmer_data,
            db_data=db_data,
            mappings=grid_config,
            grid_name=grid_name
        )

    def validate_specific_farmer(self, farmer_id: str) -> Optional[FarmerValidationResult]:
        """
        Validate a specific farmer by ID

        Args:
            farmer_id: Farmer identifier to validate

        Returns:
            Farmer validation result or None if not found
        """
        farmer_data = self.test_data.get_farmer_by_id(farmer_id)
        if not farmer_data:
            self.logger.error(f"Farmer {farmer_id} not found in test data")
            return None

        return self.validate_farmer(farmer_data)

    def validate_specific_form(self, form_name: str) -> ValidationReport:
        """
        Validate a specific form across all farmers

        Args:
            form_name: Name of the form to validate

        Returns:
            Validation report for the specific form
        """
        start_time = datetime.now()
        start_timestamp = time.time()

        self.logger.info(f"Validating form {form_name} across all farmers")

        farmers = self.test_data.get_farmers()
        if not farmers:
            return self._create_empty_report(start_time, time.time() - start_timestamp)

        # Initialize counters
        passed = 0
        failed = 0
        skipped = 0
        farmer_results = []

        # Validate each farmer for this specific form
        for farmer_data in farmers:
            farmer_id = self.test_data.get_farmer_identifier(farmer_data)
            if not farmer_id:
                skipped += 1
                continue

            try:
                # Create a limited farmer result with only this form
                farmer_result = FarmerValidationResult(
                    farmer_id=farmer_id,
                    national_id=self.test_data.get_national_id(farmer_data),
                    status=ValidationStatus.PASSED,
                    validation_time=datetime.now()
                )

                form_result = self.validate_form(farmer_id, farmer_data, form_name)
                if form_result:
                    farmer_result.form_results[form_name] = form_result
                    farmer_result.status = form_result.status

                    if form_result.status == ValidationStatus.PASSED:
                        passed += 1
                    elif form_result.status == ValidationStatus.FAILED:
                        failed += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1

                farmer_results.append(farmer_result)

            except Exception as e:
                self.logger.error(f"Error validating form {form_name} for farmer {farmer_id}: {e}")
                skipped += 1

        # Create report
        duration = time.time() - start_timestamp
        return ValidationReport(
            total_farmers=len(farmers),
            passed=passed,
            failed=failed,
            skipped=skipped,
            validation_time=start_time,
            duration_seconds=duration,
            farmer_results=farmer_results
        )

    def _create_empty_report(self, start_time: datetime, duration: float) -> ValidationReport:
        """Create an empty validation report"""
        return ValidationReport(
            total_farmers=0,
            passed=0,
            failed=0,
            skipped=0,
            validation_time=start_time,
            duration_seconds=duration,
            farmer_results=[]
        )

    def test_connections(self) -> Dict[str, bool]:
        """
        Test all connections and configurations

        Returns:
            Dictionary with test results
        """
        results = {}

        # Test database connection
        try:
            results['database'] = self.db.test_connection()
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            results['database'] = False

        # Test services configuration
        try:
            forms = self.services.get_forms()
            grids = self.services.get_grids()
            results['services_config'] = len(forms) > 0 or len(grids) > 0
        except Exception as e:
            self.logger.error(f"Services configuration test failed: {e}")
            results['services_config'] = False

        # Test test data
        try:
            farmers = self.test_data.get_farmers()
            results['test_data'] = len(farmers) > 0
        except Exception as e:
            self.logger.error(f"Test data validation failed: {e}")
            results['test_data'] = False

        return results