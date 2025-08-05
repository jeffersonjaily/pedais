# PedalPy - Pedalboard Virtual em Python

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)

Um simulador de pedalboard de guitarra em tempo real, construído com Python, Tkinter e NumPy/SciPy. Processe o áudio da sua guitarra (ou qualquer outra fonte de som) através de uma cadeia de efeitos customizável com uma interface gráfica intuitiva.

---

---

## 🎸 Sobre o Projeto

**PedalPy** nasceu da paixão por música e programação. O objetivo é criar uma plataforma de efeitos de áudio de código aberto, leve e extensível, que permita a músicos e desenvolvedores experimentar com processamento de sinais digitais (DSP) de uma forma visual e interativa.

A interface permite arrastar e soltar os pedais para reordenar a cadeia de efeitos, salvar e carregar presets, e ajustar cada parâmetro em tempo real.

### ✨ Funcionalidades

* **Processamento de Áudio em Tempo Real:** Baixa latência utilizando a biblioteca `sounddevice`.
* **Interface Gráfica Intuitiva:** Construída com o framework nativo Tkinter.
* **Cadeia de Efeitos Customizável:** Reordene os pedais com um simples arrastar e soltar.
* **Sistema de Presets:** Salve e carregue suas configurações de pedais favoritas.
* **Gravação Integrada:** Grave sua performance diretamente para um arquivo `.wav`.
* **Afinador Cromático:** Um afinador visual integrado para manter seu instrumento no tom certo.
* **Extensível:** A arquitetura é modular, facilitando a adição de novos efeitos.

---

### 🎛️ Efeitos Incluídos

O projeto conta com uma vasta gama de efeitos clássicos e modernos, incluindo:

| Categoria | Efeitos |
| :--- | :--- |
| **Ganho** | Overdrive, Vintage Overdrive, Fuzz, Distortion, Carmilla Distortion, Pure Sky |
| **Modulação** | Chorus, Chorus CE-2, Flanger (BOSS BF-2), Ultra Flanger, Tremolo, Wah-Wah |
| **Dinâmica** | Compressor |
| **Filtro** | Equalizador Gráfico (7 bandas) |
| **Tempo & Espaço** | Delay, Reverb, Caine Old School Reverb (Room, Hall, Church) |
| **Utilitários** | Afinador Cromático (Boss TU-3) |

---

## 🚀 Começando

Siga estes passos para ter o projeto rodando na sua máquina.

### Pré-requisitos

* **Python 3.9+**
* **pip** (gerenciador de pacotes do Python)
* Uma **interface de áudio** (para conectar sua guitarra ao computador com baixa latência) e drivers **ASIO** (recomendado no Windows).

### Instalação

1.  **Clone o repositório:**
    ```sh
    git clone [https://github.com/jeffersonjaily/pedais.git](https://github.com/jeffersonjaily/pedais.git)
    cd pedais
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```sh
    python -m venv venv
    # Ative o ambiente:
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```
   

4.  **Execute a aplicação:**
    ```sh
    python app.py
    ```

### Uso

1.  Abra o programa.
2.  Selecione seus dispositivos de **Entrada** e **Saída** de áudio. Dê preferência a drivers ASIO para menor latência.
3.  Clique em **▶ Iniciar** para começar o processamento de áudio.
4.  Ative os pedais desejados e ajuste os knobs.
5.  Arraste os pedais para mudar a ordem da cadeia de efeitos.
6.  Use o menu "Presets" para salvar ou carregar suas configurações.

---

## 🤝 Contribuindo

Contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito bem-vinda**.

Se você tem uma sugestão para melhorar o projeto, por favor, faça um fork do repositório e crie um pull request. Você também pode simplesmente abrir uma issue com a tag "enhancement".

1.  Faça um **Fork** do projeto.
2.  Crie sua **Feature Branch** (`git checkout -b feature/EfeitoNovoIncrivel`).
3.  Faça o **Commit** de suas mudanças (`git commit -m 'Adiciona o EfeitoNovoIncrivel'`).
4.  Faça o **Push** para a Branch (`git push origin feature/EfeitoNovoIncrivel`).
5.  Abra um **Pull Request**.

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE.txt` para mais informações.

---

## 🙏 Agradecimentos

* Aos criadores das bibliotecas `NumPy`, `SciPy` e `SoundDevice`.
* À comunidade de DSP e desenvolvimento de áudio por compartilhar tanto conhecimento.

