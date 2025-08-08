# backend/audio_interface.py

import numpy as np
import sounddevice as sd
import soundfile as sf
from queue import Queue, Empty
import time
import os

# --- IMPORTS DOS EFEITOS DE INSTRUMENTO ---
from backend.effects.overdrive import Overdrive
from backend.effects.distortion import Distortion
from backend.effects.fuzz import Fuzz
from backend.effects.chorus import ChorusEffect
from backend.effects.delay import Delay
from backend.effects.reverb import Reverb
from backend.effects.tremolo import Tremolo
from backend.effects.wahwah import WahWah
from backend.effects.equalizer import Equalizer
from backend.effects.tuner import yin_detect_pitch, freq_to_note
from backend.effects.compressor_guitarra import CompressorEffect
from backend.effects.VintageOverdrive import VintageOverdrive
from backend.effects.CarmillaDistortion import CarmillaDistortionEffect
from backend.effects.chorusCE2 import CE2ChorusEffect
from backend.effects.BOSS_BF_2_Flanger import BossBf2Flanger
from backend.effects.Ultra_Flanger_UF100 import BehringerUf100Flanger
from backend.effects.PureSky import PureSky
from backend.effects.Afinador import BossTU3Tuner
from backend.effects.CaineOldSchoolReverb import CaineOldSchoolReverb

# --- NOVOS IMPORTS DOS EFEITOS DE VOZ ---
from backend.voz.Vocal_Compressor import VocalCompressor
from backend.voz.VocalDeesser import DeEsser
from backend.voz.Vocal_equalizer import VocalEqualizer
from backend.voz.Vocal_Delay import VocalDelay
from backend.voz.Reverb_voz import Reverb
from backend.voz.PitchShift import PitchShift
from backend.voz.PitchCorrection import PitchCorrection
from backend.voz.Vocal_Tremolo import VocalTremolo
from backend.voz.PopClickSuppressor import PopClickSuppressor

# --- NOVO IMPORT DA CLASSE DE GRAVAÇÃO ---
from ui.audio_recorder import AudioRecorder

# --- CONSTANTES GLOBAIS DE ÁUDIO ---
SAMPLE_RATE = 48000
BLOCK_SIZE = 32

# --- CLASSE AUDIOENGINE ATUALIZADA PARA MULTICANAL ---
class AudioEngine:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.block_size = BLOCK_SIZE
        self.master_volume = 1.0

        self.backing_track_data = None
        self.playback_position = 0
        self.backing_track_volume = 0.7
        self.playback_state = 'stopped'

        self.channel_mapping = {
            'instrument': 0,
            'voice': 1
        }
        
        self.chain_order = {
            'instrument': ['compressor', 'wahwah', 'puresky', 'afinador', 'vintage_overdrive', 'overdrive', 'fuzz', 'carmilla_distortion', 'distortion', 'equalizer', 'chorus_ce2', 'chorus', 'boss_bf2_flanger', 'ultra_flanger', 'tremolo', 'delay', 'reverb', 'CaineOldSchoolReverb'],
            'voice': ['vocal_compressor', 'deesser', 'vocal_equalizer', 'pitch_correction', 'pitch_shifter', 'pop_click_suppressor', 'vocal_delay', 'reverb_voz', 'vocal_tremolo']
        }
        self.effects = {
            'instrument': {
                'overdrive': Overdrive(self.sample_rate), 'distortion': Distortion(self.sample_rate), 'fuzz': Fuzz(self.sample_rate), 'wahwah': WahWah(self.sample_rate), 'equalizer': Equalizer(self.sample_rate), 'chorus': ChorusEffect(self.sample_rate), 'tremolo': Tremolo(self.sample_rate), 'delay': Delay(self.sample_rate), 'reverb': Reverb(self.sample_rate), 'puresky': PureSky(self.sample_rate), 'afinador': BossTU3Tuner(sample_rate=self.sample_rate), 'compressor': CompressorEffect(self.sample_rate), 'vintage_overdrive': VintageOverdrive(self.sample_rate), 'carmilla_distortion': CarmillaDistortionEffect(self.sample_rate), 'chorus_ce2': CE2ChorusEffect(self.sample_rate), 'boss_bf2_flanger': BossBf2Flanger(self.sample_rate), 'ultra_flanger': BehringerUf100Flanger(self.sample_rate), 'CaineOldSchoolReverb': CaineOldSchoolReverb(self.sample_rate, self.block_size)
            },
            'voice': {
                'vocal_compressor': VocalCompressor(self.sample_rate), 'pop_click_suppressor': PopClickSuppressor(self.sample_rate), 'deesser': DeEsser(self.sample_rate), 'vocal_equalizer': VocalEqualizer(self.sample_rate), 'vocal_delay': VocalDelay(self.sample_rate), 'reverb_voz': Reverb(self.sample_rate), 'pitch_shifter': PitchShift(self.sample_rate), 'pitch_correction': PitchCorrection(), 'vocal_tremolo': VocalTremolo(self.sample_rate)
            }
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

    def process_audio(self, instrument_input, voice_input):
        processed_instrument = instrument_input.copy()
        for effect_name in self.chain_order['instrument']:
            if self.params_state['instrument'].get(effect_name, {}).get('enabled') and effect_name in self.effects['instrument']:
                instance = self.effects['instrument'][effect_name]
                params = self.params_state['instrument'][effect_name].get('params', {})
                processed_instrument = instance.apply(processed_instrument, **params)
        
        processed_voice = voice_input.copy()
        for effect_name in self.chain_order['voice']:
            if self.params_state['voice'].get(effect_name, {}).get('enabled') and effect_name in self.effects['voice']:
                instance = self.effects['voice'][effect_name]
                params = self.params_state['voice'][effect_name].get('params', {})
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

_engine = AudioEngine()
_stream = None
_recorder = None 
_tuner_accumulation_buffer = np.array([], dtype=np.float32)
tuner_queue = Queue(maxsize=1)
command_queue = Queue()

def set_channel_mapping(inst_idx, voice_idx):
    command_queue.put({'action': 'set_channel_mapping', 'instrument': inst_idx, 'voice': voice_idx})

def load_backing_track(filepath): return _engine.load_backing_track(filepath)
def toggle_playback(): return _engine.toggle_playback()
def stop_playback(): return _engine.stop_playback()
def get_playback_state(): return _engine.get_playback_state()
def set_backing_track_volume(volume): _engine.set_backing_track_volume(volume)
def get_playback_info(): return _engine.get_playback_info()
def set_playback_position(position_ratio): _engine.set_playback_position(position_ratio)

def toggle_effect(chain_type, effect_name, is_enabled):
    command_queue.put({'action': 'toggle_effect', 'chain': chain_type, 'effect': effect_name, 'value': is_enabled})

def update_param(chain_type, effect_name, param_key, value):
    command_queue.put({'action': 'update_param', 'chain': chain_type, 'effect': effect_name, 'param': param_key, 'value': value})

def get_param_value(chain_type, effect_name, param_key, default=None):
    return _engine.params_state.get(chain_type, {}).get(effect_name, {}).get('params', {}).get(param_key, default)

def is_effect_enabled(chain_type, effect_name):
    return _engine.params_state.get(chain_type, {}).get(effect_name, {}).get('enabled', False)

def get_chain_order(chain_type):
    return _engine.chain_order.get(chain_type, [])

def set_chain_order(chain_type, new_order):
    command_queue.put({'action': 'set_chain_order', 'chain': chain_type, 'value': new_order})

def set_master_volume(value):
    command_queue.put({'action': 'set_master_volume', 'value': float(value)})

def get_full_state():
    state = _engine.params_state.copy()
    state['master_volume'] = {'params': {'level': _engine.master_volume}}
    return state
def set_full_state(new_state): command_queue.put({'action': 'set_full_state', 'value': new_state})

def _process_commands():
    while not command_queue.empty():
        try:
            cmd = command_queue.get_nowait()
            action = cmd['action']
            if action in ['toggle_effect', 'update_param']:
                chain = cmd['chain']
                effect = cmd['effect']
                if action == 'toggle_effect':
                    _engine.params_state[chain][effect]['enabled'] = cmd['value']
                elif action == 'update_param':
                    _engine.params_state[chain][effect]['params'][cmd['param']] = cmd['value']
            elif action == 'set_master_volume':
                _engine.master_volume = cmd['value']
            elif action == 'set_chain_order':
                _engine.chain_order[cmd['chain']] = cmd['value']
            elif action == 'set_channel_mapping':
                _engine.set_channel_mapping(cmd['instrument'], cmd['voice'])
            elif action == 'set_full_state':
                full_new_state = cmd['value']
                for key, state in full_new_state.items():
                    if key in _engine.params_state: _engine.params_state[key] = state
                _engine.master_volume = _engine.params_state.get('master_volume', {}).get('params', {}).get('level', 1.0)
        except (Empty, KeyError): continue

def audio_callback(indata, outdata, frames, time, status):
    global _tuner_accumulation_buffer, _recorder
    if status: print(status, flush=True)
    _process_commands()
    
    inst_idx = _engine.channel_mapping['instrument']
    voice_idx = _engine.channel_mapping['voice']
    
    instrument_in = indata[:, inst_idx] if indata.shape[1] > inst_idx else np.zeros(frames)
    voice_in = indata[:, voice_idx] if indata.shape[1] > voice_idx else np.zeros(frames)
    
    is_tuner_enabled = _engine.params_state['instrument'].get('afinador', {}).get('enabled', False)
    if is_tuner_enabled:
        tuner_instance = _engine.effects['instrument'].get('afinador')
        if tuner_instance:
            tuner_instance.apply(instrument_in)
        audio_out = np.zeros_like(instrument_in)
    else:
        audio_out = _engine.process_audio(instrument_in, voice_in)
    
    if _recorder:
        # CORRIGIDO: Agora gravo o áudio estéreo de saída
        _recorder.write(outdata)

    outdata[:, 0] = audio_out
    outdata[:, 1] = audio_out

def list_active_devices(): return sd.query_devices()

def start_recording(filepath):
    global _recorder, _stream
    if _stream and _stream.active:
        channels = _stream.channels[1] 
        _recorder = AudioRecorder(samplerate=_stream.samplerate, channels=channels)
        return _recorder.start(filepath)
    else:
        print("Erro: Stream de áudio não está ativo.")
        return False

def stop_recording():
    global _recorder
    if _recorder:
        _recorder.stop()
        _recorder = None

def start_audio_stream(in_device_name=None, out_device_name=None):
    global _stream
    stop_audio_stream()
    try:
        device_info = sd.query_devices(in_device_name)
        in_channels = device_info['max_input_channels']
        
        _stream = sd.Stream(
            samplerate=SAMPLE_RATE, channels=(in_channels, 2), callback=audio_callback,
            device=(in_device_name, out_device_name), dtype='float32',
            blocksize=BLOCK_SIZE, latency='low'
        )
        _stream.start()
        print("-" * 50); print("STREAM DE ÁUDIO INICIADO COM SUCESSO"); print(f"  Dispositivo de Entrada: '{in_device_name}'"); print(f"  Dispositivo de Saída:   '{out_device_name}'"); print(f"  Tamanho do Bloco (Blocksize): {BLOCK_SIZE} samples"); print(f"  Taxa de Amostragem (Sample Rate): {_stream.samplerate} Hz"); input_latency_ms = _stream.latency[0] * 1000; output_latency_ms = _stream.latency[1] * 1000; print(f"  Latência REAL: {input_latency_ms:.2f} ms (Entrada), {output_latency_ms:.2f} ms (Saída)"); print(f"  Latência Total Estimada: {input_latency_ms + output_latency_ms:.2f} ms"); print("-" * 50)
    except Exception as e:
        print(f"Falha ao iniciar stream: {e}"); _stream = None; raise

def stop_audio_stream():
    global _stream, _recorder
    if _recorder:
        _recorder.stop()
        _recorder = None
    if _stream:
        _stream.stop()
        _stream.close()
        _stream = None
        print("Stream parado.")

def get_recording_time():
    global _recorder
    if _recorder:
        return _recorder.get_recording_time()
    return 0

def toggle_recording_pause():
    global _recorder
    if _recorder and _recorder.is_active:
        if _recorder.is_paused:
            _recorder.resume()
            return 'resumed'
        else:
            _recorder.pause()
            return 'paused'
    return None