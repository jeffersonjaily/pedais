import tkinter as tk
from tkinter import ttk

import backend.voz.audio_interface as audio_interface

class PedalControl(ttk.Frame):
    def __init__(self, parent, effect_name, effect_config):
        super().__init__(parent)
        self.effect_name = effect_name
        self.effect_config = effect_config

        # Inicializa o estado ativado/desativado
        self.enabled = tk.BooleanVar(value=audio_interface.is_effect_enabled(effect_name))

        self.create_widgets()
        self.load_params()

    def create_widgets(self):
        # Checkbox para ativar/desativar efeito
        self.chk_enabled = ttk.Checkbutton(
            self,
            text=self.effect_config.get('title', self.effect_name),
            variable=self.enabled,
            command=self.on_toggle
        )
        self.chk_enabled.pack(side='left', padx=5, pady=5)

        self.param_controls = {}
        params = self.effect_config.get('params', {})
        for param_key, param_info in params.items():
            frame = ttk.Frame(self)
            frame.pack(side='left', padx=5)

            # Label amigável do parâmetro
            label = ttk.Label(frame, text=param_info.get('label', param_key))
            label.pack()

            param_type = param_info.get('type', 'slider')

            if param_type == 'slider':
                var = tk.DoubleVar(value=param_info.get('default', 0.0))
                slider = ttk.Scale(
                    frame,
                    from_=param_info.get('min', 0.0),
                    to=param_info.get('max', 1.0),
                    orient='horizontal',
                    variable=var,
                    command=lambda val, p=param_key: self.on_param_change(p, val)
                )
                slider.pack()

                # Label para mostrar valor atual
                value_label = ttk.Label(frame, text=f"{var.get():.2f}")
                value_label.pack()

                # Atualiza o texto do label quando o slider é movido
                def on_slide(event, slider=slider, label=value_label):
                    label.config(text=f"{slider.get():.2f}")
                slider.bind("<Motion>", on_slide)

                self.param_controls[param_key] = {
                    'widget': slider,
                    'var': var,
                    'value_label': value_label,
                    'type': 'slider',
                }

            elif param_type == 'dropdown' or param_type == 'combobox':
                var = tk.StringVar(value=param_info.get('default', ''))
                combobox = ttk.Combobox(
                    frame,
                    values=param_info.get('options', []),
                    textvariable=var,
                    state='readonly'
                )
                combobox.pack()

                # Quando seleciona algo no combobox, atualiza parâmetro
                def on_select(event, p=param_key, v=var):
                    audio_interface.update_param(self.effect_name, p, v.get())
                combobox.bind("<<ComboboxSelected>>", on_select)

                self.param_controls[param_key] = {
                    'widget': combobox,
                    'var': var,
                    'type': 'combobox',
                }

            else:
                # Caso tipo não reconhecido, pode-se ignorar ou criar algo básico
                pass

    def on_toggle(self):
        audio_interface.toggle_effect(self.effect_name, self.enabled.get())

    def on_param_change(self, param_key, val):
        try:
            value = float(val)
            audio_interface.update_param(self.effect_name, param_key, value)
            control = self.param_controls.get(param_key)
            if control and control['type'] == 'slider':
                control['value_label'].config(text=f"{value:.2f}")
        except ValueError:
            pass  # Pode ignorar valores inválidos aqui

    def load_params(self):
        # Atualiza estado e parâmetros vindos do backend
        state = audio_interface.get_effect_state(self.effect_name)
        self.enabled.set(state.get('enabled', False))
        params = state.get('params', {})

        for param_key, control in self.param_controls.items():
            if param_key in params:
                val = params[param_key]
                if control['type'] == 'slider':
                    try:
                        control['var'].set(float(val))
                        control['value_label'].config(text=f"{float(val):.2f}")
                    except Exception:
                        pass
                elif control['type'] == 'combobox':
                    control['var'].set(str(val))
