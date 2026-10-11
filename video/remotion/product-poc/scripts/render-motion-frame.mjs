import fs from 'node:fs';
import path from 'node:path';
import {formatTimestamp, output, parseTimestamp, readArgument, root, runRemotion, stageAudio, timeline} from './motion-render-utils.mjs';

const seconds = parseTimestamp(readArgument('--at'));
if (!(seconds >= 0 && seconds < timeline.durationSeconds)) throw new Error(`Frame timestamp must be between 0 and ${timeline.durationSeconds}.`);
const frame = Math.round(seconds * timeline.fps);
const temporary = path.join(output, `frame-temp-${frame}`);
const targetDirectory = path.join(output, 'frames');
const target = path.join(targetDirectory, `FabricOps-Part1-Motion-${formatTimestamp(seconds)}.jpeg`);
fs.mkdirSync(targetDirectory, {recursive: true});
fs.rmSync(temporary, {recursive: true, force: true});
stageAudio();
runRemotion(['render', 'src/index.ts', 'FabricOpsPart1Motion', temporary, '--sequence', '--image-format=jpeg', '--jpeg-quality=95', '--muted', `--frames=${frame}-${frame}`]);
const rendered = fs.readdirSync(temporary).find((file) => /\.(jpe?g)$/i.test(file));
if (!rendered) throw new Error(`No frame was rendered at ${seconds}s.`);
fs.copyFileSync(path.join(temporary, rendered), target);
fs.rmSync(temporary, {recursive: true, force: true});
console.log(`Frame ${frame} (${seconds}s) exported to ${path.relative(root, target)}.`);
