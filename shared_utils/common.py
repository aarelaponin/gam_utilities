#!/usr/bin/env python3
"""
Common utilities shared between Joget tools
"""

from typing import Dict, Any


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

    if successful > 0 and total > 0:
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


def format_validation_summary(results: Dict[str, Any]) -> str:
    """
    Format validation summary for display

    Args:
        results: Validation results dictionary

    Returns:
        Formatted summary string
    """
    lines = []
    lines.append("=" * 40)
    lines.append("Farmers Registry Validation Report")
    lines.append("=" * 40)

    if 'validation_time' in results:
        lines.append(f"Validation Time: {results['validation_time']}")

    if 'duration_seconds' in results:
        lines.append(f"Duration: {results['duration_seconds']:.2f} seconds")

    lines.append("")
    lines.append("Summary:")
    lines.append("--------")

    summary = results.get('summary', {})
    total = summary.get('total_farmers', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    skipped = summary.get('skipped', 0)

    lines.append(f"Total Farmers: {total}")
    lines.append(f"✓ Passed: {passed}")
    lines.append(f"✗ Failed: {failed}")
    lines.append(f"⊘ Skipped: {skipped}")

    return "\n".join(lines)