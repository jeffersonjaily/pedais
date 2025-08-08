# ui/shortcut_window.py

import tkinter as tk
from tkinter import ttk

class ShortcutWindow(tk.Toplevel):
    """
    Uma nova janela para o utilizador definir os atalhos de teclado para cada pedal.
    Agora exibe os pedais separados por cadeia (instrumento e voz).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Definir Atalhos dos Pedais")
        self.geometry("400x600")
        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Clique na caixa e pressione a tecla desejada para o atalho.").pack(pady=(0, 15))

        self.entries = {}
        # Itera sobre os pedais de instrumento e de voz
        for chain_type in ['instrument', 'voice']:
            # Adiciona um título para cada secção
            ttk.Label(main_frame, text=f"--- {chain_type.capitalize()} ---", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5), anchor='w')
            
            for pedal_widget in self.parent.pedal_widgets[chain_type]:
                effect_name = pedal_widget.effect_name
                
                row_frame = ttk.Frame(main_frame)
                row_frame.pack(fill="x", pady=2)
                
                label = ttk.Label(row_frame, text=f"{effect_name.capitalize()}:", width=20)
                label.pack(side="left")
                
                entry_var = tk.StringVar()
                # Procura se já existe um atalho definido para este pedal
                for key, effect in self.parent.shortcut_map.items():
                    if effect == effect_name:
                        entry_var.set(key)
                        break

                entry = ttk.Entry(row_frame, textvariable=entry_var, width=15)
                entry.pack(side="left", fill="x", expand=True)
                # Vincula o evento de pressionar uma tecla à função que captura o nome da tecla
                entry.bind("<KeyPress>", self.on_key_press)
                
                self.entries[effect_name] = entry_var

        save_button = ttk.Button(main_frame, text="Salvar e Fechar", command=self.save_and_close)
        save_button.pack(pady=20)

    def on_key_press(self, event):
        """Captura o nome da tecla pressionada e a exibe na caixa de texto."""
        event.widget.delete(0, tk.END)
        event.widget.insert(0, event.keysym)
        return "break"

    def save_and_close(self):
        """Atualiza o mapa de atalhos da aplicação principal e salva em ficheiro."""
        new_shortcut_map = {}
        for effect_name, entry_var in self.entries.items():
            key = entry_var.get()
            if key:
                # Evita atalhos duplicados
                if key in new_shortcut_map:
                    messagebox.showwarning("Atalho Duplicado", f"A tecla '{key}' já está a ser usada. O atalho para '{effect_name}' não foi salvo.")
                    continue
                new_shortcut_map[key] = effect_name
        
        self.parent.shortcut_map = new_shortcut_map
        self.parent._save_shortcuts()
        self.destroy()
