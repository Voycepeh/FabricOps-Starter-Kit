import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'out', 'motion-experiment');
const require = createRequire(import.meta.url);
const ffmpeg = require('ffmpeg-static');
const remotionCli = path.join(root, 'node_modules', '@remotion', 'cli', 'remotion-cli.js');
const run = (args) => {
  const cliArgs = args[0] === 'remotion' ? args.slice(1) : args;
  const result = spawnSync(process.execPath, [remotionCli, ...cliArgs], {cwd: root, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
};
const runFfmpeg = (args) => {
  const result = spawnSync(ffmpeg, args, {cwd: root, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
};
const node = process.execPath;
const runNode = (args) => {
  const result = spawnSync(node, args, {cwd: root, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
};

fs.mkdirSync(output, {recursive: true});
runNode(['scripts/generate-motion-experiment-sfx.mjs']);

const original = path.join(output, 'FabricOps-Part1-Original-Sample.mp4');
const enhanced = path.join(output, 'FabricOps-Part1-Claude-Motion-Sample.mp4');
const comparison = path.join(output, 'FabricOps-Part1-Motion-Comparison.mp4');
const narration = path.join(root, 'public', 'audio', 'FabricOps_narration_master_numbered.m4a');
const sfx = path.join(root, 'public', 'generated', 'motion-experiment-sfx.wav');
const originalFrames = path.join(output, 'original-frames');
const enhancedFrames = path.join(output, 'enhanced-frames');

run(['remotion', 'render', 'src/index.ts', 'FabricOpsPart1OriginalSample', originalFrames, '--sequence', '--image-format=jpeg', '--jpeg-quality=95', '--muted', '--concurrency=4']);
run(['remotion', 'render', 'src/index.ts', 'FabricOpsPart1MotionExperiment', enhancedFrames, '--sequence', '--image-format=jpeg', '--jpeg-quality=95', '--muted', '--concurrency=4']);

runFfmpeg(['-y', '-framerate', '30', '-i', path.join(originalFrames, 'element-%03d.jpeg'), '-ss', '153.5', '-i', narration, '-t', '29.5', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', original]);
runFfmpeg(['-y', '-framerate', '30', '-i', path.join(enhancedFrames, 'element-%03d.jpeg'), '-ss', '153.5', '-i', narration, '-i', sfx, '-t', '29.5', '-filter_complex', '[1:a]volume=1[n];[2:a]volume=0.42[s];[n][s]amix=inputs=2:duration=first:normalize=0[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', enhanced]);
runFfmpeg(['-y', '-i', original, '-i', enhanced, '-filter_complex', "[0:v]fps=30,setpts=PTS-STARTPTS,drawtext=font='Consolas':text='VERSION A  |  ORIGINAL':x=64:y=54:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.72:boxborderw=18[left];[1:v]fps=30,setpts=PTS-STARTPTS,drawtext=font='Consolas':text='VERSION B  |  MOTION ENHANCED':x=64:y=54:fontsize=34:fontcolor=0x38d991:box=1:boxcolor=black@0.72:boxborderw=18[right];[left][right]hstack=inputs=2:shortest=0[v]", '-map', '[v]', '-map', '1:a', '-t', '29.5', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', comparison]);

for (const frames of [originalFrames, enhancedFrames]) fs.rmSync(frames, {recursive: true, force: true});
