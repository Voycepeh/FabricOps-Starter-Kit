import path from 'node:path';
import {formatTimestamp, output, parseTimestamp, readArgument, renderRange, timeline} from './motion-render-utils.mjs';

const full = process.argv.includes('--full');
const fromSeconds = full ? 0 : parseTimestamp(readArgument('--from'));
const toSeconds = full ? timeline.durationSeconds : parseTimestamp(readArgument('--to'));
const filename = full
  ? 'FabricOps-Part1-Motion-Full.mp4'
  : `FabricOps-Part1-Motion-${formatTimestamp(fromSeconds)}-to-${formatTimestamp(toSeconds)}.mp4`;

renderRange({fromSeconds, toSeconds, target: path.join(output, filename)});
