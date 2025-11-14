#!/usr/bin/env python3
"""
Test config loading
"""

import yaml
from pathlib import Path

# Test config loading
config_path = Path("config/risk_management.yaml")
print(f"Loading config from: {config_path}")

if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        print("Config loaded successfully!")
        
        # Check position_sizing section
        sizing_config = config.get('position_sizing', {})
        print(f"Position sizing config: {sizing_config}")
        
        base_size = sizing_config.get('base_position_size', 'NOT FOUND')
        max_size = sizing_config.get('max_position_size', 'NOT FOUND')
        
        print(f"Base Position Size: {base_size}")
        print(f"Max Position Size: {max_size}")
else:
    print("❌ Config file not found!")