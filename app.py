# app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from queue import Empty
import json
import os
import subprocess

# Importa os módulos do backend e de configuração
from backend import audio_interface
from backend.effects_config import PEDAL_CONFIGS
from backend.effects.pedal_control import PedalControl
import layout_config as layout

# --- CLASSE PARA GERENCIAR O DRAG-AND-DROP ---
class DragManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.drag_widget = None
        self.placeholder = None

    def add_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_press)
        widget.bind("<B1-Motion>", self.on_motion)
        widget.bind("<ButtonRelease-1>", self.on_release)
        widget.configure(cursor="hand2")

    def on_press(self, event):
        if isinstance(event.widget, (ttk.LabelFrame, ttk.Frame)):
            self.drag_widget = event.widget
            try:
                grid_info = self.drag_widget.grid_info()
                if not grid_info: return
                self.placeholder = ttk.Frame(self.drag_widget.master, width=self.drag_widget.winfo_width(), height=self.drag_widget.winfo_height())
                self.placeholder.grid(row=grid_info['row'], column=grid_info['column'], padx=layout.PEDAL_PADDING_X, pady=layout.PEDAL_PADDING_Y)
                self.drag_widget.lift()
            except Exception:
                self.drag_widget = None

    def on_motion(self, event):
        if not self.drag_widget: return
        self.drag_widget.place(x=event.x_root - self.app.winfo_rootx() - (self.drag_widget.winfo_width()//2),
                               y=event.y_root - self.app.winfo_rooty() - (self.drag_widget.winfo_height()//2))

    def on_release(self, event):
        if not self.drag_widget: return

        if self.placeholder: self.placeholder.destroy()
        self.drag_widget.place_forget()
        
        target_widget = self.drag_widget.winfo_containing(event.x_root, event.y_root)
        if target_widget and hasattr(target_widget, 'winfo_toplevel') and target_widget.winfo_toplevel() == self.app:
            while not hasattr(target_widget, 'effect_name') and target_widget.master:
                target_widget = target_widget.master
                if target_widget == self.app: break

            if hasattr(target_widget, 'effect_name') and target_widget != self.drag_widget:
                drag_index = self.app.pedal_frames.index(self.drag_widget)
                target_index = self.app.pedal_frames.index(target_widget)
                
                self.app.pedal_frames.insert(target_index, self.app.pedal_frames.pop(drag_index))
                self.app.pedal_widgets.insert(target_index, self.app.pedal_widgets.pop(drag_index))
        
        self.app.on_pedal_reorder()
        self.drag_widget = None

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---
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
        self.pedal_widgets = []
        self.pedal_frames = []
        
        self.create_menu()
        self.create_audio_controls()
        self.create_main_frame_with_scroll()
        self.create_pedals()
        self.layout_pedals()
        
        self.drag_manager = DragManager(self)
        for frame in self.pedal_frames:
            self.drag_manager.add_draggable(frame)
        
        self.update_tuner_display()

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('.', background=layout.COLOR_BACKGROUND, foreground=layout.COLOR_FOREGROUND)
        self.style.configure('TFrame', background=layout.COLOR_BACKGROUND)
        self.style.configure('TLabel', background=layout.COLOR_BACKGROUND, foreground=layout.COLOR_FOREGROUND)
        self.style.configure('TLabelFrame', background=layout.COLOR_PEDAL_FRAME, bordercolor=layout.COLOR_BORDER, relief=tk.RIDGE)
        self.style.configure('TLabelFrame.Label', background=layout.COLOR_PEDAL_FRAME, foreground=layout.COLOR_FOREGROUND)
        self.style.map('TCheckbutton', background=[('active', layout.COLOR_BACKGROUND)])

    def create_main_frame_with_scroll(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(main_frame, bg=layout.COLOR_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.bind_all("<MouseWheel>", self._on_mousewheel, "+")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_pedals(self):
        """Cria todos os pedais de forma genérica a partir da configuração."""
        initial_order = audio_interface.get_chain_order()
        for effect_name in initial_order:
            if effect_name not in PEDAL_CONFIGS:
                continue
            
            config = PEDAL_CONFIGS[effect_name]
            
            frame_container = ttk.LabelFrame(self.scroll_frame, text=config.get('title', effect_name.capitalize()))
            frame_container.effect_name = effect_name
            
            # CORREÇÃO: A classe genérica PedalControl cria TODOS os pedais.
            # O tratamento especial para 'equalizer' foi removido para resolver o NameError.
            widget = PedalControl(frame_container, effect_name, config)
            widget.pack(fill="x", expand=True, padx=5, pady=5)
            
            self.pedal_widgets.append(widget)
            self.pedal_frames.append(frame_container)

    def layout_pedals(self):
        for i, frame in enumerate(self.pedal_frames):
            row = i // layout.PEDALBOARD_COLUMNS
            col = i % layout.PEDALBOARD_COLUMNS
            frame.grid(row=row, column=col, padx=layout.PEDAL_PADDING_X, pady=layout.PEDAL_PADDING_Y, sticky="nsew")

    def on_pedal_reorder(self):
        new_order = [p.effect_name for p in self.pedal_frames]
        audio_interface.set_chain_order(new_order)
        self.layout_pedals()

    def open_asio_panel(self):
        if not self.stream_running:
            messagebox.showinfo("Aviso", "Por favor, inicie o stream de áudio primeiro para configurar o painel ASIO.")
            return

        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ASIO4ALL v2", "a4apanel.exe"),
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ASIO4ALL v2", "a4apanel64.exe"),
        ]
        found_path = next((path for path in possible_paths if os.path.exists(path)), None)
        
        if found_path:
            try:
                subprocess.Popen([found_path])
            except Exception as e:
                messagebox.showerror("Erro ao Abrir", f"Não foi possível iniciar o painel ASIO:\n{e}")
        else:
            messagebox.showwarning("Não Encontrado", 
                                 "O painel do ASIO4ALL (a4apanel.exe) não foi encontrado.")

    def create_audio_controls(self):
        frame = ttk.LabelFrame(self, text="Controle de Áudio", padding=10)
        frame.pack(fill='x', padx=10, pady=(5,0))
        frame.columnconfigure((1, 3), weight=1)
        
        ttk.Label(frame, text="Entrada:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.input_cb = ttk.Combobox(frame, state="readonly", width=25)
        self.input_cb.grid(row=0, column=1, sticky="ew")
        ttk.Label(frame, text="Saída:").grid(row=0, column=2, padx=(10, 5), sticky="w")
        self.output_cb = ttk.Combobox(frame, state="readonly", width=25)
        self.output_cb.grid(row=0, column=3, sticky="ew")
        self.populate_devices()
        
        control_frame = ttk.Frame(frame)
        control_frame.grid(row=1, column=0, columnspan=4, pady=(10,0), sticky="ew")
        
        self.start_btn = ttk.Button(control_frame, text="▶ Iniciar", command=self.start_stream)
        self.start_btn.pack(side="left", padx=(0,10))
        self.stop_btn = ttk.Button(control_frame, text="■ Parar", command=self.stop_stream, state="disabled")
        self.stop_btn.pack(side="left")
        self.asio_btn = ttk.Button(control_frame, text="Painel ASIO", command=self.open_asio_panel)
        self.asio_btn.pack(side="left", padx=(20, 0))
        self.record_btn = ttk.Button(control_frame, text="● Gravar", command=self.toggle_recording)
        self.record_btn.pack(side="left", padx=(10, 0))
        
        self.master_volume_var = tk.DoubleVar(value=1.0)
        master_slider = ttk.Scale(control_frame, from_=0, to=1.5, orient="horizontal", variable=self.master_volume_var, command=lambda v: audio_interface.set_master_volume(v))
        master_slider.pack(side="right", padx=(10, 0), fill='x', expand=True)
        ttk.Label(control_frame, text="Volume Master:").pack(side="right")
        
        self.tuner_label = ttk.Label(frame, text="Afinador: --", font=layout.FONT_TUNER, anchor="center")
        self.tuner_label.grid(row=2, column=0, columnspan=4, pady=(10,0), sticky="ew")

    def populate_devices(self):
        devices = audio_interface.list_active_devices()
        in_devs = [d['name'] for d in devices if d['max_input_channels'] > 0]
        out_devs = [d['name'] for d in devices if d['max_output_channels'] > 0]
        self.input_cb['values'] = in_devs
        self.output_cb['values'] = out_devs
        asio_in_device = next((d for d in in_devs if 'asio' in d.lower()), None)
        asio_out_device = next((d for d in out_devs if 'asio' in d.lower()), None)
        if asio_in_device and asio_out_device:
            self.input_cb.set(asio_in_device)
            self.output_cb.set(asio_out_device)
        else:
            try:
                default_in = audio_interface.sd.query_devices(kind='input')['name']
                default_out = audio_interface.sd.query_devices(kind='output')['name']
                self.input_cb.set(default_in)
                self.output_cb.set(default_out)
            except Exception:
                if in_devs: self.input_cb.current(0)
                if out_devs: self.output_cb.current(0)

    def create_menu(self):
        menubar = tk.Menu(self)
        audio_menu = tk.Menu(menubar, tearoff=0)
        audio_menu.add_checkbutton(label="Ativar Afinador", variable=self.tuner_enabled_var, command=self.toggle_tuner)
        audio_menu.add_separator()
        audio_menu.add_command(label="Abrir Painel ASIO", command=self.open_asio_panel)
        menubar.add_cascade(label="Áudio", menu=audio_menu)
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Salvar Preset", command=self.save_config)
        config_menu.add_command(label="Carregar Preset", command=self.load_config)
        menubar.add_cascade(label="Presets", menu=config_menu)
        self.config(menu=menubar)

    def toggle_tuner(self):
        audio_interface.toggle_effect('tuner', self.tuner_enabled_var.get())

    def update_tuner_display(self):
        if self.tuner_enabled_var.get() and self.stream_running:
            try:
                note, octave, cents = audio_interface.tuner_queue.get_nowait()
                self.tuner_label.config(text=f"{note}{octave} ({cents:+.1f} cents)" if note else "Afinador: --")
            except Empty:
                pass
        else:
            self.tuner_label.config(text="Afinador: --")
        self.after(100, self.update_tuner_display)

    def start_stream(self):
        try:
            input_name = self.input_cb.get()
            output_name = self.output_cb.get()
            if not input_name or not output_name:
                messagebox.showerror("Erro", "Dispositivos de áudio devem ser selecionados.")
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
        if self.is_recording: self.toggle_recording(force_stop=True)

    def save_config(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Presets", "*.json")])
        if not path: return
        try:
            with open(path, 'w') as f:
                json.dump(audio_interface.get_full_state(), f, indent=2)
            messagebox.showinfo("Salvo", "Preset salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar preset: {e}")
    
    def load_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Presets", "*.json")])
        if not path: return
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            audio_interface.set_full_state(config)
            self.after(50, self.sync_all_pedals)
            messagebox.showinfo("Carregado", "Preset carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar preset: {e}")

    def sync_all_pedals(self):
        master_vol = audio_interface.get_param_value('master_volume', 'level', 1.0)
        self.master_volume_var.set(master_vol)
        for widget in self.pedal_widgets:
            widget.sync_with_state()

    def toggle_recording(self, force_stop=False):
        if force_stop:
            self.is_recording = True
        
        self.is_recording = not self.is_recording
        if self.is_recording:
            filepath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
            if not filepath:
                self.is_recording = False
                return
            if audio_interface.start_recording(filepath):
                self.record_btn.config(text="■ Parar Gravação")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a gravação.")
                self.is_recording = False
        else:
            audio_interface.stop_recording()
            self.record_btn.config(text="● Gravar")

    def on_closing(self):
        self.stop_stream()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()