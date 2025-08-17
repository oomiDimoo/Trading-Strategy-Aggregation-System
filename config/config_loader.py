import json
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """
    Load the configuration file.

    Returns:
        Dictionary containing the configuration
    """
    with open('config/config.json', 'r') as f:
        return json.load(f)

def get_strategy_defaults(strategy_name: str) -> Dict[str, Any]:
    """
    Get the default parameters for a specific strategy.

    Args:
        strategy_name: The name of the strategy

    Returns:
        Dictionary containing the default parameters
    """
    config = load_config()
    return config.get('strategy_defaults', {}).get(strategy_name, {})
