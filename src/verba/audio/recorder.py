from collections import deque
from io import BytesIO
import math
import wave
import numpy as np
import sounddevice as sd


DEFAULT_INPUT_DEVICE = 4
DEFAULT_MAX_DURATION_SECONDS = 30.0
DEFAULT_PRE_ROLL_SECONDS = 2.0
DEFAULT_POST_ROLL_SECONDS = 2.0
DEFAULT_CHUNK_MILLISECONDS = 30
DEFAULT_CALIBRATION_SECONDS = 0.5


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        device: int | None = DEFAULT_INPUT_DEVICE,
        target_peak: float = 0.8,
        max_gain: float = 100.0,
        chunk_milliseconds: int = DEFAULT_CHUNK_MILLISECONDS,
        speech_threshold_multiplier: float = 2.0,
        min_rms_threshold: float = 0.0005,
        calibration_seconds: float = DEFAULT_CALIBRATION_SECONDS,
    ) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._device = device
        self._target_peak = target_peak
        self._max_gain = max_gain
        self._chunk_milliseconds = chunk_milliseconds
        self._speech_threshold_multiplier = speech_threshold_multiplier
        self._min_rms_threshold = min_rms_threshold
        self._calibration_seconds = calibration_seconds

    def record_wav(
        self,
        duration_seconds: float = DEFAULT_MAX_DURATION_SECONDS,
        pre_roll_seconds: float = DEFAULT_PRE_ROLL_SECONDS,
        post_roll_seconds: float = DEFAULT_POST_ROLL_SECONDS,
    ) -> bytes:
        frames_per_chunk = max(1, int(self._sample_rate * self._chunk_milliseconds / 1000))
        chunk_duration_seconds = frames_per_chunk / self._sample_rate
        pre_roll_chunk_count = max(1, math.ceil(pre_roll_seconds / chunk_duration_seconds))
        calibration_chunk_count = max(1, math.ceil(self._calibration_seconds / chunk_duration_seconds))

        speech_started = False
        silent_time = 0.0
        elapsed_time = 0.0
        noise_floor = 0.0
        noise_floor_samples = 0
        threshold = self._min_rms_threshold
        chunks: list[np.ndarray] = []
        pre_roll = deque(maxlen=pre_roll_chunk_count)

        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            device=self._device,
            blocksize=frames_per_chunk,
        ) as stream:
            while elapsed_time < duration_seconds:
                chunk = self._read_next_chunk(stream, frames_per_chunk)
                rms = self._compute_rms(chunk)
                elapsed_time += chunk_duration_seconds

                if not speech_started:
                    pre_roll.append(chunk)
                    if noise_floor_samples < calibration_chunk_count:
                        noise_floor = self._update_noise_floor(noise_floor, noise_floor_samples, rms)
                        noise_floor_samples += 1
                        threshold = max(
                            noise_floor * self._speech_threshold_multiplier,
                            self._min_rms_threshold,
                        )

                if rms >= threshold:
                    if not speech_started:
                        chunks.extend(pre_roll)
                        speech_started = True
                    else:
                        chunks.append(chunk)
                    silent_time = 0.0
                    continue

                if speech_started:
                    chunks.append(chunk)
                    silent_time += chunk_duration_seconds
                    if silent_time >= post_roll_seconds:
                        break

        if not chunks:
            recording = np.zeros((0, self._channels), dtype=np.float32)
        else:
            recording = np.concatenate(chunks, axis=0)

        recording = self._normalize_recording(recording)

        return self._encode_wav(recording)

    def _encode_wav(self, recording: np.ndarray) -> bytes:
        pcm16 = np.int16(np.clip(recording, -1.0, 1.0) * 32767)

        buffer = BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self._channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(pcm16.tobytes())

        return buffer.getvalue()

    def _read_next_chunk(self, stream: sd.InputStream, frames_per_chunk: int) -> np.ndarray:
        chunk, overflowed = stream.read(frames_per_chunk)
        if overflowed:
            return chunk.copy()
        return chunk.copy()

    def _compute_rms(self, chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(chunk.reshape(-1)))))

    def _update_noise_floor(self, noise_floor: float, sample_count: int, current_rms: float) -> float:
        if sample_count == 0:
            return current_rms
        return ((noise_floor * sample_count) + current_rms) / (sample_count + 1)

    def _normalize_recording(self, recording: np.ndarray) -> np.ndarray:
        if recording.size == 0:
            return recording

        peak = float(np.abs(recording).max())
        if peak <= 1e-6:
            return recording

        gain = min(self._target_peak / peak, self._max_gain)
        return np.clip(recording * gain, -1.0, 1.0)