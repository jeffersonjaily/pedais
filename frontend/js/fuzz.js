async function createFuzzEffect() {
  const context = new (window.AudioContext || window.webkitAudioContext)();
  const source = context.createBufferSource();
  const request = await fetch('sua-musica.mp3'); // substitua com o caminho do seu áudio
  const arrayBuffer = await request.arrayBuffer();
  source.buffer = await context.decodeAudioData(arrayBuffer);

  const gainNode = context.createGain();
  const distortion = context.createWaveShaper();

  // Função de curva de distorção (fuzz)
  function makeDistortionCurve(amount) {
    const k = typeof amount === 'number' ? amount : 50;
    const n_samples = 44100;
    const curve = new Float32Array(n_samples);
    const deg = Math.PI / 180;
    for (let i = 0; i < n_samples; ++i) {
      const x = (i * 2) / n_samples - 1;
      curve[i] = (3 + k) * x * 20 * deg / (Math.PI + k * Math.abs(x));
    }
    return curve;
  }

  distortion.curve = makeDistortionCurve(400);
  distortion.oversample = '4x';

  source.connect(distortion);
  distortion.connect(gainNode);
  gainNode.connect(context.destination);

  source.start();
}