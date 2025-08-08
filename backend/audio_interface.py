# backend/audio_interface.py

import numpy as np
import sounddevice as sd
import soundfile as sf
from queue import Queue, Empty
import time
import os

# --- IMPORTS DOS MÓDULOS ESSENCIAIS ---
from backend.audio_processor import AudioProcessor
from backend.audio_recorder import AudioRecorder

# --- CONSTANTES GLOBAIS DE ÁUDIO ---
SAMPLE_RATE = 48000
BLOCK_SIZE = 32

# --- INSTÂNCIAS DAS CLASSES ESSENCIAIS ---
_processor = AudioProcessor(SAMPLE_RATE, BLOCK_SIZE)
_recorder = None
_stream = None

# --- FILAS DE COMUNICAÇÃO ---
tuner_queue = Queue(maxsize=1)
command_queue = Queue()

def set_channel_mapping(inst_idx, voice_idx):
    command_queue.put({'action': 'set_channel_mapping', 'instrument': inst_idx, 'voice': voice_idx})

def toggle_input_channel(chain_type, is_enabled):
    command_queue.put({'action': 'toggle_input_channel', 'chain': chain_type, 'value': is_enabled})

def load_backing_track(filepath): return _processor.load_backing_track(filepath)
def toggle_playback(): return _processor.toggle_playback()
def stop_playback(): return _processor.stop_playback()
def get_playback_state(): return _processor.get_playback_state()
def set_backing_track_volume(volume): _processor.set_backing_track_volume(volume)
def get_playback_info(): return _processor.get_playback_info()
def set_playback_position(position_ratio): command_queue.put({'action': 'set_playback_position', 'value': position_ratio})
def toggle_effect(chain_type, effect_name, is_enabled): command_queue.put({'action': 'toggle_effect', 'chain': chain_type, 'effect': effect_name, 'value': is_enabled})
def update_param(chain_type, effect_name, param_key, value): command_queue.put({'action': 'update_param', 'chain': chain_type, 'effect': effect_name, 'param': param_key, 'value': value})
def get_param_value(chain_type, effect_name, param_key, default=None): return _processor.params_state.get(chain_type, {}).get(effect_name, {}).get('params', {}).get(param_key, default)
def is_effect_enabled(chain_type, effect_name): return _processor.params_state.get(chain_type, {}).get(effect_name, {}).get('enabled', False)
def get_chain_order(chain_type): return _processor.chain_order.get(chain_type, [])
def set_chain_order(chain_type, new_order): command_queue.put({'action': 'set_chain_order', 'chain': chain_type, 'value': new_order})
def set_master_volume(value): command_queue.put({'action': 'set_master_volume', 'value': float(value)})
def get_full_state(): return _processor.get_full_state()
def set_full_state(new_state): command_queue.put({'action': 'set_full_state', 'value': new_state})

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

def start_recording(filepath, recording_channels):
    global _recorder, _stream
    if _stream and _stream.active:
        samplerate = int(_stream.samplerate)
        channels = int(_stream.channels[1])
        _recorder = AudioRecorder(samplerate=samplerate, channels=channels, recording_channels=recording_channels)
        return _recorder.start(filepath)
    else:
        print("Erro: Stream de áudio não está ativo.")
        return False

def stop_recording():
    global _recorder
    if _recorder:
        _recorder.stop()
        _recorder = None

def _process_commands():
    while not command_queue.empty():
        try:
            cmd = command_queue.get_nowait()
            action = cmd['action']
            if action == 'set_channel_mapping': _processor.set_channel_mapping(cmd['instrument'], cmd['voice'])
            elif action == 'toggle_input_channel': _processor.toggle_input_channel(cmd['chain'], cmd['value'])
            elif action == 'set_master_volume': _processor.set_master_volume(cmd['value'])
            elif action == 'set_chain_order': _processor.set_chain_order(cmd['chain'], cmd['value'])
            elif action == 'toggle_effect': _processor.toggle_effect(cmd['chain'], cmd['effect'], cmd['value'])
            elif action == 'update_param': _processor.update_param(cmd['chain'], cmd['effect'], cmd['param'], cmd['value'])
            elif action == 'set_full_state': _processor.set_full_state(cmd['value'])
            elif action == 'set_playback_position': _processor.set_playback_position(cmd['value'])
        except (Empty, KeyError): continue

def audio_callback(indata, outdata, frames, time, status):
    global _recorder
    if status: print(status, flush=True)
    _process_commands()
    
    inst_idx = _processor.channel_mapping['instrument']
    voice_idx = _processor.channel_mapping['voice']

    if _processor.input_enabled['instrument']:
        instrument_in = indata[:, inst_idx] if indata.shape[1] > inst_idx else np.zeros(frames)
    else:
        instrument_in = np.zeros(frames)
    
    if _processor.input_enabled['voice']:
        voice_in = indata[:, voice_idx] if indata.shape[1] > voice_idx else np.zeros(frames)
    else:
        voice_in = np.zeros(frames)
    
    is_tuner_enabled = _processor.params_state['instrument'].get('afinador', {}).get('enabled', False)
    
    if is_tuner_enabled:
        _processor.process_tuner(instrument_in)
        audio_out = np.zeros_like(instrument_in)
        
        try:
            if not tuner_queue.full():
                note_data = _processor.tuner_note
                tuner_queue.put_nowait(note_data)
        except Exception:
            pass
    else:
        audio_out = _processor.process_audio(instrument_in, voice_in)

    outdata[:, 0] = audio_out
    outdata[:, 1] = audio_out

    if _recorder:
        _recorder.write(outdata)

def list_active_devices(): return sd.query_devices()

def start_audio_stream(in_device_name=None):
    global _stream
    stop_audio_stream()
    try:
        device_info = sd.query_devices(in_device_name, kind='input')
        in_channels = device_info['max_input_channels']

        try:
            out_device_info = sd.query_devices(in_device_name, kind='output')
            out_device_id = out_device_info['index']
        except Exception:
            print(f"Aviso: Dispositivo '{in_device_name}' não encontrado para saída. Usando o padrão.")
            out_device_id = sd.default.device[1]
            
        _stream = sd.Stream(
            samplerate=SAMPLE_RATE, channels=(in_channels, 2), callback=audio_callback,
            device=(in_device_name, out_device_id), dtype='float32',
            blocksize=BLOCK_SIZE, latency='low'
        )
        _stream.start()
        print("-" * 50); print("STREAM DE ÁUDIO INICIADO COM SUCESSO"); print(f"  Dispositivo de Entrada: '{in_device_name}'"); print(f"  Dispositivo de Saída:   '{sd.query_devices(out_device_id)['name']}'"); print(f"  Tamanho do Bloco (Blocksize): {BLOCK_SIZE} samples"); print(f"  Taxa de Amostragem (Sample Rate): {_stream.samplerate} Hz"); input_latency_ms = _stream.latency[0] * 1000; output_latency_ms = _stream.latency[1] * 1000; print(f"  Latência REAL: {input_latency_ms:.2f} ms (Entrada), {output_latency_ms:.2f} ms (Saída)"); print(f"  Latência Total Estimada: {input_latency_ms + output_latency_ms:.2f} ms"); print("-" * 50)
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