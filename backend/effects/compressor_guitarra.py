import numpy as np
from scipy.signal import lfilter, lfilter_zi

class CompressorEffect: # Renomeado de CompressorEffect para consistência
    """
    Implementa um efeito de compressor de áudio, com parâmetros dinâmicos
    e um modo "Bright" (high-shelf filter) otimizado.
    """

    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate

        # --- Parâmetros internos (controlados via método 'apply') ---
        self.threshold_db = -20.0
        self.ratio = 4.0
        self.attack_ms = 10.0
        self.release_ms = 200.0
        self.level = 1.0
        self.bright = False
        
        # --- Coeficientes e estado do compressor ---
        self.attack_coeff = 0.0
        self.release_coeff = 0.0
        self.envelope = 0.0
        self._update_attack_release()

        # --- Coeficientes e estado do filtro "Bright" ---
        self.bright_gain_db = 12.0
        self.bright_b = np.array([1.0])
        self.bright_a = np.array([1.0, 0.0])
        self.bright_zi = np.array([0.0])
        self._calc_bright_coeffs()

    def _update_attack_release(self):
        """Recalcula os coeficientes de attack e release."""
        # Adiciona um valor mínimo para evitar divisão por zero se o tempo for 0
        min_time_s = 0.0001
        attack_s = max(self.attack_ms / 1000.0, min_time_s)
        release_s = max(self.release_ms / 1000.0, min_time_s)
        
        self.attack_coeff = np.exp(-1.0 / (self.sample_rate * attack_s))
        self.release_coeff = np.exp(-1.0 / (self.sample_rate * release_s))

    def _calc_bright_coeffs(self):
        """Recalcula os coeficientes do filtro high-shelf para o modo Bright."""
        fc = 3000
        A = 10 ** (self.bright_gain_db / 40.0)
        w0 = 2 * np.pi * fc / self.sample_rate
        alpha = np.sin(w0) / 2.0  # Para Q=0.707

        cos_w0 = np.cos(w0)
        
        b0 =      A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
        b2 =      A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 =          ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        a1 =    2 * ((A - 1) - (A + 1) * cos_w0)
        a2 =          ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        
        self.bright_b = np.array([b0, b1, b2]) / a0
        self.bright_a = np.array([1, a1 / a0, a2 / a0])

        self.bright_zi = self.bright_zi * lfilter_zi(self.bright_b, self.bright_a)

    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        # 1. ATUALIZAR PARÂMETROS DE FORMA OTIMIZADA
        self.level = params.get('level', self.level)
        self.ratio = params.get('ratio', self.ratio)
        self.threshold_db = params.get('threshold_db', self.threshold_db)
        self.bright = params.get('bright', self.bright)

        if self.attack_ms != params.get('attack_ms', self.attack_ms) or \
           self.release_ms != params.get('release_ms', self.release_ms):
            self.attack_ms = params.get('attack_ms', self.attack_ms)
            self.release_ms = params.get('release_ms', self.release_ms)
            self._update_attack_release()

        # 2. APLICAR FILTRO "BRIGHT" (SE ATIVADO)
        processed_buffer = input_buffer
        if self.bright:
            processed_buffer, self.bright_zi = lfilter(self.bright_b, self.bright_a, input_buffer, zi=self.bright_zi)

        # 3. APLICAR COMPRESSÃO
        output_buffer = np.zeros_like(processed_buffer)
        threshold_linear = 10 ** (self.threshold_db / 20.0)
        
        for i, sample in enumerate(processed_buffer):
            # Detector de envelope (peak detector)
            rectified = abs(sample)
            if rectified > self.envelope:
                self.envelope = self.attack_coeff * self.envelope + (1 - self.attack_coeff) * rectified
            else:
                self.envelope = self.release_coeff * self.envelope + (1 - self.release_coeff) * rectified
            
            # Cálculo da redução de ganho
            gain = 1.0
            if self.envelope > threshold_linear and self.ratio > 1:
                # Quanto o sinal excedeu o threshold, em dB
                excess_db = 20 * np.log10(self.envelope / threshold_linear)
                # Redução de ganho a ser aplicada, em dB (valor negativo)
                gain_reduction_db = -excess_db * (1 - 1 / self.ratio)
                # Converte a redução de volta para escala linear
                gain = 10 ** (gain_reduction_db / 20.0)
            
            output_buffer[i] = sample * gain

        # 4. APLICAR VOLUME/LEVEL DE SAÍDA
        output_buffer *= self.level
        
        return np.clip(output_buffer, -1.0, 1.0)