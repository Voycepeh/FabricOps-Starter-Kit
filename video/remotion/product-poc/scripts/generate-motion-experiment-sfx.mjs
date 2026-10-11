import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const timeline = JSON.parse(fs.readFileSync(path.join(root, 'src/motion-experiment/timeline.json'), 'utf8'));
const sampleRate = 48000;
const channels = 2;
const length = Math.round(timeline.durationSeconds * sampleRate);
const left = new Float64Array(length);
const right = new Float64Array(length);
let seed = 314159;
const random = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
};

const add = (time, duration, gain, pan, sample) => {
  const start = Math.max(0, Math.round(time * sampleRate));
  const end = Math.min(length, start + Math.round(duration * sampleRate));
  const leftGain = Math.sqrt((1 - pan) / 2) * gain;
  const rightGain = Math.sqrt((1 + pan) / 2) * gain;
  for (let index = start; index < end; index += 1) {
    const local = (index - start) / sampleRate;
    const value = sample(local, duration);
    left[index] += value * leftGain;
    right[index] += value * rightGain;
  }
};

const softTone = (frequency) => (time, duration) => {
  const attack = Math.min(1, time / 0.025);
  const release = Math.exp(-5.5 * time / duration);
  return Math.sin(Math.PI * 2 * frequency * time) * attack * release;
};

const whoosh = (fromFrequency, toFrequency) => (time, duration) => {
  const position = time / duration;
  const envelope = Math.sin(Math.PI * position) ** 1.7;
  const cutoff = fromFrequency + (toFrequency - fromFrequency) * position;
  const noise = random() * 2 - 1;
  return noise * Math.sin(Math.PI * 2 * cutoff * time) * envelope;
};

const impact = (time, duration) => {
  const body = Math.sin(Math.PI * 2 * 64 * time) * Math.exp(-8 * time);
  const click = (random() * 2 - 1) * Math.exp(-45 * time);
  return (body * 0.8 + click * 0.2) * Math.min(1, (duration - time) / 0.04);
};

const beats = timeline.beats;
add(0, timeline.durationSeconds, 0.018, 0, (time) => {
  const fadeIn = Math.min(1, time / 1.5);
  const fadeOut = Math.min(1, (timeline.durationSeconds - time) / 1.2);
  return (Math.sin(Math.PI * 2 * 73.42 * time) + Math.sin(Math.PI * 2 * 110 * time) * 0.42) * fadeIn * fadeOut;
});
add(beats.contractActivated, 0.34, 0.12, -0.62, softTone(659.25));
add(beats.promotionBegins, 1.35, 0.10, -0.25, whoosh(180, 1450));
add(beats.productionArrives - 0.45, 0.72, 0.15, 0, impact);
beats.pipelineChecks.forEach((beat, index) => {
  add(beat, 0.24, 0.075, -0.25 + index * 0.25, softTone([783.99, 987.77, 1174.66][index]));
});
add(beats.productionApproved, 1.25, 0.11, 0.28, (time, duration) => (softTone(523.25)(time, duration) + softTone(783.99)(time, duration) * 0.68));
add(beats.consumerHandoff - 0.42, 0.9, 0.09, 0.55, whoosh(420, 2100));
add(beats.consumerHandoff, 1.8, 0.12, 0.62, (time, duration) => (softTone(659.25)(time, duration) + softTone(987.77)(time, duration) * 0.72 + softTone(1318.51)(time, duration) * 0.45));

let peak = 0;
for (let index = 0; index < length; index += 1) peak = Math.max(peak, Math.abs(left[index]), Math.abs(right[index]));
const masterGain = peak > 0 ? 0.78 / peak : 1;
const dataSize = length * channels * 2;
const buffer = Buffer.alloc(44 + dataSize);
buffer.write('RIFF', 0);
buffer.writeUInt32LE(36 + dataSize, 4);
buffer.write('WAVE', 8);
buffer.write('fmt ', 12);
buffer.writeUInt32LE(16, 16);
buffer.writeUInt16LE(1, 20);
buffer.writeUInt16LE(channels, 22);
buffer.writeUInt32LE(sampleRate, 24);
buffer.writeUInt32LE(sampleRate * channels * 2, 28);
buffer.writeUInt16LE(channels * 2, 32);
buffer.writeUInt16LE(16, 34);
buffer.write('data', 36);
buffer.writeUInt32LE(dataSize, 40);
for (let index = 0; index < length; index += 1) {
  const offset = 44 + index * 4;
  buffer.writeInt16LE(Math.round(Math.max(-1, Math.min(1, left[index] * masterGain)) * 32767), offset);
  buffer.writeInt16LE(Math.round(Math.max(-1, Math.min(1, right[index] * masterGain)) * 32767), offset + 2);
}
const narrationSource = path.join(root, 'FabricOps_narration_master_numbered.m4a');
const narrationOutput = path.join(root, 'public', 'audio', 'FabricOps_narration_master_numbered.m4a');
fs.mkdirSync(path.dirname(narrationOutput), {recursive: true});
fs.copyFileSync(narrationSource, narrationOutput);

const output = path.join(root, 'public', 'generated', 'motion-experiment-sfx.wav');
fs.mkdirSync(path.dirname(output), {recursive: true});
fs.writeFileSync(output, buffer);
console.log(`Staged narration and generated ${path.relative(root, output)} (${timeline.durationSeconds}s, stereo 48 kHz).`);
