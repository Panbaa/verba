from collections import deque
from collections.abc import Callable
from io import BytesIO
import math
import wave

import numpy as np
import sounddevice as sd

from verba.core.types import RecorderDiagnostics, RecordingResult


DEFAULT_INPUT_DEVICE = 4
DEFAULT_MAX_DURATION_SECONDS = 30.0
DEFAULT_PRE_ROLL_SECONDS = 2.0
DEFAULT_POST_ROLL_SECONDS = 2.0
DEFAULT_CHUNK_MILLISECONDS = 30
DEFAULT_CALIBRATION_SECONDS = 0.5
DEFAULT_DIAGNOSTICS_INTERVAL_SECONDS = 0.15
DEFAULT_START_THRESHOLD_MULTIPLIER = 2.4
DEFAULT_CONTINUE_THRESHOLD_MULTIPLIER = 1.4
DEFAULT_NOISE_FLOOR_ALPHA = 0.98
DEFAULT_HANGOVER_SECONDS = 0.24


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        device: int | None = DEFAULT_INPUT_DEVICE,
        target_peak: float = 0.8,
        max_gain: float = 100.0,
        chunk_milliseconds: int = DEFAULT_CHUNK_MILLISECONDS,
        min_rms_threshold: float = 0.0005,
        calibration_seconds: float = DEFAULT_CALIBRATION_SECONDS,
        diagnostics_interval_seconds: float = DEFAULT_DIAGNOSTICS_INTERVAL_SECONDS,
        start_threshold_multiplier: float = DEFAULT_START_THRESHOLD_MULTIPLIER,
        continue_threshold_multiplier: float = DEFAULT_CONTINUE_THRESHOLD_MULTIPLIER,
        noise_floor_alpha: float = DEFAULT_NOISE_FLOOR_ALPHA,
        hangover_seconds: float = DEFAULT_HANGOVER_SECONDS,
    ) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._device = device
        self._target_peak = target_peak
        self._max_gain = max_gain
        self._chunk_milliseconds = chunk_milliseconds
        self._min_rms_threshold = min_rms_threshold
        self._calibration_seconds = calibration_seconds
        self._diagnostics_interval_seconds = diagnostics_interval_seconds
        self._start_threshold_multiplier = start_threshold_multiplier
        self._continue_threshold_multiplier = continue_threshold_multiplier
        self._noise_floor_alpha = noise_floor_alpha
        self._hangover_seconds = hangover_seconds

    def record(
        self,
        duration_seconds: float = DEFAULT_MAX_DURATION_SECONDS,
        pre_roll_seconds: float = DEFAULT_PRE_ROLL_SECONDS,
        post_roll_seconds: float = DEFAULT_POST_ROLL_SECONDS,
        on_diagnostics: Callable[[RecorderDiagnostics], None] | None = None,
    ) -> RecordingResult:
        frames_per_chunk = max(1, int(self._sample_rate * self._chunk_milliseconds / 1000))
        chunk_duration_seconds = frames_per_chunk / self._sample_rate
        pre_roll_chunk_count = max(1, math.ceil(pre_roll_seconds / chunk_duration_seconds))
        calibration_chunk_count = max(1, math.ceil(self._calibration_seconds / chunk_duration_seconds))

        speech_started = False
        silent_time = 0.0
        elapsed_time = 0.0
        noise_floor = 0.0
        noise_floor_samples = 0
        start_threshold = self._min_rms_threshold
        continue_threshold = self._min_rms_threshold
        chunks: list[np.ndarray] = []
        pre_roll = deque(maxlen=pre_roll_chunk_count)
        overflow_count = 0
        stop_reason = "max_duration"
        last_diagnostics = RecorderDiagnostics(
            state="calibrating",
            elapsed_seconds=0.0,
            captured_seconds=0.0,
            current_rms=0.0,
            active_threshold=start_threshold,
            start_threshold=start_threshold,
            continue_threshold=continue_threshold,
            noise_floor=noise_floor,
            silent_seconds=0.0,
            speech_started=False,
            overflow_count=0,
        )
        last_diagnostics_emit = -self._diagnostics_interval_seconds

        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            device=self._device,
            blocksize=frames_per_chunk,
        ) as stream:
            while elapsed_time < duration_seconds:
                chunk, overflowed = self._read_next_chunk(stream, frames_per_chunk)
                if overflowed:
                    overflow_count += 1

                rms = self._compute_rms(chunk)
                elapsed_time += chunk_duration_seconds

                if not speech_started:
                    pre_roll.append(chunk)
                    if noise_floor_samples < calibration_chunk_count:
                        noise_floor = self._update_noise_floor(noise_floor, noise_floor_samples, rms)
                        noise_floor_samples += 1
                    elif rms < start_threshold:
                        noise_floor = self._adapt_noise_floor(noise_floor, rms)

                if speech_started and rms < continue_threshold:
                    noise_floor = self._adapt_noise_floor(noise_floor, rms)

                start_threshold = self._threshold_from_multiplier(
                    noise_floor,
                    self._start_threshold_multiplier,
                )
                continue_threshold = self._threshold_from_multiplier(
                    noise_floor,
                    self._continue_threshold_multiplier,
                )
                active_threshold = continue_threshold if speech_started else start_threshold

                state = self._determine_state(
                    speech_started=speech_started,
                    noise_floor_samples=noise_floor_samples,
                    calibration_chunk_count=calibration_chunk_count,
                    silent_time=silent_time,
                )
                captured_seconds = self._captured_seconds(chunks)
                last_diagnostics = RecorderDiagnostics(
                    state=state,
                    elapsed_seconds=elapsed_time,
                    captured_seconds=captured_seconds,
                    current_rms=rms,
                    active_threshold=active_threshold,
                    start_threshold=start_threshold,
                    continue_threshold=continue_threshold,
                    noise_floor=noise_floor,
                    silent_seconds=silent_time,
                    speech_started=speech_started,
                    overflow_count=overflow_count,
                )
                if (
                    on_diagnostics is not None
                    and elapsed_time - last_diagnostics_emit >= self._diagnostics_interval_seconds
                ):
                    on_diagnostics(last_diagnostics)
                    last_diagnostics_emit = elapsed_time

                if rms >= active_threshold:
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
                    if silent_time < self._hangover_seconds:
                        continue
                    if silent_time >= post_roll_seconds:
                        stop_reason = "silence_timeout"
                        break

        if not chunks:
            stop_reason = "no_speech"
            recording = np.zeros((0, self._channels), dtype=np.float32)
        else:
            recording = np.concatenate(chunks, axis=0)

        duration_captured_seconds = recording.shape[0] / self._sample_rate
        peak_level = float(np.abs(recording).max()) if recording.size else 0.0
        recording = self._normalize_recording(recording)

        final_diagnostics = RecorderDiagnostics(
            state="finished",
            elapsed_seconds=elapsed_time,
            captured_seconds=duration_captured_seconds,
            current_rms=last_diagnostics.current_rms,
            active_threshold=last_diagnostics.active_threshold,
            start_threshold=start_threshold,
            continue_threshold=continue_threshold,
            noise_floor=noise_floor,
            silent_seconds=silent_time,
            speech_started=speech_started,
            overflow_count=overflow_count,
            stop_reason=stop_reason,
        )
        if on_diagnostics is not None:
            on_diagnostics(final_diagnostics)

        return RecordingResult(
            wav_bytes=self._encode_wav(recording),
            speech_detected=recording.size > 0,
            duration_seconds=duration_captured_seconds,
            peak_level=peak_level,
            stop_reason=stop_reason,
            diagnostics=final_diagnostics,
        )

    def record_wav(
        self,
        duration_seconds: float = DEFAULT_MAX_DURATION_SECONDS,
        pre_roll_seconds: float = DEFAULT_PRE_ROLL_SECONDS,
        post_roll_seconds: float = DEFAULT_POST_ROLL_SECONDS,
    ) -> bytes:
        return self.record(
            duration_seconds=duration_seconds,
            pre_roll_seconds=pre_roll_seconds,
            post_roll_seconds=post_roll_seconds,
        ).wav_bytes

    def _encode_wav(self, recording: np.ndarray) -> bytes:
        pcm16 = np.int16(np.clip(recording, -1.0, 1.0) * 32767)

        buffer = BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self._channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(pcm16.tobytes())

        return buffer.getvalue()

    def _read_next_chunk(self, stream: sd.InputStream, frames_per_chunk: int) -> tuple[np.ndarray, bool]:
        chunk, overflowed = stream.read(frames_per_chunk)
        return chunk.copy(), overflowed

    def _determine_state(
        self,
        speech_started: bool,
        noise_floor_samples: int,
        calibration_chunk_count: int,
        silent_time: float,
    ) -> str:
        if not speech_started and noise_floor_samples < calibration_chunk_count:
            return "calibrating"
        if not speech_started:
            return "waiting_for_speech"
        if 0.0 < silent_time < self._hangover_seconds:
            return "maybe_silence"
        if silent_time >= self._hangover_seconds:
            return "post_roll"
        return "capturing_speech"

    def _captured_seconds(self, chunks: list[np.ndarray]) -> float:
        if not chunks:
            return 0.0
        frame_count = sum(chunk.shape[0] for chunk in chunks)
        return frame_count / self._sample_rate

    def _compute_rms(self, chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(chunk.reshape(-1)))))

    def _threshold_from_multiplier(self, noise_floor: float, multiplier: float) -> float:
        return max(noise_floor * multiplier, self._min_rms_threshold)

    def _update_noise_floor(self, noise_floor: float, sample_count: int, current_rms: float) -> float:
        if sample_count == 0:
            return current_rms
        return ((noise_floor * sample_count) + current_rms) / (sample_count + 1)

    def _adapt_noise_floor(self, noise_floor: float, current_rms: float) -> float:
        if noise_floor <= 0.0:
            return current_rms
        return (
            (self._noise_floor_alpha * noise_floor)
            + ((1.0 - self._noise_floor_alpha) * current_rms)
        )

    def _normalize_recording(self, recording: np.ndarray) -> np.ndarray:
        if recording.size == 0:
            return recording

        peak = float(np.abs(recording).max())
        if peak <= 1e-6:
            return recording

        gain = min(self._target_peak / peak, self._max_gain)
        return np.clip(recording * gain, -1.0, 1.0)