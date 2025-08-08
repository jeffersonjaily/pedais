import numpy as np
import soundfile as sf
from backend.effects.overdrive import Overdrive
from backend.effects.distortion import Distortion
from backend.effects.fuzz import Fuzz
from backend.effects.chorus import ChorusEffect
from backend.effects.delay import Delay
from backend.effects.reverb import Reverb
from backend.effects.tremolo import Tremolo
from backend.effects.wahwah import WahWah
from backend.effects.equalizer import Equalizer
from backend.effects.compressor_guitarra import CompressorEffect
from backend.effects.VintageOverdrive import VintageOverdrive
from backend.effects.CarmillaDistortion import CarmillaDistortionEffect
from backend.effects.chorusCE2 import CE2ChorusEffect
from backend.effects.BOSS_BF_2_Flanger import BossBf2Flanger
from backend.effects.Ultra_Flanger_UF100 import BehringerUf100Flanger
from backend.effects.PureSky import PureSky
from backend.effects.Afinador import BossTU3Tuner
from backend.effects.CaineOldSchoolReverb import CaineOldSchoolReverb

from backend.voz.Vocal_Compressor import VocalCompressor
from backend.voz.VocalDeesser import DeEsser
from backend.voz.Vocal_equalizer import VocalEqualizer
from backend.voz.Vocal_Delay import VocalDelay
from backend.voz.Reverb_voz import Reverb as VocalReverb
from backend.voz.PitchShift import PitchShift
from backend.voz.PitchCorrection import PitchCorrection
from backend.voz.Vocal_Tremolo import VocalTremolo
from backend.voz.PopClickSuppressor import PopClickSuppressor
from backend.effects.tuner import yin_detect_pitch, freq_to_note

class AudioProcessor:
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.master_volume = 1.0

        self.backing_track_data = None
        self.playback_position = 0
        self.backing_track_volume = 0.7
        self.playback_state = 'stopped'
        
        self.tuner_note = None

        self.channel_mapping = {
            'instrument': 0,
            'voice': 1
        }
        
        self.input_enabled = {
            'instrument': True,
            'voice': True
        }

        self.effects = {
            'instrument': {
                'overdrive': Overdrive(self.sample_rate), 'distortion': Distortion(self.sample_rate), 'fuzz': Fuzz(self.sample_rate), 'wahwah': WahWah(self.sample_rate), 'equalizer': Equalizer(self.sample_rate), 'chorus': ChorusEffect(self.sample_rate), 'tremolo': Tremolo(self.sample_rate), 'delay': Delay(self.sample_rate), 'reverb': Reverb(self.sample_rate), 'puresky': PureSky(self.sample_rate), 'afinador': BossTU3Tuner(sample_rate=self.sample_rate), 'compressor': CompressorEffect(self.sample_rate), 'vintage_overdrive': VintageOverdrive(self.sample_rate), 'carmilla_distortion': CarmillaDistortionEffect(self.sample_rate), 'chorus_ce2': CE2ChorusEffect(self.sample_rate), 'boss_bf2_flanger': BossBf2Flanger(self.sample_rate), 'ultra_flanger': BehringerUf100Flanger(self.sample_rate), 'CaineOldSchoolReverb': CaineOldSchoolReverb(self.sample_rate, self.block_size)
            },
            'voice': {
                'vocal_compressor': VocalCompressor(self.sample_rate), 'pop_click_suppressor': PopClickSuppressor(self.sample_rate), 'deesser': DeEsser(self.sample_rate), 'vocal_equalizer': VocalEqualizer(self.sample_rate), 'vocal_delay': VocalDelay(self.sample_rate), 'reverb_voz': VocalReverb(self.sample_rate), 'pitch_shifter': PitchShift(self.sample_rate), 'pitch_correction': PitchCorrection(), 'vocal_tremolo': VocalTremolo(self.sample_rate)
            }
        }
        self.chain_order = {
            'instrument': ['compressor', 'wahwah', 'puresky', 'afinador', 'vintage_overdrive', 'overdrive', 'fuzz', 'carmilla_distortion', 'distortion', 'equalizer', 'chorus_ce2', 'chorus', 'boss_bf2_flanger', 'ultra_flanger', 'tremolo', 'delay', 'reverb', 'CaineOldSchoolReverb'],
            'voice': ['vocal_compressor', 'deesser', 'vocal_equalizer', 'pitch_correction', 'pitch_shifter', 'pop_click_suppressor', 'vocal_delay', 'reverb_voz', 'vocal_tremolo']
        }
        self.params_state = {
            'instrument': {
                'overdrive': {'enabled': False, 'params': {'gain': 5.0, 'tone': 5.0, 'level': 7.0}}, 'distortion': {'enabled': False, 'params': {'drive': 10.0, 'level': 5.0}}, 'fuzz': {'enabled': False, 'params': {'gain': 15.0, 'mix': 1.0}}, 'chorus': {'enabled': False, 'params': {'rate': 2.0, 'width': 0.003, 'intensity': 0.7, 'tone': 5.0, 'mode': 'chorus'}}, 'delay': {'enabled': False, 'params': {'time_ms': 300, 'feedback': 0.4, 'mix': 0.3}}, 'reverb': {'enabled': False, 'params': {'mix': 0.3, 'size': 0.7, 'decay': 0.5, 'level': 1.0}}, 'tremolo': {'enabled': False, 'params': {'rate': 5.0, 'depth': 0.8}}, 'wahwah': {'enabled': False, 'params': {'rate': 1.5, 'min_freq': 400, 'max_freq': 2000, 'q': 5.0}}, 'equalizer': {'enabled': False, 'params': {}}, 'afinador': {'enabled': False, 'params': {}}, 'puresky': {'enabled': False, 'params': {'gain': 0.3, 'level': 0.7, 'bass': 0.0, 'treble': 0.0}}, 'compressor': {'enabled': False, 'params': {'threshold_db': -20, 'ratio': 4.0, 'attack_ms': 10, 'release_ms': 200, 'level': 5.0}}, 'vintage_overdrive': {'enabled': False, 'params': {'drive': 6.0, 'tone': 4.0, 'level': 8.0}}, 'carmilla_distortion': {'enabled': False, 'params': {'gain': 12.0, 'tone': 6.0, 'level': 7.0}}, 'chorus_ce2': {'enabled': False, 'params': {'rate': 4.0, 'depth': 0.75}}, 'boss_bf2_flanger': {'enabled': False, 'params': {'rate': 3.0, 'depth': 0.7, 'manual': 0.5, 'resonance': 0.4}}, 'ultra_flanger': {'enabled': False, 'params': {'rate': 2.0, 'depth': 0.8, 'resonance': 0.5, 'manual': 0.6}}, 'CaineOldSchoolReverb': {'enabled': False, 'params': {'mode': 'room', 'decay': 0.7, 'mix': 0.5, 'tone': 0.5}}
            },
            'voice': {
                'vocal_compressor': {'enabled': False, 'params': {}},'pop_click_suppressor': {'enabled': False, 'params': {}}, 'deesser': {'enabled': False, 'params': {}}, 'vocal_equalizer': {'enabled': False, 'params': {}}, 'vocal_delay': {'enabled': False, 'params': {}}, 'reverb_voz': {'enabled': False, 'params': {}}, 'pitch_shifter': {'enabled': False, 'params': {}}, 'pitch_correction': {'enabled': False, 'params': {}}, 'vocal_tremolo': {'enabled': False, 'params': {}}
            }
        }
    
    def set_channel_mapping(self, instrument_channel, voice_channel):
        self.channel_mapping['instrument'] = instrument_channel
        self.channel_mapping['voice'] = voice_channel

    def toggle_input_channel(self, chain_type, is_enabled):
        if chain_type in self.input_enabled:
            self.input_enabled[chain_type] = is_enabled

    def load_backing_track(self, filepath):
        try:
            data, sr = sf.read(filepath, dtype='float32')
            if sr != self.sample_rate: print(f"Aviso: Sample rate da backing track ({sr}Hz) é diferente do da engine ({self.sample_rate}Hz).")
            if data.ndim > 1: data = data.mean(axis=1)
            self.backing_track_data = data
            self.playback_position = 0
            self.playback_state = 'stopped'
            return True
        except Exception as e:
            print(f"Erro ao carregar a backing track: {e}")
            self.backing_track_data = None
            return False

    def toggle_playback(self):
        if self.backing_track_data is None: return 'stopped'
        if self.playback_state == 'playing': self.playback_state = 'paused'
        else: self.playback_state = 'playing'
        return self.playback_state

    def stop_playback(self):
        self.playback_state = 'stopped'
        self.playback_position = 0
        return self.playback_state

    def get_playback_state(self):
        return self.playback_state

    def set_backing_track_volume(self, volume):
        self.backing_track_volume = float(volume)

    def get_playback_info(self):
        if self.backing_track_data is None:
            return {'position': 0, 'duration': 0}
        return {'position': self.playback_position, 'duration': len(self.backing_track_data)}

    def set_playback_position(self, position_ratio):
        if self.backing_track_data is not None:
            self.playback_position = int(len(self.backing_track_data) * position_ratio)

    def set_master_volume(self, value):
        self.master_volume = value

    def set_chain_order(self, chain_type, new_order):
        self.chain_order[chain_type] = new_order
        
    def update_param(self, chain_type, effect_name, param_key, value):
        if chain_type in self.params_state and effect_name in self.params_state[chain_type]:
            self.params_state[chain_type][effect_name]['params'][param_key] = value

    def toggle_effect(self, chain_type, effect_name, is_enabled):
        if chain_type in self.params_state and effect_name in self.params_state[chain_type]:
            self.params_state[chain_type][effect_name]['enabled'] = is_enabled

    def process_audio(self, instrument_input, voice_input):
        processed_instrument = instrument_input.copy()
        for effect_name in self.chain_order['instrument']:
            state = self.params_state['instrument'].get(effect_name)
            if state and state['enabled'] and effect_name in self.effects['instrument']:
                instance = self.effects['instrument'][effect_name]
                params = state.get('params', {})
                processed_instrument = instance.apply(processed_instrument, **params)
        
        processed_voice = voice_input.copy()
        for effect_name in self.chain_order['voice']:
            state = self.params_state['voice'].get(effect_name)
            if state and state['enabled'] and effect_name in self.effects['voice']:
                instance = self.effects['voice'][effect_name]
                params = state.get('params', {})
                processed_voice = instance.apply(processed_voice, **params)

        mixed_signal = processed_instrument + processed_voice
        
        track_chunk = np.zeros(self.block_size, dtype=np.float32)
        if self.backing_track_data is not None and self.playback_state == 'playing':
            start, end = self.playback_position, self.playback_position + self.block_size
            chunk = self.backing_track_data[start:end]
            if len(chunk) < self.block_size:
                track_chunk[:len(chunk)] = chunk
                self.playback_position = 0
                self.playback_state = 'stopped'
            else:
                track_chunk = chunk
                self.playback_position = end
        
        final_mix = mixed_signal + (track_chunk * self.backing_track_volume)
        final_mix *= self.master_volume
        return np.clip(final_mix, -1.0, 1.0)
    
    def process_tuner(self, audio_buffer):
        freq = yin_detect_pitch(audio_buffer, self.sample_rate)
        note = freq_to_note(freq)
        self.tuner_note = note
        return note

    def get_full_state(self):
        state = self.params_state.copy()
        state['master_volume'] = {'params': {'level': self.master_volume}}
        state['input_enabled'] = self.input_enabled
        return state

    def set_full_state(self, new_state):
        if 'master_volume' in new_state:
            self.master_volume = new_state['master_volume']['params']['level']
            del new_state['master_volume']
        
        if 'input_enabled' in new_state:
            self.input_enabled = new_state['input_enabled']
            del new_state['input_enabled']

        for key, state in new_state.items():
            if key in self.params_state:
                self.params_state[key] = state