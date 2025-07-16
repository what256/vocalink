
import pytest
import time
import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import VocalInkApp
from hotkey import paste_text

# Mock the paste_text function
@pytest.fixture
def mock_paste_text():
    with patch('main.paste_text') as mock:
        yield mock

@pytest.fixture
def vocal_ink_app():
    # Initialize the app without starting the tray icon or hotkey listener
    # We'll manually trigger the actions for testing
    app = VocalInkApp()
    app.hotkey_manager.stop_listening() # Ensure hotkey listener is stopped
    app.tray_icon.stop() # Ensure tray icon is stopped
    yield app
    app.destroy() # Clean up after the test

def test_mic_to_paste_latency(vocal_ink_app, mock_paste_text):
    # Simulate a short audio recording
    # In a real scenario, you'd feed actual audio data to the recorder
    # For this test, we'll mock the recorder's internal frames
    # and directly call stop_and_transcribe

    # Mock the AudioRecorder to return dummy audio frames
    dummy_audio_frames = [b'\x00' * 1024 for _ in range(10)] # 10 chunks of silence

    with patch.object(vocal_ink_app.recorder, 'start_recording', return_value=None):
        with patch.object(vocal_ink_app.recorder, 'stop_recording', return_value=dummy_audio_frames):
            with patch.object(vocal_ink_app.transcriber, 'transcribe', return_value="This is a test transcription.") as mock_transcribe:
                start_time = time.time()
                vocal_ink_app.start_recording()
                vocal_ink_app.stop_and_transcribe()
                end_time = time.time()

                latency_ms = (end_time - start_time) * 1000
                print(f"Mic-to-paste latency: {latency_ms:.2f} ms")

                # Assert that paste_text was called
                mock_paste_text.assert_called_once()

                # Assert latency is within the acceptable limit
                assert latency_ms < 150, f"Latency {latency_ms:.2f} ms exceeded 150 ms limit."

