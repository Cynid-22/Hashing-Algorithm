"""
Configuration module for Hash Algorithm GUI.
"""

import json
import os
from typing import List, Dict, Optional
from tkinter import messagebox

class HashAlgorithm:
    """Dynamically loads hash algorithms from config file."""
    
    _algorithms: List[Dict] = []
    _config_loaded = False
    
    @classmethod
    def load_config(cls, config_path: str = "algorithms.json") -> None:
        """
        Load algorithms from the configuration file.
        
        Args:
            config_path: Path to the algorithms configuration file
        """
        if cls._config_loaded:
            return
            
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, config_path)
        
        try:
            with open(full_path, 'r') as f:
                config = json.load(f)
                cls._algorithms = config.get('algorithms', [])
                cls._config_loaded = True
        except FileNotFoundError:
            messagebox.showerror(
                "Configuration Error",
                f"Could not find {config_path}. Using default algorithms."
            )
            # Fallback to default algorithms
            cls._algorithms = [
                {"name": "SHA-256", "type": "hashlib", "hashlib_name": "sha256"},
                {"name": "SHA-384", "type": "hashlib", "hashlib_name": "sha384"},
                {"name": "SHA-512", "type": "hashlib", "hashlib_name": "sha512"}
            ]
            cls._config_loaded = True
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Configuration Error",
                f"Invalid JSON in {config_path}: {e}"
            )
            cls._algorithms = []
            cls._config_loaded = True
    
    @classmethod
    def get_algorithm_config(cls, name: str) -> Optional[Dict]:
        """
        Get the configuration for a specific algorithm.
        
        Args:
            name: The algorithm name
            
        Returns:
            The algorithm configuration dictionary or None
        """
        cls.load_config()
        for algo in cls._algorithms:
            if algo['name'] == name:
                return algo
        return None
    
    @classmethod
    def all(cls) -> List[str]:
        """Return all available algorithm names."""
        cls.load_config()
        return [algo['name'] for algo in cls._algorithms]
