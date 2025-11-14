#!/usr/bin/env python3
"""
Test path resolution for config file
"""

from pathlib import Path

# Test path resolution
file_path = Path(__file__)
print(f"Current file: {file_path}")
print(f"Parent: {file_path.parent}")
print(f"Parent parent: {file_path.parent.parent}")

config_path = file_path.parent.parent / "config" / "risk_management.yaml"
print(f"Config path: {config_path}")
print(f"Config exists: {config_path.exists()}")

if config_path.exists():
    print("✅ Config file found!")
else:
    print("❌ Config file NOT found!")
    
# Try alternative paths
alt_path1 = Path("config/risk_management.yaml")
print(f"Alt path 1: {alt_path1} (exists: {alt_path1.exists()})")

alt_path2 = Path("./config/risk_management.yaml")
print(f"Alt path 2: {alt_path2} (exists: {alt_path2.exists()})")