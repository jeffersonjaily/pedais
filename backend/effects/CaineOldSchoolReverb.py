# Arquivo: python_effects.py

import numpy as np
from scipy.signal import butter, lfilter

class CaineOldSchoolReverb:
    # A classe avançada que gerencia a cauda do reverb
    def __init__(self, sample_rate: int, block_size: int):
        self.sample_rate = sample_rate
        self.block_size = block_size # Armazena o tamanho do bloco
        
        self._mode, self._decay, self._mix, self._tone = "room", 0.7, 0.5, 0.5
        self._ir, self._ir_dirty = None, True
        
        # O buffer da cauda agora usa o block_size correto
        self._tail_buffer = np.zeros(block_size, dtype=np.float32)

    def _generate_impulse_response(self) -> np.ndarray:
        # Este método continua o mesmo, já compatível com sua config
        decay_time = self._map_range(self._decay, 0.1, 1.5, 0.3, 3.0)
        length = int(self.sample_rate * decay_time)
        noise = np.random.normal(0, 1, length)
        t = np.linspace(0, decay_time, length)
        
        if self._mode == "hall": envelope = np.exp(-2.5 * t)
        elif self._mode == "church": envelope = np.exp(-1.5 * t)
        else: envelope = np.exp(-4 * t)
        
        ir = noise * envelope
        cutoff_freq = self._map_range(self._tone, 0, 1, 800, 7000)
        
        if cutoff_freq < self.sample_rate / 2 - 1:
            b, a = butter(4, cutoff_freq, btype='low', fs=self.sample_rate)
            ir = lfilter(b, a, ir)
        
        ir /= np.max(np.abs(ir)) + 1e-9
        return ir

    def apply(self, input_buffer: np.ndarray, **params) -> np.ndarray:
        # Atualiza parâmetros e a flag (lógica já existente)
        if (params.get("mode", self._mode) != self._mode or
            params.get("decay", self._decay) != self._decay or
            params.get("tone", self._tone) != self._tone):
            self._ir_dirty = True
        
        self._decay = params.get("decay", self._decay)
        self._mix = params.get("mix", self._mix)
        self._tone = params.get("tone", self._tone)
        self._mode = params.get("mode", self._mode)

        if self._ir_dirty or self._ir is None:
            self._ir = self._generate_impulse_response()
            self._ir_dirty = False
            self._tail_buffer.fill(0)
            
        full_wet_signal = np.convolve(input_buffer, self._ir, mode="full")
        current_wet_block = full_wet_signal[:self.block_size] + self._tail_buffer
        
        new_tail = full_wet_signal[self.block_size:]
        if len(new_tail) >= self.block_size:
            self._tail_buffer = new_tail[:self.block_size]
        else:
            self._tail_buffer.fill(0)
            self._tail_buffer[:len(new_tail)] = new_tail
        
        output = (1 - self._mix) * input_buffer + self._mix * current_wet_block
        return np.clip(output, -1.0, 1.0)

    def _map_range(self, value, from_min, from_max, to_min, to_max):
        if (from_max - from_min) == 0: return to_min
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

# --- FIM DA CLASSE ---

# Dicionário para guardar a instância única do nosso Reverb
effect_instances = {
    # AJUSTE AQUI: Precisamos criar a classe com o block_size.
    # Coloque aqui o mesmo valor de block_size que você usa na sua interface de áudio.
    # 512 é um valor comum.
    'caine_reverb_instance': CaineOldSchoolReverb(sample_rate=48000, block_size=512)
}

# --- FUNÇÃO WRAPPER ---
# AJUSTE AQUI: A função agora precisa receber o block_size para passar para a classe.
def apply_caine_old_school_reverb(audio_buffer: np.ndarray, sample_rate: int, block_size: int, **params) -> np.ndarray:
    reverb_instance = effect_instances['caine_reverb_instance']
    
    # Atualiza o sample_rate e o block_size se eles mudarem
    if reverb_instance.sample_rate != sample_rate:
        reverb_instance.sample_rate = sample_rate
        reverb_instance._ir_dirty = True
    if reverb_instance.block_size != block_size:
        reverb_instance.block_size = block_size
        reverb_instance._tail_buffer = np.zeros(block_size, dtype=np.float32)

    return reverb_instance.apply(audio_buffer, **params)