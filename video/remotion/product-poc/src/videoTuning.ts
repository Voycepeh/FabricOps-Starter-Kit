import {SCENE_STARTS} from './videoConfig';

export const globalSecondsToLocalFrame = (seconds: number, sceneStartFrame: number, fps: number) =>
  Math.round(seconds * fps - sceneStartFrame);

export const VIDEO_TUNING = {
  notebook: {
    timingSeconds: {
      packageEnter: 55.0,
      packageImports: [55.77, 56.77, 57.77],
      packageExit: 62.0,
      environment: 68.0,
      foundation: 78.0,
      lowerNotebooks: 78.0,
      contract: 86.3,
      relationship: 103.0,
    },
    layout: {
      package: {left: 420, top: 215, width: 1080, height: 610},
      environment: {left: 755, top: 235},
      governance: {left: 220, top: 650},
      contract: {left: 785, top: 555, width: 350, height: 400},
      pipeline: {left: 1290, top: 650},
      connectorY: 755,
    },
  },
  lifecycle: {
    timingSeconds: {
      steps: [119.2, 123.47, 128.93, 137.93, 153.5, 168.57, 178.7],
      loopStart: 141.7,
    },
    loop: {
      cx: 477,
      cy: 560,
      rx: 430,
      ry: 126,
      captionLeft: 327,
      captionTop: 700,
    },
  },
} as const;

export const notebookFrame = (seconds: number, fps: number) =>
  globalSecondsToLocalFrame(seconds, SCENE_STARTS.notebooks, fps);

export const lifecycleFrame = (seconds: number, fps: number) =>
  globalSecondsToLocalFrame(seconds, SCENE_STARTS.workflow, fps);
