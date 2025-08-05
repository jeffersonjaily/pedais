# Arquivo: backend/effects/equalizer.py (Versão Refatorada)

import numpy as np
from scipy.signal import lfilter

class Equalizer:
    """
    Versão "Stateful" e eficiente do Equalizer, ideal para processamento em
    tempo real (bloco a bloco).
    """
    def __init__(self, sample_rate=48000, num_channels=1):
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        
        # Atributos para guardar os coeficientes e o estado dos filtros
        self._coefficients = []
        self._filter_states = []
        self._bands_cache = None # Cache para saber se as bandas mudaram

    def _calculate_coeffs(self, bands):
        """ Calcula os coeficientes 'b' e 'a' para todas as bandas. """
        self._coefficients = []
        for band in bands:
            gain_db = band.get('gain_db', 0.0)
            if gain_db == 0:
                continue # Pula filtros com ganho zero

            center_hz = band.get('freq', 1000)
            q_factor = band.get('q', 1.0)
            filter_type = band.get('type', 'peak')
            
            A = 10**(gain_db / 40.0)
            w0 = 2 * np.pi * center_hz / self.sample_rate
            cos_w0 = np.cos(w0)
            alpha = np.sin(w0) / (2 * q_factor)

            if filter_type == 'peak':
                b0, b1, b2 = 1 + alpha * A, -2 * cos_w0, 1 - alpha * A
                a0, a1, a2 = 1 + alpha / A, -2 * cos_w0, 1 - alpha / A
            elif filter_type == 'low_shelf':
                # Fórmulas do Audio EQ Cookbook para S=1
                beta = 2 * np.sqrt(A) * alpha
                b0, b1, b2 = A * ((A + 1) - (A - 1) * cos_w0 + beta), 2 * A * ((A - 1) - (A + 1) * cos_w0), A * ((A + 1) - (A - 1) * cos_w0 - beta)
                a0, a1, a2 = (A + 1) + (A - 1) * cos_w0 + beta, -2 * ((A - 1) + (A + 1) * cos_w0), (A + 1) + (A - 1) * cos_w0 - beta
            elif filter_type == 'high_shelf':
                # Fórmulas do Audio EQ Cookbook para S=1
                beta = 2 * np.sqrt(A) * alpha
                b0, b1, b2 = A * ((A + 1) + (A - 1) * cos_w0 + beta), -2 * A * ((A - 1) + (A + 1) * cos_w0), A * ((A + 1) + (A - 1) * cos_w0 - beta)
                a0, a1, a2 = (A + 1) - (A - 1) * cos_w0 + beta, 2 * ((A - 1) - (A + 1) * cos_w0), (A + 1) - (A - 1) * cos_w0 - beta
            else:
                continue
            
            # Normaliza e adiciona à lista
            b = np.array([b0, b1, b2]) / a0
            a = np.array([a0, a1, a2]) / a0
            self._coefficients.append((b, a))

    def apply(self, audio_data: np.ndarray, **params) -> np.ndarray:
        """
        Aplica o EQ. Recalcula os coeficientes apenas se as bandas mudarem.
        """
        bands = params.get('bands', [])

        # --- OTIMIZAÇÃO: Recalcula coeficientes apenas se necessário ---
        if bands != self._bands_cache:
            self._calculate_coeffs(bands)
            # Reseta o estado dos filtros, já que os coeficientes mudaram
            num_filters = len(self._coefficients)
            self._filter_states = [np.zeros(2) for _ in range(num_filters)]
            self._bands_cache = bands

        if not self._coefficients:
            return audio_data # Retorna o áudio original se não houver filtros ativos
            
        processed_audio = audio_data.copy()

        # --- PROCESSAMENTO STATEFUL ---
        for i, (b, a) in enumerate(self._coefficients):
            # lfilter pode retornar o estado final do filtro (zf) e usá-lo como
            # estado inicial (zi) na próxima chamada. Isso garante a continuidade.
            processed_audio, self._filter_states[i] = lfilter(b, a, processed_audio, zi=self._filter_states[i])

        return processed_audio.astype(np.float32)