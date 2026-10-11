import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'out', 'motion-experiment');
const require = createRequire(import.meta.url);
const ffmpeg = require('ffmpeg-static');
const inputs = [
  'FabricOps-Part1-Original-Sample.mp4',
  'FabricOps-Part1-Claude-Motion-Sample.mp4',
  'FabricOps-Part1-Motion-Comparison.mp4',
];
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const sheets = path.join(output, 'contact-sheets', timestamp);
fs.mkdirSync(sheets, {recursive: true});

for (const input of inputs) {
  const source = path.join(output, input);
  if (!fs.existsSync(source)) throw new Error(`Missing render: ${source}`);
  const target = path.join(sheets, `${path.parse(input).name}-contact-sheet.png`);
  const filter = "fps=1/2.5,scale=640:360,drawtext=font='Consolas':text='t=%{pts\\:hms}':x=18:y=18:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=8,tile=3x4:padding=6:margin=6:color=0x111827";
  const result = spawnSync(ffmpeg, ['-y', '-i', source, '-vf', filter, '-frames:v', '1', '-update', '1', target], {cwd: root, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
}
console.log(`Contact sheets: ${path.relative(root, sheets)}`);
