import numpy as np
from scipy.signal import butter, lfilter

class DeEsser:
    """
    Suaviza sibilância (sons 'S', 'SH', 'Z') com detecção de energia em alta frequência
    e redução dinâmica via compressão leve e otimizada para arrays NumPy.
    """

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

    def apply(self, audio_data: np.ndarray, frequency=6000, threshold_db=-25, reduction=0.6) -> np.ndarray:
        # 1. Conversão do Threshold de dB para amplitude linear
        threshold_linear = 10**(threshold_db / 20)
        
        # 2. Definição do filtro bandpass (passa-banda) para a sibilância
        nyquist = 0.5 * self.sample_rate
        low = frequency / nyquist
        high = 12000 / nyquist
        
        b_bp, a_bp = butter(4, [low, high], btype='bandpass')
        sibilance_band = lfilter(b_bp, a_bp, audio_data)

        # 3. Detecção de energia da sibilância (envelope)
        envelope = np.abs(sibilance_band)
        
        # 4. Cálculo do ganho de redução dinâmico
        # A redução só acontece quando o envelope ultrapassa o threshold
        gain_reduction = np.ones_like(audio_data)  # Começa com ganho 1 (sem alteração)
        
        # Encontra os índices onde a sibilância está acima do threshold
        over_threshold_indices = envelope > threshold_linear
        
        if np.any(over_threshold_indices):
            # Calcula a atenuação apenas para as partes que ultrapassaram o threshold
            excess_sibilance = envelope[over_threshold_indices] - threshold_linear
            
            # ATENÇÃO: Correção do erro de divisão por zero!
            # np.divide realiza a operação e retorna 0 se o divisor for 0
            safe_division = np.divide(excess_sibilance, envelope[over_threshold_indices], 
                                      out=np.zeros_like(excess_sibilance), where=envelope[over_threshold_indices]!=0)
            
            # Calcula o ganho de atenuação, que vai de 0 a 1
            gain = 1 - (safe_division * reduction)
            
            # Aplica o ganho dinâmico nos índices corretos
            gain_reduction[over_threshold_indices] = gain

        # 5. Aplicação do ganho de redução na banda de sibilância e mistura
        # Multiplica o sinal original pelo ganho de redução, atenuando a sibilância
        output = audio_data * gain_reduction

        return output.astype(np.float32)