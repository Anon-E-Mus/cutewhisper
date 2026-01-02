"""
Configuration Management Module - Handles application settings with validation
"""

import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Config:
    """Manage application configuration with validation"""

    DEFAULT_CONFIG = {
        'hotkey': {
            'toggle': 'ctrl+space'  # Press and hold to record
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1
        },
        'whisper': {
            'model_size': 'base',
            'language': 'auto',
            'device': 'cpu',
            'compute_type': 'int8'
        },
        'ui': {
            'show_notifications': True,
            'recording_indicator': True,
            'use_clipboard': True,
            'preserve_clipboard': True  # Restore clipboard after paste
        }
    }

    # Validation rules
    VALID_MODELS = ['tiny', 'base', 'small', 'medium', 'large', 'large-v1', 'large-v2', 'large-v3']
    VALID_DEVICES = ['cpu', 'cuda']
    VALID_CHANNELS = [1, 2]
    VALID_LANGUAGES = ['auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh', 'ja', 'ko']

    def __init__(self, config_path='config/user_config.yaml'):
        """
        Initialize configuration

        Args:
            config_path: Path to user config file (relative or absolute)
        """
        self.config_path = Path(config_path) if config_path else Path('config/user_config.yaml')
        self.config = self.load_config()
        self.validate_config()

    def load_config(self) -> dict:
        """
        Load config or create default

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}

                # Merge with defaults (user config overrides defaults)
                config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
                logger.info(f"Loaded config from {self.config_path}")
                return config

            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.info("No config file found, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, base_dict: dict, override_dict: dict) -> dict:
        """
        Deep merge two dictionaries

        Args:
            base_dict: Base dictionary (defaults)
            override_dict: Override dictionary (user config)

        Returns:
            Merged dictionary
        """
        result = base_dict.copy()
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def validate_config(self):
        """Validate configuration values and correct to safe defaults"""
        # Validate Whisper model size
        model_size = self.config.get('whisper', {}).get('model_size')
        if model_size not in self.VALID_MODELS:
            logger.warning(f"Invalid model_size '{model_size}', using 'base'")
            self.config.setdefault('whisper', {})['model_size'] = 'base'

        # Validate device
        device = self.config.get('whisper', {}).get('device')
        if device not in self.VALID_DEVICES:
            logger.warning(f"Invalid device '{device}', using 'cpu'")
            self.config.setdefault('whisper', {})['device'] = 'cpu'

        # Validate language
        language = self.config.get('whisper', {}).get('language')
        if language not in self.VALID_LANGUAGES:
            logger.warning(f"Invalid language '{language}', using 'auto'")
            self.config.setdefault('whisper', {})['language'] = 'auto'

        # Validate audio channels
        channels = self.config.get('audio', {}).get('channels')
        if channels not in self.VALID_CHANNELS:
            logger.warning(f"Invalid channels '{channels}', using 1")
            self.config.setdefault('audio', {})['channels'] = 1

        # Validate sample rate (must be positive)
        sample_rate = self.config.get('audio', {}).get('sample_rate')
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            logger.warning(f"Invalid sample_rate '{sample_rate}', using 16000")
            self.config.setdefault('audio', {})['sample_rate'] = 16000

    def save_config(self):
        """Persist config to file"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Config saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def get(self, key_path: str, default=None):
        """
        Get nested config value using dot notation

        Args:
            key_path: Dot-separated path (e.g., 'whisper.model_size')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key_path: str, value):
        """
        Set nested config value using dot notation

        Args:
            key_path: Dot-separated path (e.g., 'whisper.model_size')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        logger.debug(f"Config updated: {key_path} = {value}")
