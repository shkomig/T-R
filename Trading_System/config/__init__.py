"""
Configuration Module
====================

Handles loading and validation of configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_name: str = "trading_config") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        
    Returns:
        Dictionary with configuration data
    """
    config_path = Path(__file__).parent / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


__all__ = ["load_config"]
