# Seu arquivo ui\audio_recorder.py

import numpy as np
import soundfile as sf
import threading
import queue
import os
import time

class AudioRecorder:
    def __init__(self, samplerate, channels):
        self.samplerate = samplerate
        self.channels = channels
        self.q = queue.Queue()
        self.thread = None
        self.is_active = False
        self.is_paused = False
        self.start_time = None
        self.pause_start_time = None
        self.paused_duration = 0
        self.file = None

    def start(self, filepath):
        if self.is_active:
            print("Gravação já está ativa.")
            return False

        output_dir = os.path.dirname(filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            self.file = sf.SoundFile(
                filepath,
                mode='w',
                samplerate=self.samplerate,
                channels=self.channels
            )
            self.is_active = True
            self.is_paused = False
            self.paused_duration = 0
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._writer_thread)
            self.thread.start()
            print(f"Gravação iniciada em: {filepath}")
            return True
        except Exception as e:
            print(f"Erro ao iniciar a gravação: {e}")
            self.stop()
            return False

    def stop(self):
        if not self.is_active:
            return

        self.is_active = False
        self.is_paused = False
        if self.thread:
            self.thread.join()
            self.thread = None
        if self.file:
            self.file.close()
            self.file = None
        print("Gravação finalizada e arquivo salvo.")

    def write(self, data: np.ndarray):
        if self.is_active and not self.is_paused and not self.q.full():
            self.q.put(data.copy())

    def pause(self):
        if self.is_active and not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()
            print("Gravação pausada.")

    def resume(self):
        if self.is_active and self.is_paused:
            self.is_paused = False
            self.paused_duration += time.time() - self.pause_start_time
            print("Gravação retomada.")

    def get_recording_time(self):
        if not self.is_active:
            return 0
        current_time = time.time()
        if self.is_paused:
            return (self.pause_start_time - self.start_time) - self.paused_duration
        else:
            return (current_time - self.start_time) - self.paused_duration

    def _writer_thread(self):
        while self.is_active or not self.q.empty():
            try:
                data = self.q.get(timeout=0.1)
                self.file.write(data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erro na thread de gravação: {e}")
                self.is_active = False