
import pytest
from src.audio import AudioRecorder
import os

@pytest.fixture
def recorder():
    """Returns an AudioRecorder instance."""
    return AudioRecorder()

def test_list_microphones(recorder):
    """Tests listing available microphones."""
    mics = recorder.list_microphones()
    assert isinstance(mics, list)

# Note: Testing recording requires a virtual audio device or user interaction,
# which is beyond the scope of this automated test suite.
