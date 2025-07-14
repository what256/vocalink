
import pytest
from src.transcriber import Transcriber
import os

@pytest.fixture
def transcriber():
    """Returns a Transcriber instance."""
    return Transcriber()

def test_transcribe_audio(transcriber):
    """Tests transcribing an audio file."""
    # Create a dummy audio file for testing
    import wave
    import numpy as np

    test_audio_path = "test.wav"
    sample_rate = 16000
    duration = 1  # seconds
    frequency = 440  # Hz
    t = np.linspace(0., duration, int(sample_rate * duration))
    amplitude = np.iinfo(np.int16).max * 0.5
    data = amplitude * np.sin(2. * np.pi * frequency * t)

    with wave.open(test_audio_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data.astype(np.int16).tobytes())

    transcription = transcriber.transcribe(test_audio_path)
    assert isinstance(transcription, str)
    os.remove(test_audio_path)
