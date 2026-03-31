from io import BytesIO
import wave
import numpy as np
import sounddevice as sd


DEFAULT_INPUT_DEVICE = 4


class AudioRecorder:
    def __init__(self, sample_rate: int = 16_000, channels: int = 1, device: int | None = DEFAULT_INPUT_DEVICE, target_peak: float = 0.8, max_gain: float = 100.0) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._device = device
        self._target_peak = target_peak
        self._max_gain = max_gain

    def record_wav(self, duration_seconds: float = 3.0) -> bytes:
        frame_count = int(duration_seconds * self._sample_rate)

        recording = sd.rec(
            frame_count,
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            device=self._device,
        )
        sd.wait()
        recording = self._normalize_recording(recording)

        pcm16 = np.int16(np.clip(recording, -1.0, 1.0) * 32767)

        buffer = BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self._channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(pcm16.tobytes())

        return buffer.getvalue()

    def _normalize_recording(self, recording: np.ndarray) -> np.ndarray:
        peak = float(np.abs(recording).max())
        if peak <= 1e-6:
            return recording

        gain = min(self._target_peak / peak, self._max_gain)
        return np.clip(recording * gain, -1.0, 1.0)