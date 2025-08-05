const fs = require('fs');
const path = require('path');

const pasta = __dirname;
const destino = path.join(pasta, 'main.js');

// Ignora esses arquivos
const ignorar = ['main.js', 'generate-main.js'];

// Lista os arquivos .js válidos
const arquivosEfeitos = fs.readdirSync(pasta)
  .filter(arquivo =>
    arquivo.endsWith('.js') &&
    !ignorar.includes(arquivo)
  );

// Gera o código do main.js
const conteudo = `
// 🚀 Arquivo gerado automaticamente por generate-main.js

const effectsPath = './';
const effectFiles = ${JSON.stringify(arquivosEfeitos)};

let audioCtx;
let stream;
let source;
let finalNode;
let gainNode;

// Elemento de áudio oculto
const audioElement = document.createElement('audio');
audioElement.style.display = 'none';
document.body.appendChild(audioElement);

// Lista dispositivos
async function enumerateDevices() {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const inputSelect = document.getElementById('input-device');
  const outputSelect = document.getElementById('output-device');
  inputSelect.innerHTML = '';
  outputSelect.innerHTML = '';

  devices.forEach(device => {
    const option = document.createElement('option');
    option.value = device.deviceId;
    option.textContent = device.label || \`\${device.kind} \${device.deviceId}\`;
    if (device.kind === 'audioinput') inputSelect.appendChild(option);
    if (device.kind === 'audiooutput') outputSelect.appendChild(option);
  });
}

window.addEventListener('DOMContentLoaded', enumerateDevices);

// Inicia áudio e aplica efeitos
document.getElementById('toggle-audio-btn').addEventListener('click', async () => {
  const inputId = document.getElementById('input-device').value;
  const outputId = document.getElementById('output-device').value;

  audioCtx = new (window.AudioContext || window.webkitAudioContext)();

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { deviceId: inputId ? { exact: inputId } : undefined }
    });

    source = audioCtx.createMediaStreamSource(stream);
    finalNode = source;

    for (const file of effectFiles) {
      const module = await import(\`\${effectsPath}\${file}\`);
      if (typeof module.default === 'function') {
        finalNode = module.default(audioCtx, finalNode);
      }
    }

    gainNode = audioCtx.createGain();
    finalNode.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    const volumeControl = document.getElementById('volumeControl');
    const savedVolume = localStorage.getItem('masterVolume');
    gainNode.gain.value = savedVolume ? parseFloat(savedVolume) : parseFloat(volumeControl?.value || 1);

    volumeControl?.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      gainNode.gain.value = val;
      localStorage.setItem('masterVolume', val);
    });

    if (typeof audioElement.setSinkId === 'function') {
      try {
        await audioElement.setSinkId(outputId);
        console.log(\`Saída definida para: \${outputId}\`);
      } catch (err) {
        console.warn('Erro ao definir dispositivo de saída:', err);
      }
    }

    console.log('🎸 Áudio e efeitos iniciados com sucesso!');
  } catch (err) {
    console.error('❌ Erro ao acessar o microfone:', err);
  }
});
`;

fs.writeFileSync(destino, conteudo);
console.log('✅ main.js gerado com sucesso!');
