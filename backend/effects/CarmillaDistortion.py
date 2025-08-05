# backend/effects/CarmillaDistortion.py
import numpy as np
from scipy.signal import lfilter, lfilter_zi

class CarmillaDistortionEffect:
    """
    Simula um pedal de distorção de alto ganho com múltiplos estágios de EQ e
    clipping assimétrico, otimizado para performance em tempo real.
    """
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate

        # --- Parâmetros internos ---
        self.gain = 12.0
        self.level = 7.0
        self.tone = 6.0

        # --- Coeficientes e estados dos filtros (inicialização) ---
        self.pre_eq_b, self.pre_eq_a = np.array([1.]), np.array([1.])
        self.tone_b, self.tone_a = np.array([1.]), np.array([1.])
        self.pre_eq_zi = np.zeros(2)
        self.tone_zi = np.zeros(2)

        self._update_filters()

    def _update_filters(self):
        """ Recalcula todos os coeficientes dos filtros de uma vez. """
        # Pré-EQ (Low-shelf filter antes da distorção)
        fc_pre = 800  # Foco nos médios-graves
        gain_db_pre = (self.tone / 10.0 - 0.5) * 12 # -6dB a +6dB
        A = 10**(gain_db_pre / 40)
        w0 = 2 * np.pi * fc_pre / self.sample_rate
        alpha = np.sin(w0) / 2
        cos_w0 = np.cos(w0)
        
        b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
        b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
        a2 = (A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        self.pre_eq_b = np.array([b0, b1, b2]) / a0
        self.pre_eq_a = np.array([1, a1 / a0, a2 / a0])

        # Pós-EQ (High-shelf filter para dar brilho)
        fc_tone = 1500 # Foco nos agudos
        gain_db_tone = (self.tone / 10.0 - 0.5) * 18 # -9dB a +9dB
        A = 10**(gain_db_tone / 40)
        w0 = 2 * np.pi * fc_tone / self.sample_rate
        alpha = np.sin(w0) / 2
        cos_w0 = np.cos(w0)

        b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
        b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
        a2 = (A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        self.tone_b = np.array([b0, b1, b2]) / a0
        self.tone_a = np.array([1, a1 / a0, a2 / a0])

        # Atualiza o estado inicial do filtro para a transição suave
        self.pre_eq_zi = lfilter_zi(self.pre_eq_b, self.pre_eq_a) * self.pre_eq_zi[0]
        self.tone_zi = lfilter_zi(self.tone_b, self.tone_a) * self.tone_zi[0]

    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        # 1. Atualizar Parâmetros
        self.gain = params.get('gain', self.gain)
        self.level = params.get('level', self.level)
        
        new_tone = params.get('tone', self.tone)
        if new_tone != self.tone:
            self.tone = new_tone
            self._update_filters()

        # 2. Pré-Equalização (otimizado com lfilter)
        pre_eq_out, self.pre_eq_zi = lfilter(self.pre_eq_b, self.pre_eq_a, input_buffer, zi=self.pre_eq_zi)

        # 3. Estágio de Ganho
        gained = pre_eq_out * self.gain

        # 4. Clipping Assimétrico (já estava ótimo e vetorizado)
        clipped = np.tanh(gained * 0.5) # Suaviza um pouco antes do hard clip
        clipped[clipped > 0.8] = 0.8
        clipped[clipped < -0.6] = -0.6
        
        # 5. Pós-Equalização / Tone (otimizado com lfilter)
        tone_out, self.tone_zi = lfilter(self.tone_b, self.tone_a, clipped, zi=self.tone_zi)

        # 6. Volume Final
        output_signal = tone_out * self.level
        
        return np.clip(output_signal, -1.0, 1.0)