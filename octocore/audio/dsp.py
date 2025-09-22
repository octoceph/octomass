"""Digital Signal Processing utilities for audio analysis.

Основные возможности:
- загрузка аудио (librosa)
- mel-spectrogram, MFCC, spectrogram
- простая эвристика детекции событий по энергии
- простые признаки для опознавания типа звука (bird/bee etc.)

Все функции документированы на русском.
"""
import numpy as np
import librosa
from loguru import logger
from typing import Tuple, List, Dict

def load_audio(path: str, sr: int = 22050, mono: bool = True) -> Tuple[np.ndarray, int]:
    """Загрузить аудио с нормализацией частоты дискретизации."""
    logger.info("Loading audio from %s (sr=%s)", path, sr)
    y, sr_ret = librosa.load(path, sr=sr, mono=mono)
    logger.debug("Loaded audio len=%s sr=%s", y.shape, sr_ret)
    return y, sr_ret

def compute_melspec(y: np.ndarray, sr: int, n_mels: int = 128, n_fft: int = 2048, hop_length: int = 512) -> np.ndarray:
    """Вычислить mel-спектрограмму и вернуть в dB."""
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db

def compute_mfcc(y: np.ndarray, sr: int, n_mfcc: int = 13, **kwargs) -> np.ndarray:
    """Вычислить MFCC."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, **kwargs)
    return mfcc

def compute_spectrogram(y: np.ndarray, sr: int, n_fft: int = 2048, hop_length: int = 512):
    """STFT -> амплитудная спектрограмма в dB плюс частоты/времена."""
    S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    S_mag = np.abs(S)
    S_db = librosa.amplitude_to_db(S_mag, ref=np.max)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
    return S_db, freqs, times

def detect_events_energy(y: np.ndarray, sr: int, frame_length: int = 2048, hop_length: int = 512, threshold: float = 2.0) -> List[Dict]:
    """Детектируем пики энергии — простая эвристика."""
    S = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(S)), sr=sr, hop_length=hop_length)
    mean = float(np.mean(S))
    std = float(np.std(S))
    events = []
    is_event = False
    event_start = None
    for i, val in enumerate(S):
        if val > mean + threshold * std:
            if not is_event:
                is_event = True
                event_start = float(times[i])
        else:
            if is_event:
                event_end = float(times[i])
                # peak index in the window
                window_start = max(0, i-10)
                peak_idx = int(window_start + np.argmax(S[window_start:i]))
                peak_time = float(times[peak_idx])
                score = float(S[peak_idx])
                events.append({"start_time": event_start, "end_time": event_end, "peak_time": peak_time, "score": score})
                is_event = False
                event_start = None
    logger.info("Detected %d energy events", len(events))
    return events

def simple_bird_bee_detector(melspec: np.ndarray) -> Dict:
    """Простейший классификатор на основе отношения энергии в полосах частот."""
    n_mels = melspec.shape[0]
    low = float(melspec[:n_mels//3, :].mean())
    mid = float(melspec[n_mels//3:2*n_mels//3, :].mean())
    high = float(melspec[2*n_mels//3:, :].mean())
    score_bee = (mid - low) - 0.5*(high - mid)
    score_bird = (high - mid) + 0.2*(mid - low)
    return {"score_bee": float(score_bee), "score_bird": float(score_bird), "low": low, "mid": mid, "high": high}
