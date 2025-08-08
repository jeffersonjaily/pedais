import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi

class PopClickSuppressor:
    """
    Suprime plosivas ("pufs") e estalos de boca (transientes) de forma otimizada.
    """

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.last_state_highpass = None

    def apply(self, audio_data: np.ndarray, cutoff_hz=120, click_threshold=0.7) -> np.ndarray:
        
        # 1. Filtro passa-alta para remover plosivas
        nyquist = 0.5 * self.sample_rate
        # Ordem do filtro aumentada para 4 para uma atenuação mais forte
        b_high, a_high = butter(4, cutoff_hz / nyquist, btype='high')
        
        if self.last_state_highpass is None:
            self.last_state_highpass = lfilter_zi(b_high, a_high)

        filtered, self.last_state_highpass = lfilter(b_high, a_high, audio_data, zi=self.last_state_highpass)

        # 2. Supressor de cliques vetorial (sem loop!)
        filtered_abs = np.abs(filtered)
        prev_samples = np.roll(filtered_abs, 1)
        next_samples = np.roll(filtered_abs, -1)
        
        neighbor_threshold = 0.1 * click_threshold 
        
        is_click = (filtered_abs > click_threshold) & (prev_samples < neighbor_threshold) & (next_samples < neighbor_threshold)
        
        # 3. Interpolação para suavizar o clique
        output = filtered.copy()
        
        if np.any(is_click):
            click_indices = np.where(is_click)[0]
            for idx in click_indices:
                output[idx] = (output[idx - 1] + output[idx + 1]) / 2 if idx > 0 and idx < len(output) - 1 else 0
        
        return output.astype(np.float32)