import {copyFile, mkdir, readdir, readFile, unlink} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const mascotFiles = [
  'robot-carrying.png',
  'robot-coding.png',
  'robot-dev.png',
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
const sourceDirectory = path.join(repositoryRoot, 'docs', 'assets', 'mascots');
const targetDirectory = path.join(projectRoot, 'public', 'mascots');
const checkOnly = process.argv.includes('--check');

const readTargetEntries = async () => {
  try {
    return await readdir(targetDirectory);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
};

const sourceAssets = new Map();
for (const filename of mascotFiles) {
  sourceAssets.set(filename, await readFile(path.join(sourceDirectory, filename)));
}

if (sourceAssets.get('robot-masking.png').equals(sourceAssets.get('robot-validate.png'))) {
  throw new Error('robot-masking.png and robot-validate.png must remain distinct assets.');
}

const targetEntries = await readTargetEntries();
const obsoleteTargets = targetEntries.filter((filename) => filename.startsWith('robot-') && filename.endsWith('.png') && !sourceAssets.has(filename));

if (checkOnly) {
  const problems = [...obsoleteTargets.map((filename) => `obsolete target: ${filename}`)];
  for (const [filename, source] of sourceAssets) {
    try {
      const target = await readFile(path.join(targetDirectory, filename));
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
  if (problems.length > 0) {
    throw new Error(`Mascot asset check failed:\n${problems.join('\n')}`);
  }
  console.log(`Verified ${mascotFiles.length} synchronized mascot assets.`);
} else {
  await mkdir(targetDirectory, {recursive: true});
  await Promise.all([...sourceAssets.keys()].map((filename) => copyFile(
    path.join(sourceDirectory, filename),
    path.join(targetDirectory, filename),
  )));
  await Promise.all(obsoleteTargets.map((filename) => unlink(path.join(targetDirectory, filename))));
  console.log(`Synchronized ${mascotFiles.length} mascot assets from docs/assets/mascots.`);
}
