#!/usr/bin/env python3
"""
Clean up all existing metadata deployments
Deletes:
1. All app_fd_md* database tables
2. All app_form entries for md* forms
3. All app_builder API entries for md* forms
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

# Load environment
env_file = Path('config/../.env.3')
if env_file.exists():
    load_dotenv(env_file, override=True)

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3308)),
    'database': os.getenv('DB_NAME', 'jwdb'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

print("=" * 80)
print("METADATA CLEANUP")
print("=" * 80)
print()

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 1. Find all app_fd_md* tables
    print("Finding metadata tables...")
    cursor.execute("""
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'jwdb'
        AND TABLE_NAME LIKE 'app_fd_md%'
        ORDER BY TABLE_NAME
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(tables)} metadata tables")

    # 2. Drop all tables
    if tables:
        print("\nDropping tables:")
        for table in tables:
            print(f"  Dropping {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        conn.commit()
        print(f"✓ Dropped {len(tables)} tables")
    else:
        print("No tables to drop")

    # 3. Delete form definitions
    print("\nDeleting form definitions...")
    cursor.execute("""
        DELETE FROM app_form
        WHERE formId LIKE 'md%'
    """)
    form_count = cursor.rowcount
    conn.commit()
    print(f"✓ Deleted {form_count} form definitions")

    # 4. Delete API definitions
    print("\nDeleting API definitions...")
    cursor.execute("""
        DELETE FROM app_builder
        WHERE id LIKE 'api_md%'
    """)
    api_count = cursor.rowcount
    conn.commit()
    print(f"✓ Deleted {api_count} API definitions")

    cursor.close()
    conn.close()

    print()
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Tables dropped:      {len(tables)}")
    print(f"Forms deleted:       {form_count}")
    print(f"APIs deleted:        {api_count}")
    print()
    print("Database is now clean - ready for fresh deployment")
    print("=" * 80)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
