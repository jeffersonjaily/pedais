# backend/effects_config.py

PEDAL_CONFIGS = {
    # --- Efeitos existentes ---
    'wahwah': {
        'title': 'Auto-Wah',
        'params': {
            'rate': {'type': 'slider', 'label': 'Velocidade (Hz)', 'min': 0.1, 'max': 5, 'step': 0.1, 'default': 1.5},
            'min_freq': {'type': 'slider', 'label': 'Freq. Mínima', 'min': 200, 'max': 1000, 'step': 50, 'default': 400},
            'max_freq': {'type': 'slider', 'label': 'Freq. Máxima', 'min': 1000, 'max': 4000, 'step': 50, 'default': 2000},
            'q': {'type': 'slider', 'label': 'Ressonância (Q)', 'min': 1, 'max': 15, 'step': 0.5, 'default': 5.0},
        }
    },
    'fuzz': {
        'title': 'Classic Fuzz',
        'params': {
            'gain': {'type': 'slider', 'label': 'Sustain (Gain)', 'min': 1, 'max': 30, 'step': 0.5, 'default': 15.0},
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0, 'max': 1, 'step': 0.05, 'default': 1.0},
        }
    },
    'overdrive': {
        'title': 'Overdrive',
        'params': {
            'gain': {'type': 'slider', 'label': 'Ganho', 'min': 0, 'max': 10, 'step': 0.1, 'default': 5.0},
            'tone': {'type': 'slider', 'label': 'Tonalidade', 'min': 0, 'max': 10, 'step': 0.1, 'default': 5.0},
            'level': {'type': 'slider', 'label': 'Volume', 'min': 0, 'max': 10, 'step': 0.1, 'default': 7.0},
        }
    },
    'distortion': {
        'title': 'Distorção Agressiva',
        'params': {
            'drive': {'type': 'slider', 'label': 'Drive', 'min': 1, 'max': 25, 'step': 0.5, 'default': 10.0},
            'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 10, 'step': 0.1, 'default': 5.0},
        }
    },
    'equalizer': {
        'title': 'Equalizador Gráfico',
        'params': {
            'band_100hz': {'type': 'slider', 'label': '100 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_200hz': {'type': 'slider', 'label': '200 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_400hz': {'type': 'slider', 'label': '400 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_800hz': {'type': 'slider', 'label': '800 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_1.6khz': {'type': 'slider', 'label': '1.6 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_3.2khz': {'type': 'slider', 'label': '3.2 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_6.4khz': {'type': 'slider', 'label': '6.4 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
        }
    },
    'chorus': {
        'title': 'Chorus+',
        'params': {
            'rate': {'type': 'slider', 'label': 'Speed (Hz)', 'min': 0.1, 'max': 10, 'step': 0.1, 'default': 2.0},
            'width': {'type': 'slider', 'label': 'Width', 'min': 0.001, 'max': 0.01, 'step': 0.001, 'default': 0.003},
            'intensity': {'type': 'slider', 'label': 'Intensity (Mix)', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.7},
            'tone': {'type': 'slider', 'label': 'Tone', 'min': 0, 'max': 10, 'step': 0.1, 'default': 5.0},
            'mode': {'type': 'combo', 'label': 'Mode', 'options': ['chorus', 'tri-chorus'], 'default': 'chorus'},
        }
    },
    'tremolo': {
        'title': 'Tremolo',
        'params': {
            'rate': {'type': 'slider', 'label': 'Velocidade (Hz)', 'min': 0.5, 'max': 20, 'step': 0.1, 'default': 5.0},
            'depth': {'type': 'slider', 'label': 'Profundidade', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.8},
        }
    },
    'delay': {
        'title': 'Delay Digital',
        'params': {
            'time_ms': {'type': 'slider', 'label': 'Tempo (ms)', 'min': 50, 'max': 1500, 'step': 10, 'default': 300},
            'feedback': {'type': 'slider', 'label': 'Feedback', 'min': 0, 'max': 0.95, 'step': 0.05, 'default': 0.4},
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.3},
        }
    },
      'reverb': {
        'title': 'Reverb (Freeverb)',
        'params': {
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.3},
            'size': {'type': 'slider', 'label': 'Tamanho (Size)', 'min': 0.1, 'max': 0.95, 'step': 0.05, 'default': 0.7},
            'decay': {'type': 'slider', 'label': 'Decaimento (Damp)', 'min': 0, 'max': 0.95, 'step': 0.05, 'default': 0.5},

            'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 2, 'step': 0.05, 'default': 1.0},
        }
    },

    # --- Novos efeitos adicionados ---
    'boss_bf2_flanger': {
        'title': 'BOSS BF-2 Flanger',
        'params': {
            'rate': {'type': 'slider', 'label': 'Rate', 'min': 0.1, 'max': 12, 'step': 0.1, 'default': 3.0},
            'depth': {'type': 'slider', 'label': 'Depth', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.7},
            'manual': {'type': 'slider', 'label': 'Manual', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.5},
            'resonance': {'type': 'slider', 'label': 'Resonance', 'min': 0, 'max': 0.95, 'step': 0.05, 'default': 0.4},
        }
    },
    'carmilla_distortion': {
        'title': 'Carmilla Distortion',
        'params': {
            'gain': {'type': 'slider', 'label': 'Bite (Gain)', 'min': 0, 'max': 20, 'step': 0.2, 'default': 12.0},
            'tone': {'type': 'slider', 'label': 'Tone', 'min': 0, 'max': 10, 'step': 0.1, 'default': 6.0},
            'level': {'type': 'slider', 'label': 'Volume', 'min': 0, 'max': 10, 'step': 0.1, 'default': 7.0},
        }
    },
    'chorus_ce2': {
        'title': 'Chorus CE-2',
        'params': {
            'rate': {'type': 'slider', 'label': 'Rate', 'min': 0.5, 'max': 8, 'step': 0.1, 'default': 4.0},
            'depth': {'type': 'slider', 'label': 'Depth', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.75},
        }
    },
    'compressor': {
        'title': 'Compressor',
        'params': {
            'threshold_db': {'type': 'slider', 'label': 'Threshold (dB)', 'min': -60, 'max': 0, 'step': 1, 'default': -20},
            'ratio': {'type': 'slider', 'label': 'Ratio', 'min': 1, 'max': 20, 'step': 0.5, 'default': 4.0},
            'attack_ms': {'type': 'slider', 'label': 'Attack (ms)', 'min': 1, 'max': 100, 'step': 1, 'default': 10},
            'release_ms': {'type': 'slider', 'label': 'Release (ms)', 'min': 20, 'max': 1000, 'step': 10, 'default': 200},
            'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 10, 'step': 0.1, 'default': 5.0},
        }
    },
   'ultra_flanger': {
    'title': 'Ultra Flanger',
    'params': {
        'rate': {'type': 'slider', 'label': 'Rate', 'min': 0.06, 'max': 13.0, 'step': 0.01, 'default': 1.2},
        'depth': {'type': 'slider', 'label': 'Depth', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.6},
        'resonance': {'type': 'slider', 'label': 'Resonance', 'min': 0, 'max': 0.95, 'step': 0.01, 'default': 0.4},
        'manual': {'type': 'slider', 'label': 'Manual', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.5},
    }
},
    'vintage_overdrive': {
        'title': 'Vintage Overdrive',
        'params': {
            'drive': {'type': 'slider', 'label': 'Drive', 'min': 0, 'max': 10, 'step': 0.1, 'default': 6.0},
            'tone': {'type': 'slider', 'label': 'Tone', 'min': 0, 'max': 10, 'step': 0.1, 'default': 4.0},
            'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 10, 'step': 0.1, 'default': 8.0},
        }
    },
    'tuner': {
        'title': 'Afinador Cromático',
        'params': {}  # Afinadores geralmente não possuem parâmetros ajustáveis
    },

'puresky': {
    'title': 'Pure Sky Overdrive',
    'params': {
        'gain': {'type': 'slider', 'label': 'Gain', 'min': 0, 'max': 1.0, 'step': 0.05, 'default': 0.3},
        'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 1.0, 'step': 0.05, 'default': 0.7},
        'bass': {'type': 'slider', 'label': 'Bass Cut', 'min': 0, 'max': 1.0, 'step': 0.05, 'default': 0.0},
        'treble': {'type': 'slider', 'label': 'Treble Cut', 'min': 0, 'max': 1.0, 'step': 0.05, 'default': 0.0},
    }
},
'afinador': {
    'title': 'Afinador Boss TU-3',
    'params': {} 
},
    'CaineOldSchoolReverb': {
    'title': 'CaineOldSchoolReverb',
    'params': {
        'mode': {'type': 'dropdown', 'label': 'Mode', 'options': ['room', 'hall', 'church'], 'default': 'room'},
        'decay': {'type': 'slider', 'label': 'Decay', 'min': 0.1, 'max': 1.5, 'step': 0.05, 'default': 0.7},
        'mix': {'type': 'slider', 'label': 'Mix', 'min': 0.0, 'max': 1.0, 'step': 0.05, 'default': 0.5},
        'tone': {'type': 'slider', 'label': 'Tone', 'min': 0.0, 'max': 1.0, 'step': 0.05, 'default': 0.5},
    }
},
}
