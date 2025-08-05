# Conteúdo para o arquivo: tuner.py

import numpy as np

NOTE_NAMES = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

def yin_detect_pitch(audio, sample_rate=44100, threshold=0.15):
    """
    Detecta a frequência fundamental usando o algoritmo YIN, que é mais
    robusto contra erros de oitava e ruído do que a autocorrelação simples.

    Args:
        audio (np.array): O buffer de áudio.
        sample_rate (int): A taxa de amostragem.
        threshold (float): O limiar de "aperiodicidade". Valores entre 0.1 e 0.2
                           geralmente funcionam bem.

    Returns:
        float: A frequência fundamental detectada em Hz.
    """
    # Se o sinal for muito baixo, considera silêncio
    if np.max(np.abs(audio)) < 0.05:
        return 0.0

    # 1. Calcula a função de diferença (similar à autocorrelação, mas otimizada)
    yin_buffer_size = len(audio) // 2
    yin_buffer = np.zeros(yin_buffer_size)
    for tau in range(1, yin_buffer_size):
        yin_buffer[tau] = np.sum((audio[:-tau] - audio[tau:])**2)

    # 2. Normalização cumulativa da média
    # Esta é a parte chave do YIN que o diferencia da autocorrelação.
    yin_buffer[0] = 1
    running_sum = 0
    for tau in range(1, yin_buffer_size):
        running_sum += yin_buffer[tau]
        if running_sum == 0:
            yin_buffer[tau] = 1
        else:
            yin_buffer[tau] *= tau / running_sum
            
    # 3. Encontra o primeiro "mergulho" (dip) abaixo do limiar (threshold)
    # Isso encontra o período fundamental de forma muito mais confiável.
    tau = 1
    while tau < yin_buffer_size and yin_buffer[tau] > threshold:
        tau += 1
        
    # Se nenhum mergulho for encontrado, o sinal é provavelmente aperiódico (ruído)
    if tau == yin_buffer_size or yin_buffer[tau] >= threshold:
        return 0.0

    # 4. Interpolação parabólica para precisão sub-amostra
    # Encontra a localização exata do mínimo entre as amostras.
    if tau > 0 and tau < yin_buffer_size - 1:
        y_prev = yin_buffer[tau - 1]
        y_curr = yin_buffer[tau]
        y_next = yin_buffer[tau + 1]
        
        # Evita divisão por zero
        denominator = 2 * (2 * y_curr - y_next - y_prev)
        if denominator == 0:
            p = 0
        else:
            p = (y_next - y_prev) / denominator
        tau += p
        
    if tau == 0:
        return 0.0

    return sample_rate / tau

def freq_to_note(freq):
    """
    Converte uma frequência em Hz para a nota musical, oitava e desafinação em cents.
    """
    if freq <= 20: # Limiar de frequência mínima (abaixo de notas de baixo)
        return None, None, None
        
    A4_FREQ = 440.0
    
    midi_num = 12 * np.log2(freq / A4_FREQ) + 69
    midi_num_rounded = int(round(midi_num))
    
    cents = int(round((midi_num - midi_num_rounded) * 100))
    
    note_index = midi_num_rounded % 12
    octave = (midi_num_rounded // 12) - 1
    note_name = NOTE_NAMES[note_index]
    
    return note_name, octave, cents
