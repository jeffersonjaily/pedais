# backend/voz/effects_config_voz.py

PEDAL_CONFIGS_VOZ = {
    'vocal_compressor': {
        'title': 'Compressor Vocal',
        'params': {
            'threshold_db': {'type': 'slider', 'label': 'Threshold (dB)', 'min': -60, 'max': 0, 'step': 1, 'default': -20},
            'ratio': {'type': 'slider', 'label': 'Ratio', 'min': 1, 'max': 20, 'step': 0.1, 'default': 4.0},
            'attack_ms': {'type': 'slider', 'label': 'Attack (ms)', 'min': 1, 'max': 100, 'step': 1, 'default': 10},
            'release_ms': {'type': 'slider', 'label': 'Release (ms)', 'min': 20, 'max': 1000, 'step': 10, 'default': 200},
            'level': {'type': 'slider', 'label': 'Level', 'min': 0, 'max': 10, 'step': 0.1, 'default': 1.0},
        }
    },

    'deesser': {
    'title': 'De-Esser Vocal (Avançado)',
    'params': {
        'frequency': {
            'type': 'slider',
            'label': 'Frequência de Corte (Hz)',
            'min': 4000,
            'max': 12000,
            'step': 100,
            'default': 6000
        },
        'threshold_db': {
            'type': 'slider',
            'label': 'Threshold (dB)',
            'min': -60,
            'max': 0,
            'step': 1,
            'default': -25
        },
        'reduction': {
            'type': 'slider',
            'label': 'Redução',
            'min': 0.0,
            'max': 1.0,
            'step': 0.05,
            'default': 0.6
        }
    }
},

    'vocal_equalizer': {
        'title': 'Equalizador Gráfico (10 Bandas)',
        'params': {
            'band_60hz': {'type': 'slider', 'label': '60 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_125hz': {'type': 'slider', 'label': '125 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_250hz': {'type': 'slider', 'label': '250 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_500hz': {'type': 'slider', 'label': '500 Hz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_1khz': {'type': 'slider', 'label': '1 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_2khz': {'type': 'slider', 'label': '2 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_4khz': {'type': 'slider', 'label': '4 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_6khz': {'type': 'slider', 'label': '6 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_8khz': {'type': 'slider', 'label': '8 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
            'band_12khz': {'type': 'slider', 'label': '12 KHz', 'min': -15, 'max': 15, 'step': 1, 'default': 0.0},
        }
    },

    'vocal_delay': {
        'title': 'Delay Vocal',
        'params': {
            'time_ms': {'type': 'slider', 'label': 'Tempo (ms)', 'min': 50, 'max': 1500, 'step': 10, 'default': 500, 'cast': int},
            'feedback': {'type': 'slider', 'label': 'Feedback', 'min': 0.0, 'max': 0.95, 'step': 0.05, 'default': 0.6, 'cast': float},
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0.0, 'max': 1.0, 'step': 0.05, 'default': 0.7, 'cast': float},
        }
    },

    'reverb_voz': {
        'title': 'Reverb Vocal Pro',
        'params': {
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.3},
            'size': {'type': 'slider', 'label': 'Tamanho (Size)', 'min': 0.1, 'max': 1.0, 'step': 0.05, 'default': 0.7},
            'decay': {'type': 'slider', 'label': 'Decaimento (Tone)', 'min': 0, 'max': 1.0, 'step': 0.05, 'default': 0.5},
            'predelay_ms': {'type': 'slider', 'label': 'Pre-Delay (ms)', 'min': 0, 'max': 100, 'step': 1, 'default': 10},
        }
    },

    'pitch_shifter': {
        'title': 'Pitch Shifter Vocal',
        'params': {
            'semitones': {'type': 'slider', 'label': 'Semitons', 'min': -12, 'max': 12, 'step': 1, 'default': 0},
            'mix': {'type': 'slider', 'label': 'Mix', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.5},
        }
    },

    'pitch_correction': {
        'title': 'Pitch Correction Vocal',
        'params': {
            'tolerance': {'type': 'slider', 'label': 'Tolerância (cents)', 'min': 0, 'max': 50, 'step': 1, 'default': 20},
            'speed': {'type': 'slider', 'label': 'Velocidade', 'min': 0.1, 'max': 1.0, 'step': 0.05, 'default': 0.8},
        }
    },

    'vocal_tremolo': {
        'title': 'Tremolo Vocal',
        'params': {
            'rate': {'type': 'slider', 'label': 'Velocidade (Hz)', 'min': 0.5, 'max': 20, 'step': 0.1, 'default': 5.0},
            'depth': {'type': 'slider', 'label': 'Profundidade', 'min': 0, 'max': 1, 'step': 0.05, 'default': 0.8},
        }
    },

    'pop_click_suppressor': {
    'title': 'Pop & Click Suppressor (Avançado)',
    'params': {
        'cutoff_hz': {'type': 'slider', 'label': 'Corte Grave (Hz)', 'min': 40, 'max': 200, 'step': 10, 'default': 120},
        'click_threshold': {'type': 'slider', 'label': 'Limiar de Estalo', 'min': 0.1, 'max': 1.0, 'step': 0.05, 'default': 0.7},
    }
},

    'noise_reducer': {
        'title': 'Redutor de Ruído de Fundo',
        'params': {
            'threshold': {'type': 'slider', 'label': 'Limiar de Ruído', 'min': 0.001, 'max': 0.1, 'step': 0.001, 'default': 0.02},
            'reduction_db': {'type': 'slider', 'label': 'Redução (dB)', 'min': 6, 'max': 60, 'step': 1, 'default': 20},
        }
    },
}
