#!/usr/bin/env python3
"""
Debug config loading
"""

import yaml
from pathlib import Path

# Test config loading
config_path = Path("config/risk_management.yaml")
print(f"Loading config from: {config_path}")

if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        
        # Print all top-level keys
        print(f"Top-level keys: {list(config.keys())}")
        
        # Check position_sizing section - it will take the LAST one due to YAML merging
        sizing_config = config.get('position_sizing', {})
        print(f"Position sizing config: {sizing_config}")
        
        # Check if there are all the keys we need
        for key in ['base_position_size', 'max_position_size', 'min_position_size']:
            value = sizing_config.get(key, 'NOT FOUND')
            print(f"  {key}: {value}")
else:
    print("❌ Config file not found!")