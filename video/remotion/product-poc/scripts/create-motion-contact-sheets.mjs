import fs from 'node:fs';
import path from 'node:path';
import {ffmpeg, output, root, run, timeline} from './motion-render-utils.mjs';

const source = path.join(output, 'FabricOps-Part1-Motion-Full.mp4');
if (!fs.existsSync(source)) throw new Error(`Missing full render: ${source}`);
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const sheets = path.join(output, 'contact-sheets', timestamp);
fs.mkdirSync(sheets, {recursive: true});

for (const scene of timeline.scenes) {
  const duration = scene.end - scene.start;
  const count = Math.max(1, Math.ceil(duration / 4));
  const columns = Math.min(4, count);
  const rows = Math.ceil(count / columns);
  const target = path.join(sheets, `${scene.id}-contact-sheet.png`);
  const filter = `setpts=PTS+${scene.start}/TB,fps=1/4,scale=480:270,drawtext=text='t=%{pts\\:hms}':x=14:y=14:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=7,tile=${columns}x${rows}:padding=6:margin=6:color=0x111827`;
  run(ffmpeg, ['-y', '-ss', String(scene.start), '-t', String(duration), '-i', source, '-vf', filter, '-frames:v', '1', '-update', '1', target]);
}

const transitionTimes = timeline.scenes.slice(1).flatMap((scene) => [scene.start - 0.5, scene.start, scene.start + 0.5]);
const selectedFrames = [...new Set([...timeline.reviewTimes, ...transitionTimes]
  .filter((seconds) => seconds >= 0 && seconds < timeline.durationSeconds)
  .map((seconds) => Math.round(seconds * timeline.fps)))].sort((left, right) => left - right);
const selection = selectedFrames.map((frame) => `eq(n\\,${frame})`).join('+');
const columns = 5;
const rows = Math.ceil(selectedFrames.length / columns);
const reviewTarget = path.join(sheets, 'significant-beats-contact-sheet.png');
const reviewFilter = `select='${selection}',scale=384:216,drawtext=text='t=%{pts\\:hms}':x=12:y=12:fontsize=19:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=6,tile=${columns}x${rows}:padding=5:margin=5:color=0x111827`;
run(ffmpeg, ['-y', '-i', source, '-vf', reviewFilter, '-fps_mode', 'vfr', '-frames:v', '1', '-update', '1', reviewTarget]);
console.log(`Contact sheets: ${path.relative(root, sheets)}`);
