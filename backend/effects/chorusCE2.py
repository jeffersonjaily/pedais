import numpy as np

class CE2ChorusEffect:
    """    Classe que implementa o efeito Chorus CE-2.
    Simula um efeito de chorus inspirado no clássico BOSS CE-2.
    Refatorado para integração com um AudioEngine e com LFO contínuo.
    """
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate

        # --- Parâmetros internos (controlados via método 'apply') ---
        self.rate = 1.5      # Frequência do LFO em Hz
        self.depth = 0.75    # Profundidade da modulação (0 a 1)
        self.level = 1.0     # Volume de saída

        # --- Configurações da Linha de Delay ---
        self.min_delay_ms = 1.0  # Delay mínimo para o sweep
        self.max_delay_ms = 7.0  # Delay máximo para o sweep
        
        buffer_size_samples = int(self.max_delay_ms / 1000 * self.sample_rate) + 2
        self.delay_buffer = np.zeros(buffer_size_samples)
        self.buffer_index = 0
        
        # --- Estado contínuo do LFO ---
        self.lfo_phase = 0.0

    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        """
        Processa um bloco de áudio, aplicando o efeito Chorus.
        """
        # 1. ATUALIZA OS PARÂMETROS VINDO DA INTERFACE
        self.rate = params.get('rate', self.rate)
        self.depth = params.get('depth', self.depth)
        self.level = params.get('level', self.level) # Pega o novo parâmetro de volume

        output_buffer = np.zeros_like(input_buffer)
        
        # Incremento de fase do LFO por amostra, para um sweep contínuo
        lfo_inc = 2 * np.pi * self.rate / self.sample_rate

        for i, sample in enumerate(input_buffer):
            # 2. CALCULAR O TEMPO DE DELAY MODULADO PELO LFO
            # O LFO agora é contínuo entre os blocos de áudio
            lfo_value = (np.sin(self.lfo_phase) + 1) / 2 # Mapeia o seno de [-1, 1] para [0, 1]
            self.lfo_phase = (self.lfo_phase + lfo_inc) % (2 * np.pi)

            # A profundidade (depth) controla a intensidade da variação do LFO
            sweep_range_ms = (self.max_delay_ms - self.min_delay_ms) * self.depth
            current_delay_ms = self.min_delay_ms + lfo_value * sweep_range_ms
            delay_samples = current_delay_ms / 1000.0 * self.sample_rate

            # 3. LER DA LINHA DE DELAY COM INTERPOLAÇÃO LINEAR
            read_pos = self.buffer_index - delay_samples
            read_pos_int = int(read_pos)
            frac = read_pos - read_pos_int
            
            read_pos1 = read_pos_int % self.delay_buffer.size
            read_pos2 = (read_pos_int + 1) % self.delay_buffer.size
            
            delayed_sample = (1 - frac) * self.delay_buffer[read_pos1] + frac * self.delay_buffer[read_pos2]
            
            # 4. MISTURAR SINAL ORIGINAL (DRY) COM O ATRASADO (WET)
            # Mistura 50/50, um som clássico de chorus
            output_buffer[i] = 0.5 * sample + 0.5 * delayed_sample
            
            # 5. ATUALIZAR O BUFFER DE DELAY
            self.delay_buffer[self.buffer_index] = sample
            self.buffer_index = (self.buffer_index + 1) % self.delay_buffer.size
        
        # 6. APLICAR VOLUME FINAL E GARANTIR QUE NÃO VAI CLIPAR
        final_output = output_buffer * self.level
        return np.clip(final_output, -1.0, 1.0)