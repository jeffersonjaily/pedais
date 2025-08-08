import numpy as np
import sounddevice as sd
import soundfile as sf
from queue import Queue
import threading
import traceback

from backend.voz.effects_voz import AudioProcessor  # Supondo que você tenha um arquivo effects_voz.py

SAMPLE_RATE = 48000
BLOCK_SIZE = 64

class VoiceEngine:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.block_size = BLOCK_SIZE
        self.master_volume = 1.0

        self.processor = AudioProcessor()

        # Estado dos efeitos (deve bater com AudioProcessor.effects_state)
        self.params_state = {
            'equalizer': {'enabled': False, 'params': {}},
            'compressor': {'enabled': False, 'params': {}},
            'delay': {'enabled': False, 'params': {}},
            'tremolo': {'enabled': False, 'params': {}},
            'deesser': {'enabled': False, 'params': {}},
            'pitch_correction': {'enabled': False, 'params': {}},
            'pitch_shift': {'enabled': False, 'params': {}},
            'reverb': {'enabled': False, 'params': {}},
            'tuner': {'enabled': False, 'params': {}},
        }

    def process_audio(self, input_buffer: np.ndarray) -> np.ndarray:
        try:
            # Atualiza parâmetros no processador
            self.processor.update_params(self.params_state)

            processed = self.processor.process_audio(input_buffer)

            # Aplica volume mestre
            processed *= self.master_volume

            # Limita para evitar clipping
            return np.clip(processed, -1.0, 1.0)
        except Exception as e:
            print(f"Erro em process_audio: {e}")
            traceback.print_exc()
            return input_buffer  # fallback para áudio original

# Variáveis globais do módulo
_engine = VoiceEngine()
_command_queue = Queue()
_stream = None
_recording_file = None
_is_recording = False

def update_param(effect_name, param_key, value):
    _command_queue.put({'action': 'update_param', 'effect': effect_name, 'param': param_key, 'value': value})

def toggle_effect(effect_name, is_enabled):
    _command_queue.put({'action': 'toggle_effect', 'effect': effect_name, 'value': is_enabled})

def set_master_volume(value):
    _command_queue.put({'action': 'set_master_volume', 'value': float(value)})

def get_effect_state(effect_name):
    return _engine.params_state.get(effect_name, {'enabled': False, 'params': {}})

def is_effect_enabled(effect_name):
    return _engine.params_state.get(effect_name, {}).get('enabled', False)

def get_master_volume():
    return _engine.master_volume

def _process_commands():
    while not _command_queue.empty():
        try:
            cmd = _command_queue.get_nowait()
            action = cmd.get('action')
            if action == 'update_param':
                effect = cmd['effect']
                param = cmd['param']
                value = cmd['value']
                if effect in _engine.params_state:
                    _engine.params_state[effect]['params'][param] = value
            elif action == 'toggle_effect':
                effect = cmd['effect']
                value = cmd['value']
                if effect in _engine.params_state:
                    _engine.params_state[effect]['enabled'] = value
            elif action == 'set_master_volume':
                _engine.master_volume = cmd['value']
        except Exception as e:
            print(f"Erro em _process_commands: {e}")
            traceback.print_exc()

def audio_callback(indata, outdata, frames, time, status):
    global _is_recording, _recording_file
    if status:
        print(f"Stream status: {status}")
    _process_commands()

    audio_in = indata[:, 0]
    processed = _engine.process_audio(audio_in)

    outdata[:, 0] = processed

    if _is_recording and _recording_file is not None:
        try:
            _recording_file.write(processed)
        except Exception as e:
            print(f"Erro ao gravar áudio: {e}")

def start_audio_stream(input_device=None, output_device=None):
    global _stream
    stop_audio_stream()
    try:
        _stream = sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype='float32',
            callback=audio_callback,
            device=(input_device, output_device),
            latency='low',
        )
        _stream.start()
        print("Stream de áudio iniciado.")
    except Exception as e:
        print(f"Falha ao iniciar stream: {e}")
        _stream = None
        raise

def stop_audio_stream():
    global _stream, _is_recording, _recording_file
    _is_recording = False
    if _recording_file:
        try:
            _recording_file.close()
        except:
            pass
        _recording_file = None
    if _stream:
        try:
            _stream.stop()
            _stream.close()
        except:
            pass
        _stream = None
        print("Stream de áudio parado.")

def start_recording(filepath):
    global _is_recording, _recording_file
    try:
        _recording_file = sf.SoundFile(filepath, mode='w', samplerate=SAMPLE_RATE, channels=1)
        _is_recording = True
        print(f"Gravação iniciada em: {filepath}")
        return True
    except Exception as e:
        print(f"Erro ao iniciar gravação: {e}")
        return False

def stop_recording():
    global _is_recording, _recording_file
    _is_recording = False
    if _recording_file:
        try:
            _recording_file.close()
        except:
            pass
        _recording_file = None
    print("Gravação parada.")
