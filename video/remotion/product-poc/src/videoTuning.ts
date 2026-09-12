import {SCENE_STARTS} from './videoConfig';

export const globalSecondsToLocalFrame = (seconds: number, sceneStartFrame: number, fps: number) =>
  Math.round(seconds * fps - sceneStartFrame);

export const secondsToFrames = (seconds: number, fps: number) => Math.round(seconds * fps);

export const VIDEO_TUNING = {
  opening: {
    iconPopulationStartSeconds: 3,
    iconEntryFrames: 28,
    iconBurstOffsetsSeconds: [
      0, 0.05, 0.1, 0.15, 0.2, 0.25,
      0.45, 0.55, 0.65, 0.8, 0.95, 1.1,
      1.25, 1.4, 1.55, 1.7, 1.85, 2.05,
    ],
    heroCenterY: 360,
    positions: {
      Notebook: {left: 135, top: 510},
      'Data Pipeline': {left: 395, top: 510},
      Lakehouse: {left: 655, top: 510},
      Warehouse: {left: 915, top: 510},
      Environment: {left: 1175, top: 510},
      Eventstream: {left: 1435, top: 510},
      'Dataflow Gen2': {left: 40, top: 45},
      'Data Engineering': {left: 320, top: 55},
      'Data Science': {left: 1360, top: 55},
      'SQL Database': {left: 1640, top: 45},
      Eventhouse: {left: 40, top: 280},
      'Semantic Model': {left: 1640, top: 280},
      Report: {left: 40, top: 735},
      Dashboard: {left: 1640, top: 735},
      'Mirrored Database': {left: 300, top: 850},
      'ML Model': {left: 580, top: 850},
      OneLake: {left: 1100, top: 850},
      'Graph Intelligence': {left: 1380, top: 850},
    },
  },
  fabricOps: {
    floatingWords: {
      operations: 21,
      plugAndPlay: 22.5,
      selfContained: 28,
      python: 31.5,
      notebook: 33,
      pyspark: 33.5,
      lakehouse: 35,
    },
    relationship: {
      governanceAsCodeStart: 43,
      governanceAsCodeEnd: 45,
      governance: 45.5,
      engineering: 46,
      orbitStart: 48,
      end: 50,
    },
    prompts: {
      why: 39.5,
      whyExit: 42.03,
      how: 50.57,
      works: 51.27,
    },
  },
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

export const fabricOpsFrame = (seconds: number, fps: number) =>
  globalSecondsToLocalFrame(seconds, SCENE_STARTS.fabricOps, fps);

export const notebookFrame = (seconds: number, fps: number) =>
  globalSecondsToLocalFrame(seconds, SCENE_STARTS.notebooks, fps);

export const lifecycleFrame = (seconds: number, fps: number) =>
  globalSecondsToLocalFrame(seconds, SCENE_STARTS.workflow, fps);
