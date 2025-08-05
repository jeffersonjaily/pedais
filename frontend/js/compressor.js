import * as Tone from "tone";

// Elementos da interface
const compressorToggle = document.querySelector('#compressor .effect-toggle');
const thresholdControl = document.getElementById('compressor-threshold');
const ratioControl = document.getElementById('compressor-ratio');
const attackControl = document.getElementById('compressor-attack');
const releaseControl = document.getElementById('compressor-release');

let isCompressorActive = false;

// Fonte de áudio simulada (troque por entrada real se quiser)
const guitarra = new Tone.Noise("white");

// Cria compressor com valores padrão
const compressor = new Tone.Compressor({
  threshold: -30,
  ratio: 4,
  attack: 0.01,
  release: 0.3
}).toDestination();

// Conecta guitarra (sem efeito ainda)
guitarra.connect(Tone.Destination);

compressorToggle.addEventListener('click', async () => {
  isCompressorActive = !isCompressorActive;
  compressorToggle.setAttribute('aria-pressed', isCompressorActive);
  compressorToggle.textContent = isCompressorActive ? 'Desligar' : 'Ligar';

  if (isCompressorActive) {
    console.log('Compressor ativado');
    await Tone.start();
    guitarra.disconnect(Tone.Destination);
    guitarra.connect(compressor);
    guitarra.start();
    applyCompressorEffect();
  } else {
    console.log('Compressor desativado');
    guitarra.disconnect(compressor);
    guitarra.connect(Tone.Destination);
    guitarra.stop();
    removeCompressorEffect();
  }
});

function applyCompressorEffect() {
  const threshold = parseFloat(thresholdControl.value);
  const ratio = parseFloat(ratioControl.value);
  const attack = parseFloat(attackControl.value);
  const release = parseFloat(releaseControl.value);

  console.log(`Aplicando Compressor com Threshold=${threshold}dB, Ratio=${ratio}, Attack=${attack}s, Release=${release}s`);

  compressor.threshold.value = threshold;
  compressor.ratio.value = ratio;
  compressor.attack = attack;
  compressor.release = release;
}

function removeCompressorEffect() {
  console.log('Removendo o efeito Compressor');
  // Reset (se desejar)
  compressor.threshold.value = -30;
  compressor.ratio.value = 4;
  compressor.attack = 0.01;
  compressor.release = 0.3;
}