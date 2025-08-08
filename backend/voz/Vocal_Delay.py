import numpy as np

class VocalDelay:
    """
    Efeito de Delay Digital para voz (fala ou canto), com suporte a múltiplas repetições,
    cauda perceptível e realismo de ambiência.

    Parâmetros:
    - sample_rate: Taxa de amostragem (padrão: 48000 Hz)
    """

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self._delay_buffer = None
        self._write_index = 0

    def apply(self, audio_data: np.ndarray, time_ms=300, feedback=0.4, mix=0.3) -> np.ndarray:
        """
        Aplica delay vocal com cauda e repetições perceptíveis.

        Parâmetros:
        - audio_data: np.ndarray mono com valores em [-1.0, 1.0]
        - time_ms: tempo de atraso em milissegundos
        - feedback: quantidade de sinal atrasado que volta ao buffer
        - mix: mistura entre sinal limpo e sinal com delay

        Retorna:
        - np.ndarray processado com delay
        """
        if audio_data.ndim != 1:
            raise ValueError("O áudio deve ser mono (1D).")

        delay_samples = max(1, int(self.sample_rate * time_ms / 1000))

        if self._delay_buffer is None or len(self._delay_buffer) != delay_samples:
            self._delay_buffer = np.zeros(delay_samples, dtype=np.float32)
            self._write_index = 0  # reinicia o índice de escrita

        output = np.zeros_like(audio_data, dtype=np.float32)

        for i in range(len(audio_data)):
            delayed_sample = self._delay_buffer[self._write_index]
            dry = audio_data[i]
            wet = delayed_sample

            # Combina os sinais
            output[i] = (1 - mix) * dry + mix * wet

            # Atualiza o buffer com feedback
            self._delay_buffer[self._write_index] = dry + wet * feedback

            # Avança circularmente no buffer
            self._write_index = (self._write_index + 1) % delay_samples

        # Normaliza se ultrapassar os limites
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output /= max_val

        return output.astype(np.float32)
