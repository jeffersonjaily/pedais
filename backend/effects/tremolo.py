# backend/effects/tremolo.py
import numpy as np

class Tremolo:
    """
    Cria o efeito de pulsação no volume (tremolo) através de modulação
    de amplitude com um LFO (Oscilador de Baixa Frequência).
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # A fase do LFO precisa ser mantida entre os blocos de áudio para evitar "saltos"
        self.lfo_phase = 0.0

    def apply(self, audio_buffer, rate=5.0, depth=0.8):
        """
        Aplica o efeito de tremolo.

        Args:
            audio_buffer (np.array): O sinal de áudio.
            rate (float): A velocidade da pulsação em Hz.
            depth (float): A profundidade do efeito (0 a 1). 0 = sem efeito, 1 = silêncio total no ponto baixo.
        """
        # Cria um vetor de tempo para a duração do buffer atual
        time_steps = np.arange(len(audio_buffer)) / self.sample_rate
        
        # Gera a onda do LFO (senoide), continuando a partir da fase do último bloco
        lfo = np.sin(2 * np.pi * rate * time_steps + self.lfo_phase)
        
        # Atualiza a fase para o próximo bloco de áudio, garantindo uma modulação contínua
        self.lfo_phase = (self.lfo_phase + 2 * np.pi * rate * len(audio_buffer) / self.sample_rate) % (2 * np.pi)
        
        # Mapeia a onda do LFO (que vai de -1 a 1) para a faixa de modulação de amplitude (de 1-depth a 1)
        # Quando o LFO está em -1, o multiplicador é (1-depth). Quando está em 1, o multiplicador é 1.
        mod_wave = 1 - depth * (lfo + 1) / 2.0
        
        # Aplica a modulação multiplicando o áudio original pela onda do LFO
        output = audio_buffer * mod_wave
        
        return output.astype(np.float32)