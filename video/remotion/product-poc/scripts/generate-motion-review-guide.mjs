import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const timeline = JSON.parse(fs.readFileSync(path.join(root, 'src', 'motion-experiment', 'timeline.json'), 'utf8'));
const stamp = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainder = (seconds - minutes * 60).toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
  const [wholeSeconds, fraction] = remainder.split('.');
  return `${String(minutes).padStart(2, '0')}:${wholeSeconds.padStart(2, '0')}${fraction ? `.${fraction}` : ''}`;
};

const lines = [
  '# FabricOps Part 1 motion review guide',
  '',
  `Composition: \`FabricOpsPart1Motion\` | ${timeline.durationSeconds} seconds | ${timeline.fps} fps`,
  '',
  'All timestamps map directly to `src/motion-experiment/timeline.json`. Camera, element, text-hold and sound changes should be made there first; scene markup remains the content authority.',
  '',
];

for (const scene of timeline.scenes) {
  lines.push(`## ${stamp(scene.start)}-${stamp(scene.end)} - ${scene.title}`, '');
  lines.push(`- Intended message: ${scene.message}`);
  lines.push(`- Primary visual focus: ${scene.primaryFocus}`);
  lines.push(`- Visible text: ${scene.visibleText.join('; ')}`);
  lines.push(`- Narration alignment: ${scene.narrationAlignment}`);
  lines.push(`- Camera movement: ${scene.camera.map((keyframe) => `${stamp(keyframe.at)} focus (${keyframe.x}, ${keyframe.y}) at ${keyframe.scale.toFixed(2)}x`).join(' -> ')}`);
  lines.push(`- Key animation beats: ${scene.beats.map((beat) => `${stamp(beat.at)} ${beat.id}`).join('; ')}`);
  lines.push(`- Element windows: ${scene.elements.map((element) => `${element.id} ${stamp(element.appear)}-${stamp(element.disappear)}`).join('; ')}`);
  lines.push(`- Text holds: ${scene.textHolds.map((hold) => `${hold.text} ${stamp(hold.start)}-${stamp(hold.end)}`).join('; ')}`, '');
}

lines.push('## Targeted revision examples', '', '- "At 01:26, delay the zoom by one second" -> adjust the adjacent `notebooks.camera` keyframes.', '- "At 01:42, remove the secondary label" -> adjust the relevant `notebooks.elements` window and its scene markup if removal is permanent.', '- "At 02:10, hold the governance diagram longer" -> adjust the `lifecycle.camera`, `beats` and matching `textHolds` entries.', '', 'Use `npm run motion:frame -- --at 01:26.5` for an exact frame and `npm run motion:preview -- --from 01:24 --to 01:32` for a synchronized review segment.');
fs.writeFileSync(path.join(root, 'MOTION_REVIEW_GUIDE.md'), `${lines.join('\n')}\n`);
console.log('Generated MOTION_REVIEW_GUIDE.md.');
