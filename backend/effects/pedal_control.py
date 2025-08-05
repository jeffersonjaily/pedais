# Arquivo: backend/effects/pedal_control.py

import tkinter as tk
from tkinter import ttk
from backend import audio_interface # ou qualquer que seja seu módulo de comunicação

class PedalControl(ttk.Frame):
    """
    Cria a interface gráfica para um único pedal, com base em sua configuração.
    Esta classe cria os sliders, checkboxes e dropdowns necessários.
    """
    def __init__(self, master, effect_name, config):
        super().__init__(master, padding=10)
        self.effect_name = effect_name
        self.config = config
        
        self.param_vars = {}

        # Checkbox para ativar/desativar o pedal
        self.enabled_var = tk.BooleanVar(value=audio_interface.is_effect_enabled(self.effect_name))
        self.enable_button = ttk.Checkbutton(
            self,
            text="Ativado",
            variable=self.enabled_var,
            command=self.toggle_effect
        )
        self.enable_button.pack(anchor='w', pady=(0, 10))

        # Loop que cria os controles (sliders, dropdowns, etc.)
        params_config = self.config.get('params', {}) # CORREÇÃO: Usar {} como padrão para dicionários
        for param_name, param_config in params_config.items():
            param_type = param_config.get('type')
            
            frame = ttk.Frame(self)
            frame.pack(fill='x', expand=True, pady=2)
            
            label = ttk.Label(frame, text=param_config.get('label', param_name), width=15)
            label.pack(side='left')

            if param_type == 'slider':
                variable = tk.DoubleVar(value=param_config.get('default', 0))
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
                default_value = param_config.get('default', '')
                options = param_config.get('options', [])
                variable = tk.StringVar(value=default_value)
                
                combobox = ttk.Combobox(
                    frame,
                    textvariable=variable,
                    values=options,
                    state="readonly"
                )
                combobox.pack(side='left', fill='x', expand=True)
                combobox.set(default_value)
                combobox.bind(
                    "<<ComboboxSelected>>",
                    lambda event, name=param_name: self.update_param(name, event.widget.get())
                )
                self.param_vars[param_name] = variable

            elif param_type == 'checkbox':
                variable = tk.BooleanVar(value=param_config.get('default', False))
                checkbox = ttk.Checkbutton(
                    frame,
                    variable=variable,
                    command=lambda name=param_name: self.update_param(name, variable.get())
                )
                checkbox.pack(side='left')
                self.param_vars[param_name] = variable

    def toggle_effect(self):
        """Notifica o backend que o pedal foi ativado ou desativado."""
        is_enabled = self.enabled_var.get()
        audio_interface.toggle_effect(self.effect_name, is_enabled)

    def update_param(self, param_name, value):
        """Notifica o backend que um parâmetro do pedal mudou."""
        # --- CORREÇÃO ESTÁ AQUI ---
        # O nome da função correta no seu backend é 'update_param'.
        audio_interface.update_param(self.effect_name, param_name, value)
    
    def sync_with_state(self):
        """
        Sincroniza os controles da UI com o estado atual do backend.
        """
        # Esta função precisa ser chamada ao carregar um preset.
        # Vamos pegar o estado diretamente do backend.
        is_enabled = audio_interface.is_effect_enabled(self.effect_name)
        self.enabled_var.set(is_enabled)
        
        for name, var in self.param_vars.items():
            default_value = self.config['params'][name].get('default')
            value = audio_interface.get_param_value(self.effect_name, name, default_value)
            if value is not None:
                var.set(value)