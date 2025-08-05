# backend/pedal_configs/__init__.py
import os
import importlib

ALL_PEDAL_CONFIGS = {}
current_dir = os.path.dirname(__file__)

for instrument_folder in os.listdir(current_dir):
    instrument_path = os.path.join(current_dir, instrument_folder)
    if os.path.isdir(instrument_path) and not instrument_folder.startswith('__'):
        for filename in os.listdir(instrument_path):
            if filename.endswith('_config.py'):
                module_name = filename[:-3]
                effect_name = module_name.replace('_config', '')
                try:
                    module = importlib.import_module(f'.{instrument_folder}.{module_name}', package='backend.pedal_configs')
                    if hasattr(module, 'PEDAL_CONFIG'):
                        # A chave agora inclui o instrumento para evitar conflitos
                        config_key = f"{instrument_folder}_{effect_name}"
                        ALL_PEDAL_CONFIGS[config_key] = module.PEDAL_CONFIG
                except ImportError as e:
                    print(f"Erro ao importar {module_name}: {e}")