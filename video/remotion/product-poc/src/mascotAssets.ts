import {staticFile} from 'remotion';

export const mascotFiles = {
  carrying: 'robot-carrying.png',
  coding: 'robot-coding.png',
  dev: 'robot-dev.png',
  dragging: 'robot-dragging.png',
  masking: 'robot-masking.png',
  neutral: 'robot-neutral.png',
  pointing: 'robot-pointing.png',
  prod: 'robot-prod.png',
  scanning: 'robot-scanning.png',
  validate: 'robot-validate.png',
  writing: 'robot-writing.png',
} as const;

export type MascotName = keyof typeof mascotFiles;

export const mascotSrc = (mascot: MascotName) => staticFile(`mascots/${mascotFiles[mascot]}`);
