# backend/voz/Vocal_equalizer.py

import numpy as np
from scipy.signal import lfilter

class VocalEqualizer:
    """
    Versão "Stateful" e auto-suficiente do Equalizer para voz.
    Ele agora interpreta os seus próprios parâmetros a partir do effects_config,
    simplificando a sua utilização no motor de áudio.
    """
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self._coefficients = []
        self._filter_states = []
        self._params_cache = None # Cache para saber se os parâmetros mudaram

    def _calculate_coeffs(self, params):
        """
        Interpreta os parâmetros dos sliders e calcula os coeficientes 'b' e 'a'.
        """
        self._coefficients = []
        
        # Constrói a lista de bandas a partir dos parâmetros recebidos
        bands = []
        for param_key, gain_db in params.items():
            try:
                if 'band_' not in param_key: continue
                
                freq_part = param_key.split('_', 1)[1]
                if 'khz' in freq_part:
                    numeric_part = freq_part.replace('khz', '')
                    freq = float(numeric_part) * 1000
                else:
                    numeric_part = freq_part.replace('hz', '')
                    freq = float(numeric_part)
                
                bands.append({'type': 'peak', 'freq': freq, 'gain_db': gain_db, 'q': 1.4})
            except (IndexError, ValueError):
                continue

        # Agora, calcula os coeficientes para as bandas construídas
        for band in bands:
            gain_db = band.get('gain_db', 0.0)
            if gain_db == 0: continue

            center_hz = band.get('freq', 1000)
            q_factor = band.get('q', 1.4) # Q-factor mais musical para voz
            filter_type = band.get('type', 'peak')
            
            A = 10**(gain_db / 40.0)
            w0 = 2 * np.pi * center_hz / self.sample_rate
            cos_w0 = np.cos(w0)
            alpha = np.sin(w0) / (2 * q_factor)

            if filter_type == 'peak':
                b0, b1, b2 = 1 + alpha * A, -2 * cos_w0, 1 - alpha * A
                a0, a1, a2 = 1 + alpha / A, -2 * cos_w0, 1 - alpha / A
            # Adicione aqui 'elif' para 'low_shelf' ou 'high_shelf' se precisar deles no futuro
            else:
                continue
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([a0, a1, a2]) / a0
            self._coefficients.append((b, a))

    def apply(self, audio_data: np.ndarray, **params) -> np.ndarray:
        """
        Aplica o EQ. Recalcula os coeficientes apenas se os parâmetros dos sliders mudarem.
        """
        # Otimização: Recalcula apenas se os parâmetros dos knobs mudaram
        if params != self._params_cache:
            self._calculate_coeffs(params)
            num_filters = len(self._coefficients)
            self._filter_states = [np.zeros(2) for _ in range(num_filters)]
            self._params_cache = params

        if not self._coefficients:
            return audio_data
            
        processed_audio = audio_data.copy()

        # Processamento com estado para evitar cliques
        for i, (b, a) in enumerate(self._coefficients):
            processed_audio, self._filter_states[i] = lfilter(b, a, processed_audio, zi=self._filter_states[i])

        return processed_audio.astype(np.float32)
