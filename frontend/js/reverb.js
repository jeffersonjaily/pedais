// reverb.js
export default function applyReverb(audioCtx, inputNode) {
  const gainNode = audioCtx.createGain();
  gainNode.gain.value = 1.0;
  inputNode.connect(gainNode);
  return gainNode;
}
function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}