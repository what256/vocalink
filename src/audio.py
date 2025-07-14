
import pyaudio
import wave
from collections import deque
import threading
import time

class AudioRecorder:
    """Records audio from a microphone and saves it to a WAV file."""

    def __init__(self, chunk_size=1024, channels=1, sample_rate=16000):
        self.chunk_size = chunk_size
        self.channels = channels
        self.sample_rate = sample_rate
        self.frames = deque()
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self, device_index=None):
        """Starts recording audio from the specified device."""
        self.frames.clear()
        self.recording = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=device_index,
        )
        threading.Thread(target=self._record_loop, daemon=True).start()

    def _record_loop(self):
        """Continuously reads audio data from the stream."""
        while self.recording:
            try:
                data = self.stream.read(self.chunk_size)
                self.frames.append(data)
            except OSError as e:
                if e.errno == -9999:
                    print("PyAudio error -9999: Input overflowed. Retrying...")
                    time.sleep(0.1)
                else:
                    raise

    def stop_recording(self, output_filename="output.wav"):
        """Stops recording and saves the audio to a file."""
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.stream = None
        self.save_to_file(output_filename)

    def save_to_file(self, filename):
        """Saves the recorded audio frames to a WAV file."""
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    def list_microphones(self):
        """Returns a list of available input devices."""
        mic_list = []
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                mic_list.append(dev['name'])
        return mic_list

    def __del__(self):
        self.p.terminate()
