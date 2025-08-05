# backend/effects/PureSky.py
import numpy as np
from scipy.signal import lfilter, lfilter_zi

class PureSky:
    """
    Simula um pedal de overdrive transparente, inspirado no "Pure Sky" / "Timmy".
    Caracterizado por um drive suave e controles de equalização que cortam frequências.
    """
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate

        # --- Parâmetros internos ---
        self.gain = 0.3
        self.level = 0.7
        self.bass = 0.0 # 0 = sem corte, 1 = corte máximo
        self.treble = 0.0 # 0 = sem corte, 1 = corte máximo

        # --- Filtros de Tonalidade (inicialização) ---
        # Bass (High-pass) e Treble (Low-pass)
        self.bass_b, self.bass_a = np.array([1.0]), np.array([1.0, 0.0])
        self.treble_b, self.treble_a = np.array([1.0]), np.array([1.0, 0.0])
        self.bass_zi, self.treble_zi = np.array([0.0]), np.array([0.0])

        self._update_filters()

    def _update_filters(self):
        """ Recalcula os coeficientes dos filtros de Bass e Treble. """
        # BASS (High-pass filter - corta graves)
        # Frequência de corte varia de ~20Hz (sem corte) a ~700Hz (corte máximo)
        bass_cutoff = 20 + (self.bass ** 1.5) * 680
        alpha_b = np.exp(-2.0 * np.pi * bass_cutoff / self.sample_rate)
        self.bass_b = np.array([ (1 + alpha_b) / 2, -(1 + alpha_b) / 2 ])
        self.bass_a = np.array([ 1, -alpha_b ])

        # TREBLE (Low-pass filter - corta agudos)
        # Frequência de corte varia de ~20kHz (sem corte) a ~1.5kHz (corte máximo)
        treble_cutoff = 20000 - (self.treble ** 1.5) * 18500
        alpha_t = np.exp(-2.0 * np.pi * treble_cutoff / self.sample_rate)
        self.treble_b = np.array([1 - alpha_t])
        self.treble_a = np.array([1, -alpha_t])
        
        # ZI (estado do filtro) precisa ser recalculado se os coefs mudam
        self.bass_zi = self.bass_zi * lfilter_zi(self.bass_b, self.bass_a)
        self.treble_zi = self.treble_zi * lfilter_zi(self.treble_b, self.treble_a)

    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        # 1. Atualiza parâmetros
        self.gain = params.get('gain', self.gain)
        self.level = params.get('level', self.level)
        
        # Atualiza filtros apenas se necessário
        new_bass = params.get('bass', self.bass)
        new_treble = params.get('treble', self.treble)
        if new_bass != self.bass or new_treble != self.treble:
            self.bass = new_bass
            self.treble = new_treble
            self._update_filters()
        
        # 2. Estágio de Ganho (Drive)
        drive_gain = 1.0 + self.gain * 20.0 # Ganho mais sutil
        driven_signal = np.tanh(input_buffer * drive_gain)
        
        # 3. Estágio de Tonalidade (filtros otimizados)
        bass_cut_signal, self.bass_zi = lfilter(self.bass_b, self.bass_a, driven_signal, zi=self.bass_zi)
        toned_signal, self.treble_zi = lfilter(self.treble_b, self.treble_a, bass_cut_signal, zi=self.treble_zi)

        # 4. Estágio de Volume (Level)
        output_signal = toned_signal * self.level * 1.5 # Um pequeno boost geral
        
        return np.clip(output_signal, -1.0, 1.0)