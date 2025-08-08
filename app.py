# app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
from queue import Empty
import json

# --- ATIVAÇÃO DO ASIO ---
os.environ['SD_ENABLE_ASIO'] = '1'

# --- IMPORTS DOS MÓDULOS ---
from backend import audio_interface
from backend.effects_config import PEDAL_CONFIGS
from backend.voz.effects_config import PEDAL_CONFIGS_VOZ
from backend.effects.pedal_control import PedalControl
import layout_config as layout
from ui.drag_manager import DragManager
from ui.shortcut_window import ShortcutWindow
from ui.Mini_play import MiniPlayer

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(layout.WINDOW_TITLE)
        self.geometry(layout.WINDOW_GEOMETRY)
        self.configure(bg=layout.COLOR_BACKGROUND)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_styles()
        
        self.tuner_enabled_var = tk.BooleanVar(value=False)
        self.stream_running = False
        self.is_recording = False
        
        self.pedal_widgets = {'instrument': [], 'voice': []}
        self.pedal_frames = {'instrument': [], 'voice': []}
        
        self.shortcut_map = {}
        self._load_shortcuts()

        self.create_menu()
        self.create_audio_controls()
        self.create_main_frame_with_tabs()
        self.create_pedals()
        self.layout_pedals('instrument')
        self.layout_pedals('voice')
        
        self.drag_manager_instrument = DragManager(self)
        for frame in self.pedal_frames['instrument']:
            self.drag_manager_instrument.add_draggable(frame)
        
        self.drag_manager_voice = DragManager(self)
        for frame in self.pedal_frames['voice']:
            self.drag_manager_voice.add_draggable(frame)
        
        self.bind("<KeyPress>", self._handle_keypress)
        self.update_tuner_display()

    def create_main_frame_with_tabs(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        instrument_tab = ttk.Frame(self.notebook)
        self.notebook.add(instrument_tab, text='🎸 Guitarra')
        self.scroll_frame_instrument = self._create_scrolling_area(instrument_tab)
        voice_tab = ttk.Frame(self.notebook)
        self.notebook.add(voice_tab, text='🎤 Voz')
        self.scroll_frame_voice = self._create_scrolling_area(voice_tab)

    def _create_scrolling_area(self, parent_tab):
        canvas = tk.Canvas(parent_tab, bg=layout.COLOR_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scroll_frame

    def create_pedals(self):
        self._create_pedal_set('instrument', PEDAL_CONFIGS, self.scroll_frame_instrument)
        self._create_pedal_set('voice', PEDAL_CONFIGS_VOZ, self.scroll_frame_voice)

    def _create_pedal_set(self, chain_type, configs, parent_frame):
        order = audio_interface.get_chain_order(chain_type)
        for effect_name in order:
            if effect_name not in configs: continue
            config = configs[effect_name]
            frame_container = ttk.LabelFrame(parent_frame, text=config.get('title', effect_name.capitalize()))
            frame_container.effect_name = effect_name
            widget = PedalControl(frame_container, chain_type, effect_name, config)
            widget.pack(fill="x", expand=True, padx=5, pady=5)
            self.pedal_widgets[chain_type].append(widget)
            self.pedal_frames[chain_type].append(frame_container)

    def layout_pedals(self, chain_type):
        frames = self.pedal_frames[chain_type]
        for i, frame in enumerate(frames):
            row = i // layout.PEDALBOARD_COLUMNS
            col = i % layout.PEDALBOARD_COLUMNS
            frame.grid(row=row, column=col, padx=layout.PEDAL_PADDING_X, pady=layout.PEDAL_PADDING_Y, sticky="nsew")
    
    def on_pedal_reorder(self):
        active_tab_text = self.notebook.tab(self.notebook.select(), "text")
        chain_type = 'instrument' if active_tab_text.startswith('🎸') else 'voice'
        new_order = [p.effect_name for p in self.pedal_frames[chain_type]]
        audio_interface.set_chain_order(chain_type, new_order)
        self.layout_pedals(chain_type)

    def sync_all_pedals(self):
        for chain_type in ['instrument', 'voice']:
            for widget in self.pedal_widgets[chain_type]:
                widget.sync_with_state()
        master_vol = audio_interface.get_param_value('master_volume', 'level', 1.0)
        if master_vol is not None:
            self.master_volume_var.set(master_vol)

    def toggle_tuner(self):
        audio_interface.toggle_effect('instrument', 'afinador', self.tuner_enabled_var.get())

    def _handle_keypress(self, event):
        key = event.keysym
        if key in self.shortcut_map:
            target_effect_name = self.shortcut_map[key]
            for chain_type in ['instrument', 'voice']:
                for pedal_widget in self.pedal_widgets[chain_type]:
                    if pedal_widget.effect_name == target_effect_name:
                        pedal_widget.enable_button.invoke()
                        state = "ativado" if pedal_widget.enabled_var.get() else "desativado"
                        print(f"Atalho '{key}' -> Pedal '{target_effect_name}' ({chain_type}) {state}.")
                        return

    def _load_shortcuts(self):
        try:
            if os.path.exists("shortcuts.json"):
                with open("shortcuts.json", "r") as f:
                    self.shortcut_map = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar atalhos: {e}")
            self.shortcut_map = {}

    def _save_shortcuts(self):
        try:
            with open("shortcuts.json", "w") as f:
                json.dump(self.shortcut_map, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar os atalhos:\n{e}")

    def _open_shortcut_window(self):
        ShortcutWindow(self)

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('.', background=layout.COLOR_BACKGROUND, foreground=layout.COLOR_FOREGROUND)
        self.style.configure('TFrame', background=layout.COLOR_BACKGROUND)
        self.style.configure('TLabel', background=layout.COLOR_BACKGROUND, foreground=layout.COLOR_FOREGROUND)
        self.style.configure('TLabelFrame', background=layout.COLOR_PEDAL_FRAME, bordercolor=layout.COLOR_BORDER, relief=tk.RIDGE, borderwidth=1)
        self.style.configure('TLabelFrame.Label', background=layout.COLOR_PEDAL_FRAME, foreground=layout.COLOR_FOREGROUND)
        self.style.map('TCheckbutton', background=[('active', layout.COLOR_BACKGROUND)])
        self.style.map('TLabelFrame', bordercolor=[('active', layout.COLOR_PEDAL_ACTIVE_BORDER)], borderwidth=[('active', 2)])
        self.style.map('TLabelFrame.Label', foreground=[('active', layout.COLOR_PEDAL_ACTIVE_LABEL)])

    def create_audio_controls(self):
        main_audio_frame = ttk.LabelFrame(self, text="Controle de Áudio", padding=10)
        main_audio_frame.pack(fill='x', padx=10, pady=(5,0))
        
        device_frame = ttk.Frame(main_audio_frame)
        device_frame.pack(fill='x', expand=True)
        device_frame.columnconfigure((1, 3, 5), weight=1)

        ttk.Label(device_frame, text="Dispositivo:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.input_cb = ttk.Combobox(device_frame, state="readonly", width=25)
        self.input_cb.grid(row=0, column=1, columnspan=5, sticky="ew")
        self.input_cb.bind("<<ComboboxSelected>>", self._update_channel_selectors)

        # --- NOVOS SELETORES DE CANAL ---
        ttk.Label(device_frame, text="Entrada Guitarra:").grid(row=1, column=0, padx=(0, 5), pady=(5,0), sticky="w")
        self.instrument_channel_cb = ttk.Combobox(device_frame, state="readonly", width=15)
        self.instrument_channel_cb.grid(row=1, column=1, pady=(5,0), sticky="w")
        self.instrument_channel_cb.bind("<<ComboboxSelected>>", self._on_channel_mapping_change)

        ttk.Label(device_frame, text="Entrada Voz:").grid(row=1, column=2, padx=(10, 5), pady=(5,0), sticky="w")
        self.voice_channel_cb = ttk.Combobox(device_frame, state="readonly", width=15)
        self.voice_channel_cb.grid(row=1, column=3, pady=(5,0), sticky="w")
        self.voice_channel_cb.bind("<<ComboboxSelected>>", self._on_channel_mapping_change)

        self.populate_devices()
        
        control_frame = ttk.Frame(main_audio_frame)
        control_frame.pack(fill='x', expand=True, pady=(10,0))
        
        self.start_btn = ttk.Button(control_frame, text="▶ Iniciar", command=self.start_stream)
        self.start_btn.pack(side="left", padx=(0,10))
        self.stop_btn = ttk.Button(control_frame, text="■ Parar", command=self.stop_stream, state="disabled")
        self.stop_btn.pack(side="left")
        self.record_btn = ttk.Button(control_frame, text="● Gravar", command=self.toggle_recording)
        self.record_btn.pack(side="left", padx=(20, 0))
        
        self.master_volume_var = tk.DoubleVar(value=1.0)
        master_slider = ttk.Scale(control_frame, from_=0, to=1.5, orient="horizontal", variable=self.master_volume_var, command=lambda v: audio_interface.set_master_volume(v))
        master_slider.pack(side="right", padx=(10, 0), fill='x', expand=True)
        ttk.Label(control_frame, text="Volume Master:").pack(side="right")
        
        self.mini_player = MiniPlayer(main_audio_frame)
        self.mini_player.pack(fill='x', expand=True, pady=(5,0))

        self.tuner_label = ttk.Label(main_audio_frame, text="Afinador: --", font=layout.FONT_TUNER, anchor="center")
        self.tuner_label.pack(fill='x', expand=True, pady=(10,0))

    def populate_devices(self):
        self.devices_list = audio_interface.list_active_devices()
        in_devs = [d['name'] for d in self.devices_list if d['max_input_channels'] > 0]
        self.input_cb['values'] = in_devs
        
        asio_device_name = "ASIO4ALL v2"
        if asio_device_name in in_devs:
            self.input_cb.set(asio_device_name)
        else:
            try:
                default_in = audio_interface.sd.query_devices(kind='input')['name']
                self.input_cb.set(default_in)
            except Exception:
                if in_devs: self.input_cb.current(0)
        
        self._update_channel_selectors()

    def _update_channel_selectors(self, event=None):
        selected_device_name = self.input_cb.get()
        num_channels = 0
        for dev in self.devices_list:
            if dev['name'] == selected_device_name:
                num_channels = dev['max_input_channels']
                break
        
        channel_options = [f"Canal {i+1}" for i in range(num_channels)]
        self.instrument_channel_cb['values'] = channel_options
        self.voice_channel_cb['values'] = channel_options
        
        if num_channels > 0:
            self.instrument_channel_cb.current(0)
        if num_channels > 1:
            self.voice_channel_cb.current(1)
        
        self._on_channel_mapping_change()

    def _on_channel_mapping_change(self, event=None):
        inst_idx = self.instrument_channel_cb.current()
        voice_idx = self.voice_channel_cb.current()
        if inst_idx == -1 or voice_idx == -1: return
        
        if inst_idx == voice_idx:
            messagebox.showwarning("Aviso", "A entrada da Guitarra e da Voz não podem ser o mesmo canal.")
            self.voice_channel_cb.current(1 if inst_idx == 0 else 0)
            voice_idx = self.voice_channel_cb.current()

        audio_interface.set_channel_mapping(inst_idx, voice_idx)
        print(f"Mapeamento de canais atualizado: Guitarra -> Canal {inst_idx+1}, Voz -> Canal {voice_idx+1}")

    def create_menu(self):
        menubar = tk.Menu(self)
        audio_menu = tk.Menu(menubar, tearoff=0)
        audio_menu.add_checkbutton(label="Ativar Afinador", variable=self.tuner_enabled_var, command=self.toggle_tuner)
        menubar.add_cascade(label="Áudio", menu=audio_menu)
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Salvar Preset", command=self.save_config)
        config_menu.add_command(label="Carregar Preset", command=self.load_config)
        menubar.add_cascade(label="Presets", menu=config_menu)
        shortcut_menu = tk.Menu(menubar, tearoff=0)
        shortcut_menu.add_command(label="Definir Atalhos para Pedais", command=self._open_shortcut_window)
        menubar.add_cascade(label="Atalhos", menu=shortcut_menu)
        self.config(menu=menubar)

    def on_closing(self):
        self.stop_stream()
        self.destroy()

    def update_tuner_display(self):
        if self.tuner_enabled_var.get() and self.stream_running:
            try:
                note, octave, cents = audio_interface.tuner_queue.get_nowait()
                note_display = f"{note}{octave if octave is not None else ''}"
                self.tuner_label.config(text=f"{note_display} ({cents:+.1f} cents)" if note and note != '--' else "Afinador: --")
            except Empty: pass
        else:
            self.tuner_label.config(text="Afinador: --")
        self.after(100, self.update_tuner_display)

    def start_stream(self):
        try:
            input_name = self.input_cb.get()
            output_name = input_name 
            if not input_name:
                messagebox.showerror("Erro", "Dispositivo de áudio deve ser selecionado.")
                return
            audio_interface.start_audio_stream(input_name, output_name)
            self.stream_running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Erro de Áudio", f"Não foi possível iniciar o stream: {e}")

    def stop_stream(self):
        audio_interface.stop_audio_stream()
        self.stream_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        if self.is_recording:
            audio_interface.stop_recording()
            self.is_recording = False
            self.record_btn.config(text="● Gravar")
            self.record_btn.config(style="TButton")

    def save_config(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Presets", "*.json")])
        if not path: return
        try:
            with open(path, 'w') as f: json.dump(audio_interface.get_full_state(), f, indent=2)
            messagebox.showinfo("Salvo", "Preset salvo com sucesso!")
        except Exception as e: messagebox.showerror("Erro", f"Falha ao salvar preset: {e}")
    
    def load_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Presets", "*.json")])
        if not path: return
        try:
            with open(path, 'r') as f: config = json.load(f)
            audio_interface.set_full_state(config)
            self.after(50, self.sync_all_pedals)
            messagebox.showinfo("Carregado", "Preset carregado com sucesso!")
        except Exception as e: messagebox.showerror("Erro", f"Falha ao carregar preset: {e}")

    def toggle_recording(self):
        if not self.stream_running:
            messagebox.showwarning("Aviso", "Inicie o stream de áudio antes de gravar.")
            return

        if not self.is_recording:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav")],
                title="Salvar gravação como..."
            )
            
            if not filepath:
                return
            
            try:
                audio_interface.start_recording(filepath)
                self.is_recording = True
                self.record_btn.config(text="■ Parar Gravação")
                self.record_btn.config(style="Danger.TButton")
                print(f"Gravação iniciada em: {filepath}")
            except Exception as e:
                messagebox.showerror("Erro de Gravação", f"Não foi possível iniciar a gravação:\n{e}")
                self.is_recording = False
                self.record_btn.config(text="● Gravar")

        else:
            audio_interface.stop_recording()
            self.is_recording = False
            self.record_btn.config(text="● Gravar")
            self.record_btn.config(style="TButton")
            print("Gravação finalizada.")

if __name__ == "__main__":
    app = App()
    app.mainloop()