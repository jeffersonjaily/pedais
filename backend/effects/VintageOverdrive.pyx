# Nome do arquivo: vintage_overdrive_cython.pyx

import numpy as np
# Importa as definições de tipo do Cython para o NumPy
cimport numpy as np
# Importa o decorador 'boundscheck' para otimização extra
cimport cython

# --- DEFINIÇÃO DA CLASSE COM TIPOS (CYTHON) ---
# 'cdef class' cria uma classe C otimizada
cdef class VintageOverdriveCython:
    # --- DECLARAÇÃO DE ATRIBUTOS COM TIPOS C ---
    # 'cdef' declara variáveis C que são muito mais rápidas que as do Python
    cdef public float sample_rate, drive, tone, volume, tone_alpha, tone_y1
    
    def __init__(self, float sample_rate):
        """
        Inicializa o efeito de overdrive com tipos definidos.
        """
        self.sample_rate = sample_rate
        self.drive = 0.5
        self.tone = 0.6
        self.volume = 0.5
        self.tone_y1 = 0.0
        self._update_tone_filter()

    # 'cdef' para um método interno otimizado
    cdef void _update_tone_filter(self):
        """
        Recalcula o coeficiente do filtro. A matemática é a mesma,
        mas agora executa em velocidade de C.
        """
        cdef float min_freq = 500.0
        cdef float max_freq = 12000.0
        cdef float cutoff_freq = min_freq + (self.tone ** 2) * (max_freq - min_freq)
        self.tone_alpha = np.exp(-2.0 * np.pi * cutoff_freq / self.sample_rate)
        
    # --- O CORAÇÃO DA OTIMIZAÇÃO ---
    # Este método é o que será chamado pelo seu audio_interface.py
    # Decoradores para máxima performance: desliga checagens de segurança do Python
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def apply(self, np.ndarray[np.float32_t, ndim=1] input_buffer, **params):
        """
        Processa o áudio. Este método inteiro é compilado para C.
        """
        # 1. ATUALIZA OS PARÂMETROS
        # A lógica de atualização permanece em Python para flexibilidade
        self.drive = params.get('drive', 6.0) / 10.0
        self.volume = params.get('level', 8.0) / 10.0
        new_tone_normalized = params.get('tone', 4.0) / 10.0
        
        if new_tone_normalized != self.tone:
            self.tone = new_tone_normalized
            self._update_tone_filter()

        # 2. ETAPA: DRIVE (GANHO E SATURAÇÃO)
        # As operações do NumPy já são rápidas, então as mantemos
        cdef float drive_gain = 1.0 + self.drive * 49.0
        # O tipo do array é definido na assinatura do método
        cdef np.ndarray[np.float32_t, ndim=1] distorted_signal = np.tanh(input_buffer * drive_gain)
        
        # 3. ETAPA: TONE (FILTRAGEM) - O LOOP OTIMIZADO
        cdef int n_samples = distorted_signal.shape[0]
        cdef np.ndarray[np.float32_t, ndim=1] toned_signal = np.zeros(n_samples, dtype=np.float32)
        
        # Declaração de variáveis C locais para o loop
        cdef int i
        cdef float sample, y0
        # Copia os atributos da classe para variáveis locais C, o que é mais rápido dentro de um loop
        cdef float local_alpha = self.tone_alpha
        cdef float local_y1 = self.tone_y1
        
        # Este loop agora executa em velocidade nativa de C, sem a sobrecarga do Python
        for i in range(n_samples):
            sample = distorted_signal[i]
            y0 = (1 - local_alpha) * sample + local_alpha * local_y1
            toned_signal[i] = y0
            local_y1 = y0
            
        # Atualiza o estado do filtro na classe
        self.tone_y1 = local_y1
        
        # 4. ETAPA: VOLUME
        cdef np.ndarray[np.float32_t, ndim=1] output_signal = toned_signal * self.volume
        
        # O clipping do NumPy também é rápido
        return np.clip(output_signal, -1.0, 1.0)
