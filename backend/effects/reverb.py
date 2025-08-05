# backend/effects/reverb.py
import numpy as np
from scipy.signal import lfilter

class Reverb:
    """
    Implementa um reverb simples e eficaz (baseado no algoritmo de Gardner) 
    usando filtros all-pass e um loop de feedback para criar a sensação de espaço.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Parâmetros internos do algoritmo, podem ser ajustados
        self.allpass_delays = [int(d * sample_rate) for d in [0.0047, 0.0036, 0.0127, 0.0093]]
        self.allpass_gains = [0.7, 0.7, 0.7, 0.7]
        self.feedback_delay_len = int(0.07 * sample_rate) # Tamanho do delay principal
        self.feedback_buffer = np.zeros(self.feedback_delay_len)
        self.feedback_pos = 0
        self.lp_filter_state = 0.0 # Estado do filtro low-pass

    def _allpass_filter(self, audio, delay, gain):
        """Filtro All-pass simples para criar difusão."""
        if delay <= 0:
            return audio
        b = np.zeros(delay + 1)
        b[0], b[delay] = -gain, 1
        a = np.zeros(delay + 1)
        a[0], a[delay] = 1, -gain
        return lfilter(b, a, audio)
    
    def apply(self, audio_buffer, mix=0.3, size=0.7, decay=0.5):
        """
        Aplica o efeito de reverb.

        Args:
            audio_buffer (np.array): O sinal de áudio.
            mix (float): A mistura entre o som original e o com efeito.
            size (float): O "tamanho" da sala, afetando o tempo das reflexões.
            decay (float): O decaimento do reverb, controlando a duração da cauda.
        """
        # Cria cópias dos sinais
        dry_signal = audio_buffer
        wet_signal = audio_buffer.copy()
        
        # 1. Early reflections (difusão) com filtros all-pass
        for i in range(len(self.allpass_delays)):
            delay = int(self.allpass_delays[i] * (0.5 + size * 0.5)) # 'Size' afeta o delay
            wet_signal = self._allpass_filter(wet_signal, delay, self.allpass_gains[i])

        # 2. Reverb tail (cauda) com loop de feedback e filtro low-pass
        output_buffer = np.zeros_like(wet_signal)
        for i in range(len(wet_signal)):
            # Pega a amostra do fim do buffer de feedback
            delayed_sample = self.feedback_buffer[self.feedback_pos]
            
            # Filtro Low-pass simples para simular absorção do som (escurece as repetições)
            self.lp_filter_state = delayed_sample * (1.0 - decay) + self.lp_filter_state * decay
            
            # Soma o som atual com o feedback filtrado
            input_feedback = wet_signal[i] + self.lp_filter_state
            
            # Escreve no buffer de feedback
            self.feedback_buffer[self.feedback_pos] = np.clip(input_feedback, -1.0, 1.0)
            
            # Avança o ponteiro
            self.feedback_pos = (self.feedback_pos + 1) % self.feedback_delay_len
            
            output_buffer[i] = delayed_sample

        # 3. Mixagem final
        final_output = (dry_signal * (1 - mix)) + (output_buffer * mix)
        return np.clip(final_output, -1.0, 1.0).astype(np.float32)