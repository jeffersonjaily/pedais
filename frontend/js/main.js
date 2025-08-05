// 🚀 Arquivo gerado automaticamente por generate-main.js

const effectsPath = './';
const effectFiles = ['fuzz.js', 'wahwah.js'];["fuzz.js","wahwah.js","overdrive.js","compressor.js",
    "chorus.js","flanger.js",
    "reverb.js","tremolo.js","delay.js","distortion.js","equalizer.js"
    ,"boss_bf_2_flanger.js",
    "carmilla_distortion.js","compressor_guitarra.js",
    "fuzz.js","pure_sky.js","ultra_flanger_uf100.js",
    "vintage_overdrive.js","wahwah.js","tuner.js"];
let audioCtx;
let stream;
let source;
let finalNode;
let gainNode;

// Elemento de áudio oculto para possível redirecionamento
const audioElement = document.createElement('audio');
audioElement.style.display = 'none';
document.body.appendChild(audioElement);

// Lista dispositivos de entrada e saída
async function enumerateDevices() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const inputSelect = document.getElementById('input-device');
    const outputSelect = document.getElementById('output-device');
    if (!inputSelect || !outputSelect) {
      console.warn('❗ Elementos de seleção de dispositivo não encontrados');
      return;
    }

    inputSelect.innerHTML = '';
    outputSelect.innerHTML = '';

    devices.forEach(device => {
      const option = document.createElement('option');
      option.value = device.deviceId;
      option.textContent = device.label || `${device.kind} (${device.deviceId})`;
      if (device.kind === 'audioinput') inputSelect.appendChild(option);
      if (device.kind === 'audiooutput') outputSelect.appendChild(option);
    });
  } catch (err) {
    console.error('❌ Erro ao enumerar dispositivos:', err);
  }
}

window.addEventListener('DOMContentLoaded', enumerateDevices);

// Inicia captura de áudio e aplica efeitos
document.getElementById('toggle-audio-btn')?.addEventListener('click', async () => {
  const inputId = document.getElementById('input-device')?.value;
  const outputId = document.getElementById('output-device')?.value;
  const volumeControl = document.getElementById('volumeControl');

  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    stream = await navigator.mediaDevices.getUserMedia({
      audio: inputId ? { deviceId: { exact: inputId } } : true
    });

    source = audioCtx.createMediaStreamSource(stream);
    finalNode = source;

    // Carrega e aplica os efeitos dinamicamente
    for (const file of effectFiles) {
      try {
        const module = await import(`${effectsPath}${file}`);
        if (typeof module.default === 'function') {
          finalNode = module.default(audioCtx, finalNode);
        } else {
          console.warn(`⚠️ Módulo ${file} não exporta uma função padrão.`);
        }
      } catch (e) {
        console.error(`❌ Erro ao carregar efeito ${file}:`, e);
      }
    }

    // Controlador de volume mestre
    gainNode = audioCtx.createGain();
    finalNode.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    // Define volume inicial
    const savedVolume = localStorage.getItem('masterVolume');
    const initialVolume = savedVolume ? parseFloat(savedVolume) : parseFloat(volumeControl?.value || '1');
    gainNode.gain.value = initialVolume;

    // Atualiza volume ao interagir
    volumeControl?.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      gainNode.gain.value = val;
      localStorage.setItem('masterVolume', val);
    });

    // Redireciona áudio para saída selecionada (se suportado)
    if (typeof audioElement.setSinkId === 'function' && outputId) {
      try {
        await audioElement.setSinkId(outputId);
        console.log(`📢 Saída definida para: ${outputId}`);
      } catch (err) {
        console.warn('⚠️ Erro ao definir dispositivo de saída:', err);
      }
    }

    console.log('🎸 Áudio com efeitos iniciado com sucesso!');
  } catch (err) {
    console.error('❌ Falha ao iniciar captura de áudio:', err);
    alert('Erro ao acessar o microfone. Verifique as permissões.');
  }
});
