
import pytest
from src.config import AppConfig, load_config, save_config
import os

@pytest.fixture
def temp_config_file(tmp_path):
    """Creates a temporary config file for testing."""
    return tmp_path / "config.json"

def test_load_default_config(temp_config_file):
    """Tests loading the default configuration."""
    config = load_config(str(temp_config_file))
    assert isinstance(config, AppConfig)
    assert config.model_size == "tiny"

def test_save_and_load_config(temp_config_file):
    """Tests saving and loading a configuration."""
    config = AppConfig(model_size="base", theme="darkly")
    save_config(config, str(temp_config_file))
    loaded_config = load_config(str(temp_config_file))
    assert loaded_config.model_size == "base"
    assert loaded_config.theme == "darkly"
