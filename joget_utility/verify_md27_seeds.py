#!/usr/bin/env python3
"""
Verify SEEDS records in md27input table
"""
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_file = Path('.env.3')
load_dotenv(env_file, override=True)

db_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3308)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

print("=" * 80)
print("MD27INPUT DATA VERIFICATION")
print("=" * 80)
print()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Count by category
print("Records by category:")
cursor.execute("""
    SELECT c_input_category, COUNT(*) as count
    FROM app_fd_md27input
    GROUP BY c_input_category
    ORDER BY c_input_category
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

print()

# Show sample SEEDS records
print("Sample SEEDS records:")
cursor.execute("""
    SELECT c_code, c_name, c_category
    FROM app_fd_md27input
    WHERE c_input_category = 'SEEDS'
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} ({row[2]})")

print()
print("Total SEEDS records:", end=" ")
cursor.execute("SELECT COUNT(*) FROM app_fd_md27input WHERE c_input_category = 'SEEDS'")
print(cursor.fetchone()[0])

cursor.close()
conn.close()

print()
print("=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
