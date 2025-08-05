import numpy as np
import cpp_effects

from effects.tuner import detect_pitch, freq_to_note
# Se quiser, importe outras funções Python dos efeitos que não tem no C++

class AudioProcessor:

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

        # Mantém o estado atual dos pedais recebido do frontend
        self.effects_state = {
            'overdrive': {'enabled': False, 'params': {}},
            'distortion': {'enabled': False, 'params': {}},
            'equalizer': {'enabled': False, 'params': {}},
            'delay': {'enabled': False, 'params': {}},
            'reverb': {'enabled': False, 'params': {}},
            'chorus': {'enabled': False, 'params': {}},
            'tremolo': {'enabled': False, 'params': {}},
            'wahwah': {'enabled': False, 'params': {}},
            'tuner': {'enabled': False, 'params': {}},
            'puresky': {'enabled': False, 'params': {}},
            'compressor': {'enabled': False, 'params': {}},
            'flanger_bf2': {'enabled': False, 'params': {}},    
            'BehringerUf100Flanger': {'enabled': False, 'params': {}},   
            'afinador': {'enabled': False, 'params': {}},
            'vintage_overdrive': {'enabled': False, 'params': {}},
            'ultra_flanger': {'enabled': False, 'params': {}},
            'CaineOldSchoolReverb': {'enabled': False, 'params': {}}
        }

    def update_state(self, data):
        """
        Atualiza o estado de um efeito com base nos dados de controle do frontend.
        Espera receber um dict com chaves 'effect', 'enabled' e 'params'.
        """
        effect = data.get('effect')
        if effect in self.effects_state:
            self.effects_state[effect]['enabled'] = data.get('enabled', False)
            self.effects_state[effect]['params'] = data.get('params', {})

    def process_audio(self, audio_buffer: np.ndarray) -> np.ndarray:
        """
        Aplica a cadeia de efeitos ao buffer de áudio.
        audio_buffer: numpy array do tipo float32 ou float64.
        Retorna um novo numpy array processado.
        """
        if self.effects_state['CaineOldSchoolReverb']['enabled']:
            params = self.effects_state['CaineOldSchoolReverb']['params']
            block_size = len(audio_buffer)

            processed_buffer = python_effects.apply_caine_old_school_reverb(
                processed_buffer,
                self.sample_rate,
                block_size, # <--- ADICIONE ESTA LINHA
                **params
            )

        return processed_buffer
        # Silencia o áudio se o afinador estiver ativo
        if effect_name == 'tuner':
    note_data = instance.detect_pitch(audio_buffer)
    self.tuner_note = note_data
else:
    processed_buffer = instance.apply(processed_buffer, **params)
        processed_buffer = audio_buffer  
        
def get_tuner_note(self):
    return self.tuner_note


        # 1. Overdrive
        if self.effects_state['overdrive']['enabled']:
            params = self.effects_state['overdrive']['params']
            processed_buffer = cpp_effects.apply_overdrive(
                processed_buffer,
                float(params.get('ganho', 5.0)),
                float(params.get('tonalidade', 5.0)),
                float(params.get('level', 7.0))
            )

        # 2. Distortion
        if self.effects_state['distortion']['enabled']:
            params = self.effects_state['distortion']['params']
            processed_buffer = cpp_effects.apply_distortion(
                processed_buffer,
                float(params.get('drive', 5.0)),
                float(params.get('level', 5.0))
            )

        # 3. Equalizer
        if self.effects_state['equalizer']['enabled']:
            params = self.effects_state['equalizer']['params']
            bands = params.get('bands', [])
            if isinstance(bands, (list, tuple)) and len(bands) > 0:
                processed_buffer = cpp_effects.apply_equalizer(processed_buffer, bands)

        # 4. Chorus
        if self.effects_state['chorus']['enabled']:
            params = self.effects_state['chorus']['params']
            processed_buffer = cpp_effects.apply_chorus(
                processed_buffer,
                str(params.get('mode', 'default')),
                float(params.get('rate', 1.0)),
                float(params.get('width', 0.5)),
                float(params.get('intensity', 0.5)),
                float(params.get('tone', 5.0))
            )

        # 5. Tremolo
        if self.effects_state['tremolo']['enabled']:
            params = self.effects_state['tremolo']['params']
            processed_buffer = cpp_effects.apply_tremolo(
                processed_buffer,
                float(params.get('rate', 5.0)),
                float(params.get('depth', 0.5))
            )

        # 6. Delay
        if self.effects_state['delay']['enabled']:
            params = self.effects_state['delay']['params']
            processed_buffer = cpp_effects.apply_delay(
                processed_buffer,
                float(params.get('time_ms', 500)),
                float(params.get('feedback', 0.5)),
                float(params.get('mix', 0.5))
            )

        # 7. Reverb
        if self.effects_state['reverb']['enabled']:
            params = self.effects_state['reverb']['params']
            processed_buffer = cpp_effects.apply_reverb(
                processed_buffer,
                float(params.get('mix', 0.5)),
                float(params.get('size', 0.5)),
                float(params.get('decay', 0.5))
            )

        # 8. Wahwah
        if self.effects_state['wahwah']['enabled']:
            params = self.effects_state['wahwah']['params']
            processed_buffer = cpp_effects.apply_wahwah(
                processed_buffer,
                float(params.get('rate', 1.0)),
                float(params.get('min_freq', 500)),
                float(params.get('max_freq', 1500)),
                float(params.get('q', 0.5))
            )
            
            # 9. Behringer UF100 Flanger
if self.effects_state['BehringerUf100Flanger']['enabled']:
    params = self.effects_state['BehringerUf100Flanger']['params']
    processed_buffer = python_effects.apply_behringer_uf100_flanger(
        processed_buffer,
        float(params.get('manual', 0.5)),
        float(params.get('depth', 0.5)),
        float(params.get('rate', 1.0)),
        float(params.get('resonance', 0.3))
    )
    # 10. Boss BF-2 Flanger
if self.effects_state['flanger_bf2']['enabled']:
    params = self.effects_state['flanger_bf2']['params']
    processed_buffer = python_effects.apply_boss_bf2_flanger(
        processed_buffer,
        float(params.get('manual', 0.6)),
        float(params.get('depth', 0.7)),
        float(params.get('rate', 1.2)),
        float(params.get('resonance', 0.4))
    )
    # 11. Caine Old School Reverb
if self.effects_state['CaineOldSchoolReverb']['enabled']:
    params = self.effects_state['CaineOldSchoolReverb']['params']
    processed_buffer = python_effects.apply_CaineOldSchoolReverb(
        processed_buffer,
        mode=params.get('mode', 'room'),
        decay=float(params.get('decay', 0.7)),
        mix=float(params.get('mix', 0.5)),
        tone=float(params.get('tone', 0.5))
    )

        return processed_buffer

    def get_tuner_data(self, audio_buffer: np.ndarray):
        """
        Analisa o áudio e retorna os dados de afinação se o afinador estiver ativo.
        Retorna uma tupla (nota, oitava, cents) ou None.
        """
        if self.effects_state['tuner']['enabled']:
            # Lembre-se que seu sample_rate pode precisar ser passado aqui, ex: 48000
            freq = detect_pitch(audio_buffer, self.sample_rate) 
            # Assumindo que freq_to_note retorna (nota, oitava, cents)
            return freq_to_note(freq) 
        return None
    effect_instances = {
    'CaineOldSchoolReverb': Reverb(sample_rate=48000) # Assumindo sample_rate de 48000
}

def apply_CaineOldSchoolReverb(
    audio_buffer: np.ndarray,
    sample_rate: int, # Adicionamos sample_rate como parâmetro
    mode: str = 'room',
    decay: float = 0.7,
    mix: float = 0.5,
    tone: float = 0.5
) -> np.ndarray:
    """
    Aplica um efeito de Reverb customizado usando a engine do pedalboard.
    """
    # 1. Pega a instância do nosso reverb
    reverb_effect = effect_instances.get('CaineOldSchoolReverb')

    # Garante que o sample_rate do efeito esteja correto
    if reverb_effect.sample_rate != sample_rate:
        reverb_effect.sample_rate = sample_rate

    # 2. Mapeia os seus parâmetros para os controles do Reverb
    # Mapeia 'mode' para o tamanho da sala (room_size)
    if mode == 'room':
        reverb_effect.room_size = 0.60
    elif mode == 'hall':
        reverb_effect.room_size = 0.80
    elif mode == 'church':
        reverb_effect.room_size = 0.95
    
    # Mapeia 'tone' para 'damping' (controle de agudos no reverb)
    reverb_effect.damping = 1.0 - tone

    # 'decay' não tem um mapeamento direto, mas podemos usá-lo para
    # influenciar o tamanho da sala junto com o modo.
    reverb_effect.room_size *= (0.5 + decay) # Ajusta o tamanho da sala com base no decay

    # Mapeia 'mix' para os níveis de dry/wet
    reverb_effect.wet_level = mix
    reverb_effect.dry_level = 1.0 - mix

    # 3. Processa o áudio com o efeito
    # Usamos process(), que modifica o buffer diretamente (in-place)
    processed_buffer = reverb_effect.process(audio_buffer.copy(), reset=False) # Copiamos para não modificar o original
    
    return processed_buffer
Passo 3: Ajustar a Chamada no AudioProcessor
Seu código AudioProcessor está quase perfeito. A única pequena mudança necessária é passar o self.sample_rate para a nova função.

No seu método process_audio, localize o bloco do CaineOldSchoolReverb e ajuste-o assim:

Python

# Na classe AudioProcessor, método process_audio

# ... (outros efeitos acima)

# 11. Caine Old School Reverb
if self.effects_state['CaineOldSchoolReverb']['enabled']:
    params = self.effects_state['CaineOldSchoolReverb']['params']
    
    # A ÚNICA MUDANÇA É AQUI: Adicionar o sample_rate
    processed_buffer = python_effects.apply_CaineOldSchoolReverb(
        processed_buffer,
        self.sample_rate,  # <--- Adicione esta linha
        mode=params.get('mode', 'room'),
        decay=float(params.get('decay', 0.7)),
        mix=float(params.get('mix', 0.5)),
        tone=float(params.get('tone', 0.5))
    )

return processed_buffer