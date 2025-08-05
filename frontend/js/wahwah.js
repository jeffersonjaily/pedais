const wahwahToggle = document.querySelector('#wahwah .effect-toggle');
const rateControl = document.getElementById('wahwah-rate');
const minFreqControl = document.getElementById('wahwah-minfreq');
const maxFreqControl = document.getElementById('wahwah-maxfreq');

let isEffectActive = false;

wahwahToggle.addEventListener('click', () => {
  isEffectActive = !isEffectActive;
  wahwahToggle.setAttribute('aria-pressed', isEffectActive);
  wahwahToggle.textContent = isEffectActive ? 'Desligar' : 'Ligar';

  if (isEffectActive) {
    console.log('Efeito WahWah ativado');
    applyWahWahEffect();
  } else {
    console.log('Efeito WahWah desativado');
    removeWahWahEffect();
  }
});

function applyWahWahEffect() {
  const rate = parseFloat(rateControl.value);
  const minFreq = parseInt(minFreqControl.value, 10);
  const maxFreq = parseInt(maxFreqControl.value, 10);

  console.log(`Aplicando WahWah com Rate=${rate}, MinFreq=${minFreq}, MaxFreq=${maxFreq}`);
  // Aqui você pode integrar com uma biblioteca de áudio como Tone.js ou Web Audio API
}

function removeWahWahEffect() {
  console.log('Removendo o efeito WahWah');
  // Cancelar ou resetar alterações no efeito
}