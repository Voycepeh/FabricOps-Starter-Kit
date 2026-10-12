import {copyFile, mkdir, readdir, readFile, unlink} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const mascotFiles = [
  'robot-carrying.png',
  'robot-coding.png',
  'robot-dev.png',
  'robot-dragging.png',
  'robot-masking.png',
  'robot-neutral.png',
  'robot-pointing.png',
  'robot-prod.png',
  'robot-scanning.png',
  'robot-validate.png',
  'robot-writing.png',
];

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = path.resolve(projectRoot, '../../..');
const sourceMascotDirectory = path.join(repositoryRoot, 'docs', 'assets', 'mascots');
const targetMascotDirectory = path.join(projectRoot, 'public', 'mascots');
const narrationFilename = 'FabricOps_narration_master_numbered.m4a';
const sourceNarration = path.join(projectRoot, narrationFilename);
const targetAudioDirectory = path.join(projectRoot, 'public', 'audio');
const targetNarration = path.join(targetAudioDirectory, narrationFilename);
const checkOnly = process.argv.includes('--check');

const readTargetEntries = async () => {
  try {
    return await readdir(targetMascotDirectory);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
};

const sourceAssets = new Map();
for (const filename of mascotFiles) {
  sourceAssets.set(filename, await readFile(path.join(sourceMascotDirectory, filename)));
}
const narration = await readFile(sourceNarration);

if (sourceAssets.get('robot-masking.png').equals(sourceAssets.get('robot-validate.png'))) {
  throw new Error('robot-masking.png and robot-validate.png must remain distinct assets.');
}

const targetEntries = await readTargetEntries();
const obsoleteTargets = targetEntries.filter((filename) => filename.startsWith('robot-') && filename.endsWith('.png') && !sourceAssets.has(filename));

if (checkOnly) {
  const problems = [...obsoleteTargets.map((filename) => `obsolete target: ${filename}`)];
  for (const [filename, source] of sourceAssets) {
    try {
      const target = await readFile(path.join(targetMascotDirectory, filename));
      if (!source.equals(target)) {
        problems.push(`out-of-sync target: ${filename}`);
      }
    } catch (error) {
      if (error.code === 'ENOENT') {
        problems.push(`missing target: ${filename}`);
      } else {
        throw error;
      }
    }
  }
  try {
    const target = await readFile(targetNarration);
    if (!narration.equals(target)) {
      problems.push(`out-of-sync target: public/audio/${narrationFilename}`);
    }
  } catch (error) {
    if (error.code === 'ENOENT') {
      problems.push(`missing target: public/audio/${narrationFilename}`);
    } else {
      throw error;
    }
  }
  if (problems.length > 0) {
    throw new Error(`Remotion asset check failed:\n${problems.join('\n')}`);
  }
  console.log(`Verified narration and ${mascotFiles.length} synchronized mascot assets.`);
} else {
  await mkdir(targetMascotDirectory, {recursive: true});
  await mkdir(targetAudioDirectory, {recursive: true});
  await Promise.all([...sourceAssets.keys()].map((filename) => copyFile(
    path.join(sourceMascotDirectory, filename),
    path.join(targetMascotDirectory, filename),
  )));
  await copyFile(sourceNarration, targetNarration);
  await Promise.all(obsoleteTargets.map((filename) => unlink(path.join(targetMascotDirectory, filename))));
  console.log(`Synchronized narration and ${mascotFiles.length} mascot assets.`);
}
