# backend/effects/delay.py
import numpy as np

class Delay:
    """
    Implementa um efeito de delay digital com um buffer de memória circular
    e controle de feedback para criar repetições.
    """
    def __init__(self, sample_rate=44100, max_delay_s=2.0):
        self.sample_rate = sample_rate
        # Cria um buffer grande o suficiente para o delay máximo
        buffer_size = int(max_delay_s * sample_rate)
        self.delay_buffer = np.zeros(buffer_size, dtype=np.float32)
        # Ponteiro que indica onde escrever a próxima amostra no buffer
        self.write_pos = 0

    def apply(self, audio_buffer, time_ms=300.0, feedback=0.4, mix=0.3):
        """
        Aplica o efeito de delay ao bloco de áudio.

        Args:
            audio_buffer (np.array): O sinal de áudio de entrada.
            time_ms (float): O tempo de atraso em milissegundos.
            feedback (float): A quantidade de repetições (0 a 0.95).
            mix (float): A mistura entre o som original e o som com efeito (0 a 1).
        """
        output_buffer = np.zeros_like(audio_buffer)
        
        # Converte o tempo de delay de milissegundos para amostras
        delay_samples = int((time_ms / 1000.0) * self.sample_rate)
        
        # Garante que o delay não seja maior que o buffer disponível
        if delay_samples >= len(self.delay_buffer):
            delay_samples = len(self.delay_buffer) - 1

        # Processa o áudio amostra por amostra
        for i in range(len(audio_buffer)):
            # Calcula a posição de leitura no buffer circular
            read_pos = (self.write_pos - delay_samples + len(self.delay_buffer)) % len(self.delay_buffer)
            
            # Pega o áudio atrasado do buffer
            delayed_sample = self.delay_buffer[read_pos]
            
            # Mixa o sinal original (dry) com o sinal com efeito (wet)
            output_sample = (audio_buffer[i] * (1 - mix)) + (delayed_sample * mix)
            
            # Escreve o som atual no buffer, somado ao feedback do som atrasado
            # para criar as repetições. O feedback é limitado para evitar auto-oscilação.
            self.delay_buffer[self.write_pos] = np.clip(audio_buffer[i] + (delayed_sample * feedback), -1.0, 1.0)
            
            # Armazena a amostra de saída
            output_buffer[i] = output_sample

            # Avança o ponteiro de escrita para a próxima posição
            self.write_pos = (self.write_pos + 1) % len(self.delay_buffer)
            
        return np.clip(output_buffer, -1.0, 1.0).astype(np.float32)