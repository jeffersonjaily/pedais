import numpy as np
from scipy.signal import resample

class PitchShift:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

    def apply(self, audio_data: np.ndarray, semitones=2, mix=1.0) -> np.ndarray:
        factor = 2 ** (semitones / 12)
        new_len = int(len(audio_data) / factor)
        shifted = resample(audio_data, new_len)

        if len(shifted) < len(audio_data):
            shifted = np.pad(shifted, (0, len(audio_data) - len(shifted)))
        else:
            shifted = shifted[:len(audio_data)]

        output = (1 - mix) * audio_data + mix * shifted
        return output.astype(np.float32)