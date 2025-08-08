import numpy as np
import cpp_effects
import python_effects # Presumindo que seus efeitos em Python estão neste módulo

from effects.tuner import yin_detect_pitch, freq_to_note

class AudioProcessor:
    """
    Versão refatorada que gerencia a cadeia de efeitos de forma dinâmica e flexível.
    """
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.tuner_note = None
        
        # 1. MAPA DE EFEITOS: O "cérebro" da nossa arquitetura.
        #    Associa o nome de um efeito à sua função de processamento e parâmetros.
        self._effects_map = self._initialize_effects_map()

        # 2. ORDEM DA CADEIA: Esta lista controla a ordem de processamento.
        #    Pode ser alterada dinamicamente pela UI!
        self.chain_order = list(self._effects_map.keys())

        # 3. ESTADO DOS PARÂMETROS: Guarda os valores dos knobs.
        self.params_state = {
            name: {'enabled': False, 'params': config.get('default_params', {})}
            for name, config in self._effects_map.items()
        }

    def _initialize_effects_map(self):
        """
        Centraliza a definição de todos os efeitos disponíveis.
        """
        return {
            'overdrive': {
                'processor': cpp_effects.apply_overdrive,
                'default_params': {'ganho': 5.0, 'tonalidade': 5.0, 'level': 7.0}
            },
            'distortion': {
                'processor': cpp_effects.apply_distortion,
                'default_params': {'drive': 5.0, 'level': 5.0}
            },
            'equalizer': {
                'processor': cpp_effects.apply_equalizer,
                'default_params': {'bands': []}
            },
            'chorus': {
                'processor': cpp_effects.apply_chorus,
                'default_params': {'mode': 'default', 'rate': 1.0, 'width': 0.5, 'intensity': 0.5, 'tone': 5.0}
            },
            'CaineOldSchoolReverb': {
                'processor': python_effects.apply_caine_old_school_reverb,
                'default_params': {'mode': 'room', 'decay': 0.7, 'mix': 0.5, 'tone': 0.5},
                'requires_extra_args': True # Flag para efeitos que precisam de mais do que apenas o buffer
            },
            'tuner': {
                'processor': None # O afinador não processa áudio, apenas analisa.
            }
            # Adicione TODOS os seus outros efeitos aqui neste formato
        }

    def update_state(self, data):
        """Atualiza o estado de um efeito."""
        effect = data.get('effect')
        if effect in self.params_state:
            self.params_state[effect]['enabled'] = data.get('enabled', False)
            if 'params' in data:
                # Atualiza apenas os parâmetros recebidos
                for param, value in data['params'].items():
                    self.params_state[effect]['params'][param] = value

    def set_chain_order(self, new_order: list):
        """Permite que a UI altere a ordem de processamento dos efeitos."""
        self.chain_order = new_order

    def process_audio(self, audio_buffer: np.ndarray) -> np.ndarray:
        """
        Aplica a cadeia de efeitos na ordem definida por self.chain_order.
        """
        if self.params_state.get('tuner', {}).get('enabled'):
            self.get_tuner_data(audio_buffer)
            return np.zeros_like(audio_buffer)

        processed_buffer = audio_buffer.copy()

        # Loop genérico que aplica os efeitos na ordem correta
        for effect_name in self.chain_order:
            state = self.params_state.get(effect_name)
            
            if state and state['enabled']:
                config = self._effects_map[effect_name]
                processor_func = config.get('processor')
                
                if processor_func:
                    params = state['params']
                    
                    # Lógica para efeitos que precisam de argumentos extras
                    if config.get('requires_extra_args'):
                        extra_args = {
                            'sample_rate': self.sample_rate,
                            'block_size': len(audio_buffer)
                        }
                        # Combina os parâmetros da UI com os argumentos extras
                        final_params = {**params, **extra_args}
                        processed_buffer = processor_func(processed_buffer, **final_params)
                    else:
                        processed_buffer = processor_func(processed_buffer, **params)

        return processed_buffer

    def get_tuner_data(self, audio_buffer: np.ndarray):
        """Analisa o áudio e guarda a nota detectada."""
        freq = yin_detect_pitch(audio_buffer, self.sample_rate) 
        self.tuner_note = freq_to_note(freq)
        return self.tuner_note
    
    def get_last_tuner_note(self):
        """Retorna a última nota que foi detectada."""
        return self.tuner_note
