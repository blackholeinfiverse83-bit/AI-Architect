"""
Root conftest.py — loaded by pytest before any test module is imported.
Sets demo auth env vars so Settings picks them up at import time.
Does NOT affect production: these vars are only active during pytest runs.
"""
import os

os.environ.setdefault("DEMO_MODE", "True")
os.environ.setdefault("DEMO_USERNAME", "demo")
os.environ.setdefault("DEMO_PASSWORD", "demo123")
