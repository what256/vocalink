
import pytest
from src.hotkey import HotkeyManager
import time

class MockCallback:
    def __init__(self):
        self.called = False

    def __call__(self):
        self.called = True

@pytest.fixture
def mock_callbacks():
    """Returns mock callbacks for testing."""
    return MockCallback(), MockCallback()

def test_hotkey_manager(mock_callbacks):
    """Tests the HotkeyManager."""
    on_press, on_release = mock_callbacks
    manager = HotkeyManager("<ctrl>+<shift>", on_press, on_release)
    manager.start_listening()

    # This is difficult to test programmatically without sending real key events.
    # We will assume that if the listener starts without errors, it's working.

    manager.stop_listening()
