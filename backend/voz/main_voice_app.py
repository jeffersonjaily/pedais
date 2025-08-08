import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import queue
import os
import sounddevice as sd
import sys

# Ajusta o sys.path para importar o módulo 'backend' corretamente
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import backend.voz.audio_interface as audio_interface
from backend.voz.voz_control import PedalControl
from backend.voz.effects_config import effects_CONFIGS

class FullVoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Processador de Voz com Pedais e Stream")
        self.geometry("900x800")
        self.configure(bg="#1e1e1e")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.record_queue = queue.Queue()
        self.is_recording = False

        self.build_interface()

    def build_interface(self):
        pad = 10

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=pad, pady=pad)

        # Aba Efeitos
        self.effects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.effects_tab, text="Efeitos")

        self.effects_frame = ttk.Frame(self.effects_tab)
        self.effects_frame.pack(fill='both', expand=True)

        self.pedal_controls = {}
        for effect_name, config in effects_CONFIGS.items():
            frame = ttk.Labelframe(self.effects_frame, text=config.get('title', effect_name))
            frame.pack(fill='x', padx=pad, pady=5)
            pedal = PedalControl(frame, effect_name, config)
            pedal.pack(fill='x')
            self.pedal_controls[effect_name] = pedal

        # Aba Áudio
        self.audio_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_tab, text="Áudio")

        # Dispositivo de Entrada
        ttk.Label(self.audio_tab, text="Dispositivo de Entrada:").pack(anchor='w', padx=pad, pady=(10, 0))
        self.input_devices = self.get_devices(input=True)
        self.selected_input = tk.StringVar()
        self.input_combo = ttk.Combobox(self.audio_tab, values=self.input_devices, textvariable=self.selected_input, state='readonly')
        self.input_combo.pack(fill='x', padx=pad)
        if self.input_devices:
            self.selected_input.set(self.input_devices[0])

        # Dispositivo de Saída
        ttk.Label(self.audio_tab, text="Dispositivo de Saída:").pack(anchor='w', padx=pad, pady=(10, 0))
        self.output_devices = self.get_devices(output=True)
        self.selected_output = tk.StringVar()
        self.output_combo = ttk.Combobox(self.audio_tab, values=self.output_devices, textvariable=self.selected_output, state='readonly')
        self.output_combo.pack(fill='x', padx=pad)
        if self.output_devices:
            self.selected_output.set(self.output_devices[0])

        # Controle de volume master
        ttk.Label(self.audio_tab, text="Volume Master:").pack(anchor='w', padx=pad, pady=(10, 0))
        self.master_volume = tk.DoubleVar(value=audio_interface.get_master_volume())
        volume_slider = ttk.Scale(self.audio_tab, from_=0, to=2.0, variable=self.master_volume, orient='horizontal', command=self.on_master_volume_change)
        volume_slider.pack(fill='x', padx=pad)

        # Botões Iniciar, Parar e Gravar
        btn_frame = ttk.Frame(self.audio_tab)
        btn_frame.pack(pady=pad)

        self.start_btn = ttk.Button(btn_frame, text="▶ Iniciar", command=self.start_stream)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="■ Parar", command=self.stop_stream, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.record_btn = ttk.Button(btn_frame, text="● Gravar", command=self.toggle_recording, state='disabled')
        self.record_btn.pack(side='left', padx=5)

    def get_devices(self, input=False, output=False):
        try:
            devices = sd.query_devices()
            if input:
                return [d['name'] for d in devices if d['max_input_channels'] > 0]
            if output:
                return [d['name'] for d in devices if d['max_output_channels'] > 0]
            return []
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível obter dispositivos de áudio:\n{e}")
            return []

    def on_master_volume_change(self, val):
        audio_interface.set_master_volume(float(val))

    def start_stream(self):
        try:
            input_dev = self.selected_input.get()
            output_dev = self.selected_output.get()
            audio_interface.start_audio_stream(input_device=input_dev, output_device=output_dev)
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.record_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar o stream:\n{e}")

    def stop_stream(self):
        audio_interface.stop_audio_stream()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        if self.is_recording:
            self.toggle_recording(force_stop=True)
        self.record_btn.config(state='disabled')

    def toggle_recording(self, force_stop=False):
        if force_stop:
            if self.is_recording:
                audio_interface.stop_recording()
            self.is_recording = False
            self.record_btn.config(text="● Gravar")
            return

        if self.start_btn['state'] != 'disabled':
            messagebox.showwarning("Aviso", "Inicie o stream antes de gravar.")
            return

        if not self.is_recording:
            filepath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Arquivo WAV", "*.wav")])
            if not filepath:
                return
            success = audio_interface.start_recording(filepath)
            if success:
                self.is_recording = True
                self.record_btn.config(text="■ Parar Gravação")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a gravação.")
        else:
            audio_interface.stop_recording()
            self.is_recording = False
            self.record_btn.config(text="● Gravar")

    def on_closing(self):
        if self.is_recording:
            self.toggle_recording(force_stop=True)
        audio_interface.stop_audio_stream()
        self.destroy()

if __name__ == "__main__":
    app = FullVoiceApp()
    app.mainloop()
