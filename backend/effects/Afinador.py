import numpy as np
# Importa as funções de alta precisão do seu arquivo tuner.py
from .tuner import yin_detect_pitch, freq_to_note

class BossTU3Tuner:
    """
    Classe que representa e simula o pedal afinador BOSS TU-3.
    Utiliza o algoritmo YIN para detecção de afinação de alta precisão.
    """

    def __init__(self, sample_rate=44100, buffer_size=4096):
        # --- Configurações do Pedal ---
        self.nome = "Boss TU-3 Chromatic Tuner"
        self.tipo = "Afinador cromático (YIN Algorithm)"
        self.enabled = True

        # --- Configurações de Análise ---
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        # --- Parâmetros Configuráveis ---
        self.modos_disponiveis = ["Chromatic", "Guitar", "Bass"]
        self.modo_afinacao = self.modos_disponiveis[0]
        self.afinacao_de_referencia = 440  # Afinação de A4 em Hz

        # --- Estado da Análise (Resultados) ---
        self.detected_frequency = 0.0
        self.detected_note = "--"
        self.cents_deviation = 0

    def set_param(self, name: str, value):
        """
        Interface padronizada para alterar parâmetros.
        """
        if name == "Enabled":
            self.enabled = bool(value)
        elif name == "Mode":
            if value in self.modos_disponiveis:
                self.modo_afinacao = value
            else:
                print(f"Modo '{value}' inválido.")
    
    def get_tuner_state(self) -> dict:
        """
        Retorna o estado atual do afinador para ser usado por uma GUI.
        """
        return {
            "note": self.detected_note,
            "deviation_cents": self.cents_deviation,
            "frequency": self.detected_frequency
        }

    def apply(self, input_signal: np.ndarray, **params) -> np.ndarray:
        """
        Processa o sinal de áudio. Se o afinador estiver ligado, analisa a
        frequência e muta o som. Se desligado, apenas passa o som adiante.
        """
        if not self.enabled:
            # Limpa o estado do afinador quando ele é desligado
            if self.detected_note != "--":
                self.detected_note = "--"
                self.cents_deviation = 0
            return input_signal

        # --- Análise de Frequência com YIN ---
        self._analyze_frequency_yin(input_signal)

        # --- Mudo na Saída ---
        # Retorna um sinal de zeros para mutar o som enquanto afina
        return np.zeros_like(input_signal)

    def _analyze_frequency_yin(self, signal_chunk: np.ndarray):
        """
        O coração do afinador, agora usando o algoritmo YIN.
        """
        # 1. Detecta a frequência fundamental
        self.detected_frequency = yin_detect_pitch(signal_chunk, self.sample_rate)

        # 2. Converte a frequência para nota e desvio
        if self.detected_frequency > 0:
            note_name, octave, cents = freq_to_note(self.detected_frequency)
            if note_name is not None:
                self.detected_note = f"{note_name}{octave}"
                self.cents_deviation = cents
                # Exibe a nota no console para feedback em tempo real
                print(f"Afinador YIN -> Nota: {self.detected_note:<4s} | Desvio: {self.cents_deviation: >4d} cents | Freq: {self.detected_frequency:.2f} Hz")
            else:
                # Caso a frequência seja válida mas não mapeie para uma nota
                self.detected_note = "??"
                self.cents_deviation = 0
        else:
            # Se nenhuma frequência for detectada (silêncio ou ruído)
            self.detected_note = "--"
            self.cents_deviation = 0
