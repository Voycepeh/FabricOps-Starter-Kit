import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const timeline = JSON.parse(fs.readFileSync(path.join(root, 'src', 'motion-experiment', 'timeline.json'), 'utf8'));
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
  return (Math.sin(Math.PI * 2 * frequency * time) + Math.sin(Math.PI * 4 * frequency * time) * 0.24) * attack * release;
};
const whoosh = (time, duration) => {
  const position = time / duration;
  return (random() * 2 - 1) * Math.sin(Math.PI * position) ** 1.8 * Math.sin(Math.PI * 2 * (180 + position * 1250) * time);
};
const impact = (time, duration) => {
  const body = Math.sin(Math.PI * 2 * 62 * time) * Math.exp(-8 * time);
  const click = (random() * 2 - 1) * Math.exp(-44 * time);
  return (body * 0.82 + click * 0.18) * Math.min(1, (duration - time) / 0.04);
};
const bed = (time, duration) => {
  const fadeIn = Math.min(1, time / 2.2);
  const fadeOut = Math.min(1, (duration - time) / 1.8);
  return (Math.sin(Math.PI * 2 * 55 * time) + Math.sin(Math.PI * 2 * 82.41 * time) * 0.38) * fadeIn * fadeOut;
};

timeline.soundCues.forEach((cue, index) => {
  const sample = cue.type === 'bed' ? bed : cue.type === 'whoosh' ? whoosh : cue.type === 'impact' ? impact : softTone(523.25 + (index % 5) * 65.41);
  add(cue.at, cue.duration, cue.gain, cue.pan, sample);
});

let peak = 0;
for (let index = 0; index < length; index += 1) peak = Math.max(peak, Math.abs(left[index]), Math.abs(right[index]));
const masterGain = peak > 0 ? 0.74 / peak : 1;
const buffer = Buffer.alloc(44 + length * channels * 2);
buffer.write('RIFF', 0);
buffer.writeUInt32LE(36 + length * channels * 2, 4);
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
buffer.writeUInt32LE(length * channels * 2, 40);
for (let index = 0; index < length; index += 1) {
  const offset = 44 + index * 4;
  buffer.writeInt16LE(Math.round(Math.max(-1, Math.min(1, left[index] * masterGain)) * 32767), offset);
  buffer.writeInt16LE(Math.round(Math.max(-1, Math.min(1, right[index] * masterGain)) * 32767), offset + 2);
}

const narrationSource = path.join(root, 'FabricOps_narration_master_numbered.m4a');
const narrationOutput = path.join(root, 'public', 'audio', 'FabricOps_narration_master_numbered.m4a');
fs.mkdirSync(path.dirname(narrationOutput), {recursive: true});
fs.copyFileSync(narrationSource, narrationOutput);
const output = path.join(root, 'public', 'generated', 'fabricops-part1-motion-sfx.wav');
fs.mkdirSync(path.dirname(output), {recursive: true});
fs.writeFileSync(output, buffer);
console.log(`Staged narration and generated ${path.relative(root, output)} (${timeline.durationSeconds}s, stereo 48 kHz).`);
