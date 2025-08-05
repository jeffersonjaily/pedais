import numpy as np

class VintageOverdrive:
    """
    Implementa um efeito de pedal de guitarra "Vintage Overdrive".
    Esta versão mantém a lógica de processamento original do autor,
    adaptada para ser compatível com o AudioEngine.
    """

    def __init__(self, sample_rate: int):
        """
        Inicializa o efeito de overdrive.
        """
        self.sample_rate = sample_rate

        # --- Parâmetros internos ---
        self.drive = 0.5
        self.tone = 0.6
        self.volume = .05 # Usando 'volume' internamente como no original

        # --- Variáveis internas do filtro de tonalidade ---
        self.tone_alpha = 0.0
        self.tone_y1 = 0.0
        
        self._update_tone_filter()

    def _update_tone_filter(self):
        """
        Recalcula o coeficiente do filtro de tonalidade (low-pass).
        """
        min_freq = 500
        max_freq = 12000
        cutoff_freq = min_freq + (self.tone ** 2) * (max_freq - min_freq)
        self.tone_alpha = np.exp(-2.0 * np.pi * cutoff_freq / self.sample_rate)
        
    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        """
        Processa um bloco de áudio, aplicando o efeito de overdrive.
        """
        # 1. ATUALIZA OS PARÂMETROS VINDO DA INTERFACE
        self.drive = params.get('drive', 6.0) / 10.0
        self.volume = params.get('level', 8.0) / 10.0
        new_tone_normalized = params.get('tone', 4.0) / 10.0
        self.tone = new_tone_normalized

        # Atualiza o filtro de forma otimizada, apenas se o 'tone' mudar
        new_tone = params.get('tone', self.tone)
        if new_tone != self.tone:
            self.tone = new_tone
            self._update_tone_filter()

        # 2. ETAPA: DRIVE (GANHO E SATURAÇÃO)
        drive_gain = 1.0 + self.drive * 49.0
        distorted_signal = np.tanh(input_buffer * drive_gain)
        
        # 3. ETAPA: TONE (FILTRAGEM USANDO O LOOP ORIGINAL)
        toned_signal = np.zeros_like(distorted_signal)
        y1 = self.tone_y1
        
        for i, sample in enumerate(distorted_signal):
            y0 = (1 - self.tone_alpha) * sample + self.tone_alpha * y1
            toned_signal[i] = y0
            y1 = y0
            
        self.tone_y1 = y1
        
        # 4. ETAPA: VOLUME
        output_signal = toned_signal * self.volume
        
        return np.clip(output_signal, -1.0, 1.0)