# ui/Mini_play.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from backend import audio_interface

class MiniPlayer(ttk.Frame):
    """
    Um widget que encapsula toda a funcionalidade do leitor de áudio.
    """
    def __init__(self, master):
        super().__init__(master, padding=(0, 10, 0, 0))
        self.master = master
        self._seeking = False

        # --- Criação dos Widgets do Leitor ---
        self.load_track_btn = ttk.Button(self, text="Carregar Áudio", command=self._load_track_dialog)
        self.load_track_btn.pack(side="left")

        self.play_pause_var = tk.StringVar(value="▶")
        self.play_pause_btn = ttk.Button(self, textvariable=self.play_pause_var, command=self._toggle_playback, width=3)
        self.play_pause_btn.pack(side="left", padx=(10, 0))

        self.stop_player_btn = ttk.Button(self, text="■", command=self._stop_playback, width=3)
        self.stop_player_btn.pack(side="left", padx=(5, 10))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_slider = ttk.Scale(self, from_=0, to=1.0, orient="horizontal", variable=self.progress_var)
        self.progress_slider.pack(side="left", fill='x', expand=True)
        self.progress_slider.bind("<ButtonPress-1>", self._on_seek_press)
        self.progress_slider.bind("<B1-Motion>", self._on_seek_drag)
        self.progress_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.track_volume_var = tk.DoubleVar(value=0.7)
        track_slider = ttk.Scale(self, from_=0, to=1.5, orient="horizontal", variable=self.track_volume_var, command=self._set_backing_track_volume, length=100)
        track_slider.pack(side="right", padx=(10, 0))
        ttk.Label(self, text="Volume:").pack(side="right")

        # Inicia o loop de atualização da barra de progresso
        self._update_progress_bar()

    def _load_track_dialog(self):
        """Abre uma janela para o utilizador selecionar um ficheiro de áudio."""
        filepath = filedialog.askopenfilename(
            title="Selecionar Ficheiro de Áudio",
            filetypes=[("Ficheiros de Áudio", "*.wav *.flac *.mp3 *.ogg *.aiff"), ("Todos os ficheiros", "*.*")]
        )
        if filepath:
            if audio_interface.load_backing_track(filepath):
                messagebox.showinfo("Sucesso", "Ficheiro de áudio carregado.")
                self.play_pause_var.set("▶")
            else:
                messagebox.showerror("Erro", "Não foi possível carregar o ficheiro. Verifique o formato.")

    def _toggle_playback(self):
        """Callback para o botão de play/pause."""
        new_state = audio_interface.toggle_playback()
        if new_state == 'playing': self.play_pause_var.set("❚❚")
        else: self.play_pause_var.set("▶")
            
    def _stop_playback(self):
        """Callback para o botão de stop."""
        audio_interface.stop_playback()
        self.play_pause_var.set("▶")
        self.progress_var.set(0)

    def _set_backing_track_volume(self, value):
        """Callback para o slider de volume da backing track."""
        audio_interface.set_backing_track_volume(float(value))

    def _update_progress_bar(self):
        """Atualiza a posição da barra de progresso."""
        if not self._seeking:
            info = audio_interface.get_playback_info()
            position, duration = info['position'], info['duration']
            if duration > 0:
                self.progress_var.set(position / duration)
                if self.play_pause_var.get() == "❚❚" and audio_interface.get_playback_state() == 'stopped':
                     self.play_pause_var.set("▶")
            else:
                self.progress_var.set(0)
        self.after(200, self._update_progress_bar)

    def _on_seek_press(self, event):
        self._seeking = True
        self._set_playback_from_slider()

    def _on_seek_drag(self, event):
        if self._seeking:
            # Esta técnica força a atualização do valor do slider durante o arrasto
            self.progress_slider.event_generate("<ButtonRelease-1>", x=event.x, y=event.y)
            self.progress_slider.event_generate("<ButtonPress-1>", x=event.x, y=event.y)
            self._set_playback_from_slider()

    def _on_seek_release(self, event):
        self._seeking = False
        self._set_playback_from_slider()

    def _set_playback_from_slider(self):
        seek_ratio = self.progress_var.get()
        audio_interface.set_playback_position(seek_ratio)
