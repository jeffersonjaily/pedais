# backend/effects/fuzz.py
import numpy as np

class Fuzz:
    """
    Implementa um efeito de Fuzz clássico, caracterizado por uma distorção
    extrema que transforma a onda sonora em algo próximo de uma onda quadrada.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply(self, audio_buffer, gain=15.0, mix=1.0):
        """
        Aplica o efeito de Fuzz.

        Args:
            audio_buffer (np.array): O sinal de áudio.
            gain (float): A intensidade do efeito. Valores altos criam mais sustentação e compressão.
            mix (float): A mistura entre o som original (dry) e o com Fuzz (wet).
        """
        # Sinal original para a mixagem
        dry_signal = audio_buffer.copy()
        
        # Aplica um ganho extremo para saturar o sinal
        signal = audio_buffer * gain
        
        # "Hard clipping": corta o sinal abruptamente nos limites -1 e 1.
        # Esta é a principal fonte do som "quadrado" do Fuzz.
        clipped_signal = np.clip(signal, -1.0, 1.0)
        
        # Mixa o sinal original com o sinal processado
        wet_signal = clipped_signal
        output_signal = (dry_signal * (1 - mix)) + (wet_signal * mix)

        return np.clip(output_signal, -1.0, 1.0).astype(np.float32)