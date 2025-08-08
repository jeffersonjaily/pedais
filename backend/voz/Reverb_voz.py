# backend/voz/Reverb_voz.py

import numpy as np

class Reverb:
    """
    Implementa um reverb algorítmico de alta qualidade baseado no design
    clássico de Schroeder, com a adição de Early Reflections e Pre-Delay,
    tornando-o ideal para vocais.
    """
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        
        # --- Parâmetros dos Filtros (atrasos em segundos) ---
        self._comb_delays_sec = np.array([0.0297, 0.0371, 0.0411, 0.0437])
        self._allpass_delays_sec = np.array([0.005, 0.0017])
        self._allpass_gain = 0.7
        # --- Parâmetros para Early Reflections (atrasos em segundos) ---
        self._er_delays_sec = np.array([0.0043, 0.0215, 0.0225, 0.0268, 0.0270, 0.0298])
        self._er_gains = np.array([0.841, 0.504, 0.490, 0.379, 0.380, 0.346])

        # --- Buffers de Delay ---
        max_delay = int(max(self._comb_delays_sec) * 1.5 * self.sample_rate)
        self._comb_buffers = [np.zeros(max_delay) for _ in self._comb_delays_sec]
        self._allpass_buffers = [np.zeros(int(d * self.sample_rate)) for d in self._allpass_delays_sec]
        self._er_buffer = np.zeros(max_delay)
        
        # Ponteiros de escrita/leitura para os buffers
        self._comb_pos = [0] * len(self._comb_delays_sec)
        self._allpass_pos = [0] * len(self._allpass_delays_sec)
        self._er_pos = 0
        
        # Estado do filtro low-pass (para o controlo de 'decay')
        self._lp_state = 0.0

    def apply(self, audio_buffer: np.ndarray, mix=0.3, size=0.7, decay=0.5, predelay_ms=10.0) -> np.ndarray:
        """
        Aplica o efeito de reverb ao buffer de áudio.
        """
        output_buffer = np.zeros_like(audio_buffer)
        
        # Converte parâmetros da UI em valores de processamento
        feedback = 0.82 + (size * 0.15) # 'size' afeta a duração
        damping = decay * 0.4           # 'decay' afeta o brilho
        predelay_samples = int((predelay_ms / 1000.0) * self.sample_rate)

        # Processa o áudio amostra por amostra
        for i in range(len(audio_buffer)):
            # --- 1. Pré-Atraso (Pre-Delay) e Early Reflections ---
            input_sample = audio_buffer[i]
            
            # Escreve a amostra atual no buffer de early reflections
            self._er_buffer[self._er_pos] = input_sample
            
            # Calcula a posição de leitura do pré-atraso
            predelay_read_pos = (self._er_pos - predelay_samples + len(self._er_buffer)) % len(self._er_buffer)
            predelayed_sample = self._er_buffer[predelay_read_pos]

            # Calcula as Early Reflections a partir do sinal pré-atrasado
            early_reflections = 0.0
            for j in range(len(self._er_delays_sec)):
                delay_samps = int(self._er_delays_sec[j] * self.sample_rate * size)
                read_pos = (predelay_read_pos - delay_samps + len(self._er_buffer)) % len(self._er_buffer)
                early_reflections += self._er_buffer[read_pos] * self._er_gains[j]

            # Avança o ponteiro de escrita do buffer de ER
            self._er_pos = (self._er_pos + 1) % len(self._er_buffer)

            # --- 2. Cauda do Reverb (Algoritmo Schroeder) ---
            comb_output = 0.0
            # Filtros Comb em Paralelo
            for j in range(len(self._comb_buffers)):
                delay_len = int(self._comb_delays_sec[j] * self.sample_rate * size)
                delayed_sample = self._comb_buffers[j][self._comb_pos[j]]
                self._lp_state = delayed_sample * (1.0 - damping) + self._lp_state * damping
                self._comb_buffers[j][self._comb_pos[j]] = predelayed_sample + (self._lp_state * feedback)
                self._comb_pos[j] = (self._comb_pos[j] + 1) % delay_len
                comb_output += delayed_sample

            # Filtros All-Pass em Série
            allpass_output = comb_output
            for j in range(len(self._allpass_buffers)):
                buffer = self._allpass_buffers[j]
                pos = self._allpass_pos[j]
                delayed_sample = buffer[pos]
                buffer[pos] = allpass_output + (delayed_sample * self._allpass_gain)
                allpass_output = -allpass_output + delayed_sample
                self._allpass_pos[j] = (pos + 1) % len(buffer)

            # --- 3. Combina os Sinais ---
            # O sinal "wet" é uma mistura das primeiras reflexões e da cauda do reverb
            wet_signal = (early_reflections * 0.6) + (allpass_output * 0.4)
            output_buffer[i] = wet_signal

        # 4. Mixagem final
        final_output = (audio_buffer * (1 - mix)) + (output_buffer * mix)
        return np.clip(final_output, -1.0, 1.0).astype(np.float32)
