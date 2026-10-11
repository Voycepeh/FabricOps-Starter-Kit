import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const output = path.join(root, 'out', 'motion-experiment');
const require = createRequire(import.meta.url);
export const ffmpeg = require('ffmpeg-static');
const remotionCli = path.join(root, 'node_modules', '@remotion', 'cli', 'remotion-cli.js');
export const timeline = JSON.parse(fs.readFileSync(path.join(root, 'src', 'motion-experiment', 'timeline.json'), 'utf8'));

export const run = (command, args) => {
  const result = spawnSync(command, args, {cwd: root, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
};

export const runRemotion = (args) => run(process.execPath, [remotionCli, ...args]);

export const parseTimestamp = (value) => {
  if (typeof value !== 'string' || value.trim() === '') throw new Error('Timestamp is required.');
  const parts = value.trim().split(':').map(Number);
  if (parts.some((part) => !Number.isFinite(part)) || parts.length > 3) throw new Error(`Invalid timestamp: ${value}`);
  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return parts[0] * 3600 + parts[1] * 60 + parts[2];
};

export const formatTimestamp = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainder = (seconds - minutes * 60).toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
  const [wholeSeconds, fraction] = remainder.split('.');
  return `${String(minutes).padStart(2, '0')}-${wholeSeconds.padStart(2, '0')}${fraction ? `-${fraction}` : ''}`;
};

export const readArgument = (name) => {
  const direct = process.argv.find((argument) => argument.startsWith(`${name}=`));
  if (direct) return direct.slice(name.length + 1);
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
};

export const stageAudio = () => run(process.execPath, ['scripts/generate-motion-sfx.mjs']);

const normalizeFrameNames = (framesDirectory) => {
  const frames = fs.readdirSync(framesDirectory)
    .filter((file) => /\.(jpe?g)$/i.test(file))
    .sort((left, right) => Number(left.match(/\d+/)?.[0] ?? 0) - Number(right.match(/\d+/)?.[0] ?? 0));
  if (frames.length === 0) throw new Error(`No rendered frames found in ${framesDirectory}`);
  frames.forEach((file, index) => fs.renameSync(path.join(framesDirectory, file), path.join(framesDirectory, `frame-${String(index).padStart(6, '0')}.jpeg`)));
  return frames.length;
};

export const renderRange = ({fromSeconds, toSeconds, target}) => {
  const {fps, durationSeconds} = timeline;
  if (!(fromSeconds >= 0 && toSeconds > fromSeconds && toSeconds <= durationSeconds)) {
    throw new Error(`Range must satisfy 0 <= from < to <= ${durationSeconds}.`);
  }
  const startFrame = Math.round(fromSeconds * fps);
  const endFrameExclusive = Math.round(toSeconds * fps);
  const durationSecondsExact = (endFrameExclusive - startFrame) / fps;
  const framesDirectory = path.join(output, `frames-temp-${startFrame}-${endFrameExclusive}`);
  fs.mkdirSync(output, {recursive: true});
  fs.rmSync(framesDirectory, {recursive: true, force: true});
  stageAudio();
  runRemotion([
    'render', 'src/index.ts', 'FabricOpsPart1Motion', framesDirectory,
    '--sequence', '--image-format=jpeg', '--jpeg-quality=92', '--muted', '--concurrency=4',
    `--frames=${startFrame}-${endFrameExclusive - 1}`,
  ]);
  const frameCount = normalizeFrameNames(framesDirectory);
  const narration = path.join(root, 'public', 'audio', 'FabricOps_narration_master_numbered.m4a');
  const sfx = path.join(root, 'public', 'generated', 'fabricops-part1-motion-sfx.wav');
  run(ffmpeg, [
    '-y', '-framerate', String(fps), '-i', path.join(framesDirectory, 'frame-%06d.jpeg'),
    '-ss', String(fromSeconds), '-i', narration,
    '-ss', String(fromSeconds), '-i', sfx,
    '-t', String(durationSecondsExact),
    '-filter_complex', '[1:a]volume=1[n];[2:a]volume=0.36[s];[n][s]amix=inputs=2:duration=longest:normalize=0[a]',
    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', target,
  ]);
  fs.rmSync(framesDirectory, {recursive: true, force: true});
  console.log(`Rendered ${frameCount} frames (${fromSeconds}s–${toSeconds}s) to ${path.relative(root, target)}.`);
};
