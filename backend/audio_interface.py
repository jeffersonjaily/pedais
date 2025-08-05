# backend/audio_interface.py

import numpy as np
import sounddevice as sd
import soundfile as sf
from queue import Queue, Empty
import time

# --- CONSTANTES GLOBAIS DE ÁUDIO ---
SAMPLE_RATE = 48000
BLOCK_SIZE = 512 # Comece com 512 ou 256 para mais estabilidade.

# --- IMPORTS DOS EFEITOS ---
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

# --- CLASSE AUDIOENGINE CORRIGIDA E COMPLETA ---
class AudioEngine:
    """
    Classe que encapsula todo o estado e a lógica de processamento de áudio.
    """
    def __init__(self):
        # 1. Parâmetros Globais de Áudio
        self.sample_rate = SAMPLE_RATE
        self.block_size = BLOCK_SIZE
        self.master_volume = 1.0

        # 2. Ordem dos Efeitos
        self.chain_order = [
            'compressor', 'wahwah', 'puresky', 'afinador',
            'vintage_overdrive', 'overdrive', 'fuzz', 'carmilla_distortion', 'distortion',
            'equalizer',
            'chorus_ce2', 'chorus', 'boss_bf2_flanger', 'ultra_flanger', 'tremolo',
            'delay', 'reverb', 'CaineOldSchoolReverb'
        ]

        # 3. Instâncias dos Efeitos (Objetos das Classes)
        self.effects = {
            'overdrive': Overdrive(self.sample_rate), 'distortion': Distortion(self.sample_rate),
            'fuzz': Fuzz(self.sample_rate), 'wahwah': WahWah(self.sample_rate),
            'equalizer': Equalizer(self.sample_rate), 'chorus': ChorusEffect(self.sample_rate),
            'tremolo': Tremolo(self.sample_rate), 'delay': Delay(self.sample_rate),
            'reverb': Reverb(self.sample_rate), 'puresky': PureSky(self.sample_rate),
            'afinador': BossTU3Tuner(), 'compressor': CompressorEffect(self.sample_rate),
            'vintage_overdrive': VintageOverdrive(self.sample_rate),
            'carmilla_distortion': CarmillaDistortionEffect(self.sample_rate),
            'chorus_ce2': CE2ChorusEffect(self.sample_rate),
            'boss_bf2_flanger': BossBf2Flanger(self.sample_rate),
            'ultra_flanger': BehringerUf100Flanger(self.sample_rate),
            'CaineOldSchoolReverb': CaineOldSchoolReverb(self.sample_rate, self.block_size)
        }

        # 4. Estado dos Efeitos (Valores dos Knobs vindos da UI)
        self.params_state = {
            'overdrive': {'enabled': False, 'params': {'gain': 5.0, 'tone': 5.0, 'level': 7.0}},
            'distortion': {'enabled': False, 'params': {'drive': 10.0, 'level': 5.0}},
            'fuzz': {'enabled': False, 'params': {'gain': 15.0, 'mix': 1.0}},
            'chorus': {'enabled': False, 'params': {'rate': 2.0, 'width': 0.003, 'intensity': 0.7, 'tone': 5.0, 'mode': 'chorus'}},
            'delay': {'enabled': False, 'params': {'time_ms': 300, 'feedback': 0.4, 'mix': 0.3}},
            'reverb': {'enabled': False, 'params': {'mix': 0.3, 'size': 0.7, 'decay': 0.5}},
            'tremolo': {'enabled': False, 'params': {'rate': 5.0, 'depth': 0.8}},
            'wahwah': {'enabled': False, 'params': {'rate': 1.5, 'min_freq': 400, 'max_freq': 2000, 'q': 5.0}},
            'equalizer': {'enabled': False, 'params': {}},
            'afinador': {'enabled': False, 'params': {}},
            'puresky': {'enabled': False, 'params': {'gain': 0.3, 'level': 0.7, 'bass': 0.0, 'treble': 0.0}},
            'compressor': {'enabled': False, 'params': {'threshold_db': -20, 'ratio': 4.0, 'attack_ms': 10, 'release_ms': 200, 'level': 5.0}},
            'vintage_overdrive': {'enabled': False, 'params': {'drive': 6.0, 'tone': 4.0, 'level': 8.0}},
            'carmilla_distortion': {'enabled': False, 'params': {'gain': 12.0, 'tone': 6.0, 'level': 7.0}},
            'chorus_ce2': {'enabled': False, 'params': {'rate': 4.0, 'depth': 0.75}},
            'boss_bf2_flanger': {'enabled': False, 'params': {'rate': 3.0, 'depth': 0.7, 'manual': 0.5, 'resonance': 0.4}},
            'ultra_flanger': {'enabled': False, 'params': {'rate': 2.0, 'depth': 0.8, 'resonance': 0.5, 'manual': 0.6}},
            'CaineOldSchoolReverb': {'enabled': False, 'params': {'mode': 'room', 'decay': 0.7, 'mix': 0.5, 'tone': 0.5}},
        }

    def process_audio(self, input_buffer):
        """
        Aplica a cadeia de efeitos ao buffer de áudio na ordem correta.
        """
        processed_buffer = input_buffer.copy()

        for effect_name in self.chain_order:
            if self.params_state.get(effect_name, {}).get('enabled') and effect_name in self.effects:
                instance = self.effects[effect_name]
                params = self.params_state[effect_name].get('params', {})

                # Tratamento especial para o Equalizer
                if effect_name == 'equalizer':
                    bands_list = []
                    for param_key, gain_db in params.items():
                        try:
                            freq_str = param_key.split('_', 1)[1].replace('hz', '').replace('khz', '000').replace('.', '')
                            freq = float(freq_str)
                            bands_list.append({'type': 'peak', 'freq': freq, 'gain_db': gain_db, 'q': 1.4})
                        except (IndexError, ValueError):
                            continue
                    
                    # A classe Equalizer espera os parâmetros dentro de uma chave 'bands'
                    processed_buffer = instance.apply(processed_buffer, bands=bands_list)
                else:
                    # Todos os outros efeitos recebem seus parâmetros diretamente
                    processed_buffer = instance.apply(processed_buffer, **params)

        processed_buffer *= self.master_volume
        return np.clip(processed_buffer, -1.0, 1.0)

# --- SINGLETON E INTERFACE GLOBAL ---
_engine = AudioEngine()
_stream = None
_recording_file = None
_is_recording = False
_tuner_accumulation_buffer = np.array([], dtype=np.float32)
tuner_queue = Queue(maxsize=1)
command_queue = Queue()

# --- FUNÇÕES DE INTERFACE (já estavam corretas) ---
def update_param(effect_name, param_key, value): command_queue.put({'action': 'update_param', 'effect': effect_name, 'param': param_key, 'value': value})
def toggle_effect(effect_name, is_enabled): command_queue.put({'action': 'toggle_effect', 'effect': effect_name, 'value': is_enabled})
def set_master_volume(value): command_queue.put({'action': 'set_master_volume', 'value': float(value)})
def set_chain_order(new_order): command_queue.put({'action': 'set_chain_order', 'value': new_order})
def get_param_value(effect_name, param_key, default=None): return _engine.params_state.get(effect_name, {}).get('params', {}).get(param_key, default)
def is_effect_enabled(effect_name): return _engine.params_state.get(effect_name, {}).get('enabled', False)
def get_chain_order(): return _engine.chain_order

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
            if action == 'update_param':
                _engine.params_state[cmd['effect']]['params'][cmd['param']] = cmd['value']
            elif action == 'toggle_effect':
                _engine.params_state[cmd['effect']]['enabled'] = cmd['value']
            elif action == 'set_master_volume':
                _engine.master_volume = cmd['value']
            elif action == 'set_chain_order':
                _engine.chain_order = cmd['value']
            elif action == 'set_full_state':
                full_new_state = cmd['value']
                for key, state in full_new_state.items():
                    if key in _engine.params_state:
                         _engine.params_state[key] = state
                _engine.master_volume = _engine.params_state.get('master_volume', {}).get('params', {}).get('level', 1.0)
        except (Empty, KeyError):
            continue

def audio_callback(indata, outdata, frames, time, status):
    global _tuner_accumulation_buffer
    if status: print(status, flush=True)
    _process_commands()
    
    audio_in = indata[:, 0]
    
    if _engine.params_state.get('afinador', {}).get('enabled', False):
        _tuner_accumulation_buffer = np.append(_tuner_accumulation_buffer, audio_in)
        if len(_tuner_accumulation_buffer) >= 8192:
            freq = detect_pitch(_tuner_accumulation_buffer)
            note_data = freq_to_note(freq)
            if not tuner_queue.full(): tuner_queue.put(note_data)
            _tuner_accumulation_buffer = np.array([], dtype=np.float32)
        audio_out = np.zeros_like(audio_in)
    else:
        audio_out = _engine.process_audio(audio_in)
        
    outdata[:, 0] = audio_out
    
    if _is_recording and _recording_file:
        _recording_file.write(audio_out)

def list_active_devices(): return sd.query_devices()
def start_recording(filepath):
    global _is_recording, _recording_file
    try:
        _recording_file = sf.SoundFile(filepath, mode='w', samplerate=SAMPLE_RATE, channels=1)
        _is_recording = True
        return True
    except Exception as e:
        print(f"Erro ao iniciar gravação: {e}")
        return False
def stop_recording():
    global _is_recording, _recording_file
    if _recording_file: _recording_file.close()
    _is_recording = False
    _recording_file = None

def start_audio_stream(in_device_name=None, out_device_name=None):
    global _stream
    stop_audio_stream()
    try:
        _stream = sd.Stream(
            samplerate=SAMPLE_RATE, channels=1, callback=audio_callback,
            device=(in_device_name, out_device_name), dtype='float32',
            blocksize=BLOCK_SIZE, latency='low'
        )
        _stream.start()
        print("-" * 50); print("STREAM DE ÁUDIO INICIADO COM SUCESSO"); print(f"  Dispositivo de Entrada: '{in_device_name}'"); print(f"  Dispositivo de Saída:   '{out_device_name}'"); print(f"  Tamanho do Bloco (Blocksize): {BLOCK_SIZE} samples"); print(f"  Taxa de Amostragem (Sample Rate): {_stream.samplerate} Hz"); input_latency_ms = _stream.latency[0] * 1000; output_latency_ms = _stream.latency[1] * 1000; print(f"  Latência REAL: {input_latency_ms:.2f} ms (Entrada), {output_latency_ms:.2f} ms (Saída)"); print(f"  Latência Total Estimada: {input_latency_ms + output_latency_ms:.2f} ms"); print("-" * 50)
    except Exception as e:
        print(f"Falha ao iniciar stream: {e}")
        _stream = None
        raise

def stop_audio_stream():
    global _stream
    stop_recording()
    if _stream:
        _stream.stop()
        _stream.close()
        _stream = None
        print("Stream parado.")
