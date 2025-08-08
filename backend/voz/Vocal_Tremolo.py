import numpy as np

class VocalTremolo:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self._phase = 0.0  # Fase inicial em radianos

    def apply(self, audio_data: np.ndarray, rate=5.0, depth=0.8) -> np.ndarray:
        """
        Aplica efeito tremolo ao áudio.

        Parâmetros:
        - audio_data: np.ndarray (forma de onda do áudio)
        - rate: frequência da modulação em Hz (velocidade do tremolo)
        - depth: profundidade do efeito (0 = sem efeito, 1 = efeito máximo)

        Retorna:
        - np.ndarray com áudio modulado
        """

        n_samples = len(audio_data)
        t = np.arange(n_samples) / self.sample_rate

        # Modulação em seno variando de (1-depth) a (1+depth)
        # Corrigido para oscilar entre 1-depth e 1+depth para efeito mais natural
        modulation = 1.0 + depth * np.sin(2 * np.pi * rate * t + self._phase)

        # Atualiza a fase para a próxima chamada (continuidade)
        self._phase += 2 * np.pi * rate * n_samples / self.sample_rate
        self._phase = self._phase % (2 * np.pi)  # Mantém fase entre 0 e 2pi

        # Aplica modulação multiplicativa ao áudio
        output = audio_data * modulation

        # Normaliza para evitar clipping, mantendo dentro do range [-1,1]
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output = output / max_val

        return output.astype(np.float32)
