# backend/effects/pedal_control.py

import tkinter as tk
from tkinter import ttk
from backend import audio_interface

class PedalControl(ttk.Frame):
    """
    Cria a interface gráfica para um único pedal. Agora, ele sabe a que
    cadeia de efeitos (ex: 'instrument' ou 'voice') pertence.
    """
    def __init__(self, master, chain_type, effect_name, config):
        super().__init__(master, padding=10)
        self.chain_type = chain_type  # NOVO: Guarda o tipo de cadeia ('instrument' ou 'voice')
        self.effect_name = effect_name
        self.config = config
        
        self.parent_frame = master
        self.param_vars = {}

        # A chamada agora inclui o chain_type
        self.enabled_var = tk.BooleanVar(value=audio_interface.is_effect_enabled(self.chain_type, self.effect_name))
        self.enable_button = ttk.Checkbutton(
            self,
            text="Ativado",
            variable=self.enabled_var,
            command=self.toggle_effect
        )
        self.enable_button.pack(anchor='w', pady=(0, 10))

        params_config = self.config.get('params', {})
        for param_name, param_config in params_config.items():
            param_type = param_config.get('type')
            
            frame = ttk.Frame(self)
            frame.pack(fill='x', expand=True, pady=2)
            
            label = ttk.Label(frame, text=param_config.get('label', param_name), width=15)
            label.pack(side='left')

            default_value = audio_interface.get_param_value(self.chain_type, self.effect_name, param_name, param_config.get('default'))

            if param_type == 'slider':
                variable = tk.DoubleVar(value=default_value)
                slider = ttk.Scale(
                    frame,
                    from_=param_config.get('min', 0),
                    to=param_config.get('max', 1),
                    orient='horizontal',
                    variable=variable,
                    command=lambda v, name=param_name: self.update_param(name, float(v))
                )
                slider.pack(side='left', fill='x', expand=True)
                self.param_vars[param_name] = variable

            elif param_type in ['combo', 'dropdown']:
                variable = tk.StringVar(value=default_value)
                combobox = ttk.Combobox(frame, textvariable=variable, values=param_config.get('options', []), state="readonly")
                combobox.pack(side='left', fill='x', expand=True)
                combobox.set(default_value)
                combobox.bind("<<ComboboxSelected>>", lambda event, name=param_name: self.update_param(name, event.widget.get()))
                self.param_vars[param_name] = variable
        
        self._update_visual_state()

    def toggle_effect(self):
        """Notifica o backend sobre a mudança de estado, especificando a cadeia."""
        is_enabled = self.enabled_var.get()
        audio_interface.toggle_effect(self.chain_type, self.effect_name, is_enabled)
        self._update_visual_state()

    def update_param(self, param_name, value):
        """Notifica o backend sobre a mudança de um parâmetro, especificando a cadeia."""
        audio_interface.update_param(self.chain_type, self.effect_name, param_name, value)
    
    def _update_visual_state(self):
        """Muda o estado visual do pedal (borda destacada)."""
        if self.enabled_var.get():
            self.parent_frame.state(['active'])
        else:
            self.parent_frame.state(['!active'])

    def sync_with_state(self):
        """Sincroniza a UI com o estado do backend ao carregar presets."""
        is_enabled = audio_interface.is_effect_enabled(self.chain_type, self.effect_name)
        self.enabled_var.set(is_enabled)
        
        for name, var in self.param_vars.items():
            default_value = self.config.get('params', {}).get(name, {}).get('default')
            value = audio_interface.get_param_value(self.chain_type, self.effect_name, name, default_value)
            if value is not None:
                var.set(value)
        
        self._update_visual_state()
