# backend/effects/chorus.py
import numpy as np
from scipy.signal import lfilter, butter

class ChorusEffect:
    """
    Implementa um efeito de Chorus e Tri-Chorus com LFO de fase contínua
    para uma modulação suave e profissional.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # MUDANÇA: Armazena a fase de cada LFO para garantir continuidade.
        # Para o Tri-Chorus, as fases iniciam deslocadas em 120 graus (2*pi/3).
        self.lfo_phases = [0.0, 2 * np.pi / 3, 4 * np.pi / 3]

    def _generate_lfos(self, num_samples, rate, num_lfos=1):
        """
        Gera as ondas do LFO, continuando a partir da fase anterior.
        """
        lfos = []
        # Gera o vetor de tempo apenas uma vez
        time_steps = np.arange(num_samples) / self.sample_rate
        
        for i in range(num_lfos):
            phase = self.lfo_phases[i]
            # Gera a onda senoidal para o bloco atual
            lfo = np.sin(2 * np.pi * rate * time_steps + phase)
            lfos.append(lfo)
            
            # MUDANÇA: Atualiza a fase para o início do próximo bloco de áudio
            end_phase = phase + 2 * np.pi * rate * num_samples / self.sample_rate
            self.lfo_phases[i] = end_phase % (2 * np.pi)
            
        return lfos

    def apply(self, audio_data, mode='chorus', rate=2.0, width=0.003, intensity=0.7, tone=5.0):
        """
        Aplica o efeito de chorus ao bloco de áudio.
        """
        delay_center_s = 0.015  # Atraso médio em segundos
        lfo_amp = width / 2.0     # Amplitude da modulação do LFO

        # MUDANÇA: Gera os LFOs usando a nova função com fase contínua
        num_lfos_to_gen = 3 if mode == 'tri-chorus' else 1
        lfos = self._generate_lfos(audio_data.shape[0], rate, num_lfos_to_gen)

        wet_signals = []
        for lfo in lfos:
            # Modula o tempo de delay usando o LFO
            delay_samples = (delay_center_s + lfo * lfo_amp) * self.sample_rate
            
            # Interpolação linear para ler o sinal em posições não-inteiras (evita "cliques")
            indices = np.arange(audio_data.shape[0]) - delay_samples
            indices_floor = np.floor(indices).astype(int)
            frac = indices - indices_floor
            
            # Garante que os índices não saiam dos limites do array
            indices_floor = np.clip(indices_floor, 0, audio_data.shape[0] - 1)
            indices_ceil = np.clip(indices_floor + 1, 0, audio_data.shape[0] - 1)

            delayed_signal = (audio_data[indices_floor] * (1 - frac) + audio_data[indices_ceil] * frac)
            wet_signals.append(delayed_signal)

        # Combina os sinais "molhados" (para Tri-Chorus, faz a média dos três)
        wet_signal_combined = np.mean(np.array(wet_signals), axis=0)

        # Aplica o filtro de Tonalidade no sinal com efeito
        if tone < 9.9:
            cutoff_hz = 800 + (tone / 10.0) * 14200
            nyq = 0.5 * self.sample_rate
            normal_cutoff = cutoff_hz / nyq
            b, a = butter(1, normal_cutoff, btype='low', analog=False)
            wet_signal_toned = lfilter(b, a, wet_signal_combined)
        else:
            wet_signal_toned = wet_signal_combined

        # Mixa o sinal original (dry) com o sinal processado (wet)
        output_audio = (audio_data * (1 - intensity)) + (wet_signal_toned * intensity)
        
        # MUDANÇA: Garante que a saída não tenha distorção digital
        return np.clip(output_audio, -1.0, 1.0).astype(np.float32)

# MUDANÇA: Removida a instância global. A criação do objeto deve ser feita
# no seu 'audio_interface.py' para manter o código modular.