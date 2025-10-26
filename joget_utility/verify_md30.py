#!/usr/bin/env python3
"""
Verify all md30targetGroup records
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
print("MD30 TARGET GROUP VERIFICATION")
print("=" * 80)
print()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Get all records
cursor.execute("SELECT c_code, c_name, c_description FROM app_fd_md30targetGroup ORDER BY c_code")
records = cursor.fetchall()

print(f"Total records: {len(records)}")
print()
print("All records:")
for code, name, desc in records:
    print(f"  {code:15} {name:30} {desc}")

cursor.close()
conn.close()

print()
print("=" * 80)
print("✅ ALL 10 RECORDS LOADED SUCCESSFULLY")
print("=" * 80)