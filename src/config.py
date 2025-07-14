
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AppConfig(BaseModel):
    """Application configuration model."""
    model_config = ConfigDict(protected_namespaces=(), extra='ignore')

    model_size: str = Field("auto", description="Whisper model size (auto, tiny, base, small, medium, large).")
    mic_device: Optional[int] = Field(None, description="Index of the preferred microphone device.")
    hotkey: str = Field("<ctrl>+<shift>", description="Hotkey combination (e.g., <ctrl>+<shift>).")
    theme: str = Field("superhero", description="UI theme for the settings window.")
    auto_launch: bool = Field(False, description="Launch the application on system startup.")
    minimize_to_tray: bool = Field(True, description="Minimize the settings window to the system tray.")


def load_config(path: str = "config.json") -> AppConfig:
    """Loads the application configuration from a JSON file."""
    try:
        with open(path, "r") as f:
            return AppConfig.model_validate_json(f.read())
    except (FileNotFoundError, ValueError):
        return AppConfig()

def save_config(config: AppConfig, path: str = "config.json"):
    """Saves the application configuration to a JSON file."""
    with open(path, "w") as f:
        f.write(config.model_dump_json(indent=4))
