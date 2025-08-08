import numpy as np

class PitchCorrection:
    def __init__(self):
        pass

    def apply(self, audio_data: np.ndarray, strength=0.5, mix=1.0) -> np.ndarray:
        smoothed = np.convolve(audio_data, np.ones(5)/5, mode='same')
        corrected = (1 - strength) * audio_data + strength * smoothed
        output = (1 - mix) * audio_data + mix * corrected
        return output.astype(np.float32)