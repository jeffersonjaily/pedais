# backend/effects/distortion.py

import numpy as np

class Distortion:
    """
    Implementa um efeito de distorção mais agressivo usando "hard clipping".
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply(self, audio_buffer, drive=10.0, level=5.0):
        """
        Aplica o efeito de distorção.

        Args:
            audio_buffer (np.array): Sinal de áudio.
            drive (float): Nível de saturação, de 1 a 25.
            level (float): Volume de saída, de 0 a 10.
        """
        # Mapeia os controlos da UI para multiplicadores de ganho
        # A curva de 'drive' é exponencial para uma resposta mais drástica
        drive_gain = 1.0 + (drive ** 2) / 50.0
        level_gain = 0.1 + (level / 10.0) * 1.5

        # Aplica o ganho de entrada (drive)
        signal = audio_buffer * drive_gain

        # Aplica "hard clipping" para distorção
        # O sinal é cortado abruptamente nos umbrais -1.0 e 1.0
        clipped = np.clip(signal, -1.0, 1.0)
        
        # Aplica o volume de saída
        output = clipped * level_gain
        
        # Garante que a saída final não ultrapasse os limites
        return np.clip(output, -1.0, 1.0).astype(np.float32)