import numpy as np

class NoiseReducer:
    """
    Redutor simples de ruído de fundo (noise gate) baseado em limiar e atenuação.
    Ideal para pausas ou regiões de baixa energia vocal.
    """

    def __init__(self, threshold=0.02, reduction_db=20):
        self.threshold = threshold
        self.gain = 10 ** (-reduction_db / 20)  # converte dB para multiplicador linear

    def apply(self, audio_data: np.ndarray) -> np.ndarray:
        output = audio_data.copy()
        mask = np.abs(audio_data) < self.threshold
        output[mask] *= self.gain  # atenua regiões silenciosas
        return output.astype(np.float32)
