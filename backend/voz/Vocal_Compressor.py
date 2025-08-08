import numpy as np

class VocalCompressor:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

    def apply(self, audio_data: np.ndarray, threshold_db=-20, ratio=4.0,
              attack_ms=10, release_ms=200, level=1.0) -> np.ndarray:
        
        # Converte threshold de dB para linear
        threshold = 10 ** (threshold_db / 20)
        
        # Coeficientes para ataque e release
        attack_coeff = np.exp(-1.0 / (self.sample_rate * attack_ms / 1000))
        release_coeff = np.exp(-1.0 / (self.sample_rate * release_ms / 1000))
        
        envelope = 0.0
        gain_reduction = np.ones_like(audio_data, dtype=np.float32)
        
        for i in range(len(audio_data)):
            sample = abs(audio_data[i])
            
            # Atualiza envelope com ataque/release
            if sample > envelope:
                envelope = attack_coeff * (envelope - sample) + sample
            else:
                envelope = release_coeff * (envelope - sample) + sample
            
            if envelope > threshold:
                # Calcula ganho com compressão
                compressed_level = threshold + (envelope - threshold) / ratio
                gain_reduction[i] = threshold / compressed_level
            else:
                gain_reduction[i] = 1.0
        
        compressed = audio_data * gain_reduction * level
        return compressed.astype(np.float32)
