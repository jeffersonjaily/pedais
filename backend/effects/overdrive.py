# backend/effects/overdrive.py

import numpy as np
from scipy.signal import butter, lfilter

class Overdrive:
    """
    Implementa um efeito de Overdrive robusto com pré-filtro,
    clipping assimétrico e controlo de tonalidade (pós-filtro).
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Pré-aloca os coeficientes dos filtros para não os recalcular a cada chamada
        self.hp_b, self.hp_a = butter(1, 120.0, btype='high', fs=sample_rate)
        self.lp_b, self.lp_a = None, None
        self.last_tone = -1

    def _tone_filter(self, audio, tone_control):
        """
        Filtro passa-baixas (Low-pass) para o controlo de tonalidade.
        """
        # Apenas recalcula os coeficientes do filtro se o valor do "tone" mudar
        if tone_control != self.last_tone:
            # Mapeia o controlo de 0-10 para uma frequência de corte
            min_freq = 700
            max_freq = 12000
            cutoff_hz = min_freq * ((max_freq / min_freq) ** (tone_control / 10.0))

            if cutoff_hz >= max_freq - 100:
                self.lp_b, self.lp_a = None, None # Desativa o filtro
            else:
                nyq = 0.5 * self.sample_rate
                normal_cutoff = cutoff_hz / nyq
                self.lp_b, self.lp_a = butter(1, normal_cutoff, btype='low')
            self.last_tone = tone_control
        
        if self.lp_b is not None:
            return lfilter(self.lp_b, self.lp_a, audio)
        return audio

    def apply(self, audio_buffer, gain=5.0, tone=5.0, level=7.0):
        """
        Aplica a cadeia de processamento do Overdrive.
        """
        processed = audio_buffer.astype(np.float32)

        # 1. Pré-Filtro para "apertar" o som
        processed = lfilter(self.hp_b, self.hp_a, processed)

        # 2. Estágio de Ganho (Drive)
        drive_amount = 1.0 + (gain / 10.0) * 15.0
        processed = processed * drive_amount

        # 3. Soft Clipping com tanh para uma saturação suave
        processed = np.tanh(processed)

        # 4. Filtro de Tonalidade (Pós-distorção)
        processed = self._tone_filter(processed, tone)

        # 5. Nível de Saída (Volume)
        level_mult = 0.1 + (level / 10.0)
        processed = processed * level_mult

        return np.clip(processed, -1.0, 1.0).astype(np.float32)