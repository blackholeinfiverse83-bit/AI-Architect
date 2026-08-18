#!/usr/bin/env python3
"""
Test MongoDB connection
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from pymongo import MongoClient
from app.config import settings
import time

print("=" * 70)
print("MONGODB CONNECTION TEST")
print("=" * 70)
print()

print(f"MongoDB URL: {settings.MONGODB_URL[:50]}...")
print(f"Database: {settings.MONGODB_DATABASE}")
print()

print("Attempting to connect...")
start_time = time.time()

try:
    # Try with shorter timeout
    client = MongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=10000,  # 10 seconds
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )

    # Test connection
    client.admin.command('ping')

    elapsed = time.time() - start_time
    print(f"[SUCCESS] Connected to MongoDB in {elapsed:.2f} seconds")
    print()

    # Get database
    db = client[settings.MONGODB_DATABASE]

    # Check collections
    collections = db.list_collection_names()
    print(f"Collections found: {len(collections)}")
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  - {coll}: {count} documents")

    print()

    # Check admin user
    print("Checking admin user...")
    user = db.users.find_one({"username": "admin"})
    if user:
        print(f"[OK] Admin user found")
        print(f"  _id: {user.get('_id')}")
        print(f"  username: {user.get('username')}")
        print(f"  is_active: {user.get('is_active')}")
    else:
        print("[ERROR] Admin user not found")

    client.close()

except Exception as e:
    elapsed = time.time() - start_time
    print(f"[ERROR] Connection failed after {elapsed:.2f} seconds")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
