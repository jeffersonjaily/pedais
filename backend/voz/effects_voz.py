import numpy as np

from backend.voz.PitchShift import PitchShift
from backend.voz.Reverb_voz import Reverb
from backend.voz.Vocal_Compressor import VocalCompressor
from backend.voz.Vocal_Delay import VocalDelay
from backend.voz.Vocal_equalizer import VocalEqualizer
from backend.voz.Vocal_Tremolo import VocalTremolo
from backend.voz.VocalDeesser import VocalDeesser

from backend.voz.PitchCorrection import PitchCorrection
from backend.effects.tuner import yin_detect_pitch, freq_to_note

class AudioProcessor:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.tuner_note = None

        # Instâncias dos efeitos
        self.pitch_shift = PitchShift(sample_rate)
        self.reverb = Reverb(sample_rate)
        self.compressor = VocalCompressor(sample_rate)
        self.delay = VocalDelay(sample_rate)
        self.equalizer = VocalEqualizer(sample_rate)
        self.tremolo = VocalTremolo(sample_rate)
        self.deesser = VocalDeesser(sample_rate)
        self.pitch_correction = PitchCorrection()

        # Estado dos efeitos e parâmetros (default)
        self.effects_state = {
            'pitch_shift': {'enabled': False, 'params': {'semitones': 0}},
            'pitch_correction': {'enabled': False, 'params': {'target_note': 'A4'}},
            'reverb': {'enabled': False, 'params': {'mix': 0.3, 'room_size': 0.5}},
            'compressor': {'enabled': False, 'params': {'threshold': -20, 'ratio': 4, 'attack': 10, 'release': 100}},
            'delay': {'enabled': False, 'params': {'delay_time_ms': 400, 'feedback': 0.5, 'mix': 0.3}},
            'equalizer': {'enabled': False, 'params': {'bands': []}},  # 'bands' deve ser lista de ganhos por banda
            'tremolo': {'enabled': False, 'params': {'rate': 5.0, 'depth': 0.5}},
            'deesser': {'enabled': False, 'params': {'threshold': 0.5, 'frequency': 6000}},
            'tuner': {'enabled': False, 'params': {}},
        }

    def update_params(self, new_state):
        """
        Atualiza estado e parâmetros dos efeitos.
        Mantém parâmetros já existentes e atualiza os recebidos.
        """
        for effect, state in new_state.items():
            if effect in self.effects_state:
                self.effects_state[effect]['enabled'] = state.get('enabled', False)
                # Atualiza apenas os parâmetros fornecidos, sem apagar os antigos
                params = state.get('params', {})
                self.effects_state[effect]['params'].update(params)

    def update_state(self, data):
        """
        Atualiza o estado de um efeito específico.
        """
        effect = data.get('effect')
        if effect in self.effects_state:
            self.effects_state[effect]['enabled'] = data.get('enabled', False)
            if 'params' in data:
                # Substitui os parâmetros completamente se fornecidos
                self.effects_state[effect]['params'] = data.get('params', {})

    def process_audio(self, buffer: np.ndarray) -> np.ndarray:
        """
        Processa o áudio aplicando os efeitos habilitados.
        """
        # Afinador: se ativo, analisa o buffer e retorna som mudo
        if self.effects_state.get('tuner', {}).get('enabled', False):
            self.get_tuner_data(buffer)
            return np.zeros_like(buffer)

        processed = buffer.copy()

        if self.effects_state['pitch_shift']['enabled']:
            semitones = self.effects_state['pitch_shift']['params'].get('semitones', 0)
            processed = self.pitch_shift.process(processed, semitones)

        if self.effects_state['pitch_correction']['enabled']:
            target_note = self.effects_state['pitch_correction']['params'].get('target_note', 'A4')
            processed = self.pitch_correction.process(processed, target_note)

        if self.effects_state['compressor']['enabled']:
            p = self.effects_state['compressor']['params']
            processed = self.compressor.process(
                processed,
                threshold=p.get('threshold', -20),
                ratio=p.get('ratio', 4),
                attack=p.get('attack', 10),
                release=p.get('release', 100),
            )

        if self.effects_state['delay']['enabled']:
            p = self.effects_state['delay']['params']
            processed = self.delay.process(
                processed,
                delay_time_ms=p.get('delay_time_ms', 400),
                feedback=p.get('feedback', 0.5),
                mix=p.get('mix', 0.3),
            )

        if self.effects_state['reverb']['enabled']:
            p = self.effects_state['reverb']['params']
            processed = self.reverb.process(
                processed,
                mix=p.get('mix', 0.3),
                room_size=p.get('room_size', 0.5)
            )

        if self.effects_state['equalizer']['enabled']:
            bands = self.effects_state['equalizer']['params'].get('bands', [])
            processed = self.equalizer.process(processed, bands)

        if self.effects_state['tremolo']['enabled']:
            p = self.effects_state['tremolo']['params']
            processed = self.tremolo.process(
                processed,
                rate=p.get('rate', 5.0),
                depth=p.get('depth', 0.5),
            )

        if self.effects_state['deesser']['enabled']:
            p = self.effects_state['deesser']['params']
            processed = self.deesser.process(
                processed,
                threshold=p.get('threshold', 0.5),
                frequency=p.get('frequency', 6000),
            )

        return processed

    def get_tuner_data(self, buffer: np.ndarray):
        freq = yin_detect_pitch(buffer, self.sample_rate)
        self.tuner_note = freq_to_note(freq)
        return self.tuner_note

    def get_last_tuner_note(self):
        return self.tuner_note
