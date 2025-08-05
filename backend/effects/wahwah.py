# backend/effects/wahwah.py
import numpy as np

class WahWah:
    """
    Simula um efeito auto-wah, que é um filtro ressonante (band-pass)
    cuja frequência central é varrida por um LFO (Oscilador de Baixa Frequência).
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.lfo_phase = 0.0
        # Estado do filtro (amostras anteriores de saída e entrada)
        self.y_n1 = 0.0
        self.y_n2 = 0.0
        self.x_n1 = 0.0
        self.x_n2 = 0.0

    def apply(self, audio_buffer, rate=1.5, min_freq=400.0, max_freq=2000.0, q=5.0, gain=1.5):
        """
        Aplica o efeito de auto-wah.

        Args:
            audio_buffer (np.array): O sinal de áudio.
            rate (float): A velocidade da varredura do LFO em Hz.
            min_freq (float): A frequência mais baixa da varredura.
            max_freq (float): A frequência mais alta da varredura.
            q (float): A ressonância ou "pico" do filtro.
            gain (float): Fator de ganho para aumentar o volume do sinal.
        """
        output_buffer = np.zeros_like(audio_buffer)
        
        # Gera a onda do LFO para todo o bloco, mapeada de 0 a 1
        time_steps = np.arange(len(audio_buffer)) / self.sample_rate
        lfo = (np.sin(2 * np.pi * rate * time_steps + self.lfo_phase) + 1) / 2.0
        
        # Atualiza a fase para o próximo bloco, garantindo continuidade
        self.lfo_phase = (self.lfo_phase + 2 * np.pi * rate * len(audio_buffer) / self.sample_rate) % (2 * np.pi)

        # Mapeia o LFO para a faixa de frequência desejada em uma escala logarítmica
        center_freqs = min_freq * ((max_freq / min_freq) ** lfo)

        # Loop sample-a-sample porque os coeficientes mudam a cada amostra
        for i in range(len(audio_buffer)):
            # Recalcula os coeficientes do filtro para a frequência atual
            w0 = 2 * np.pi * center_freqs[i] / self.sample_rate
            alpha = np.sin(w0) / (2 * q)

            b0 = alpha
            b1 = 0
            b2 = -alpha
            a0 = 1 + alpha
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha

            # Normaliza os coeficientes por a0
            b0, b1, b2 = b0/a0, b1/a0, b2/a0
            a1, a2 = a1/a0, a2/a0
            
            # Aplica a equação de diferença do filtro IIR
            x_n = audio_buffer[i]
            y_n = b0*x_n + b1*self.x_n1 + b2*self.x_n2 - a1*self.y_n1 - a2*self.y_n2
            
            output_buffer[i] = y_n
            
            # Atualiza o estado do filtro para a próxima amostra
            self.x_n2, self.x_n1 = self.x_n1, x_n
            self.y_n2, self.y_n1 = self.y_n1, y_n

        # Aplica o ganho e limita o sinal para evitar clipping
        output_buffer *= gain

        return np.clip(output_buffer, -1.0, 1.0).astype(np.float32)
