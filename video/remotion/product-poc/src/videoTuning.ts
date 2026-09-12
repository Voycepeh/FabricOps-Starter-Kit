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
  notebook: {
    packageStartSeconds: 55,
    packageImportSeconds: [55.77, 56.77, 57.77],
    packageEndSeconds: 62,
    environmentSeconds: 68,
    lowerNotebooksSeconds: 78,
    contractSeconds: 86.3,
    relationshipSeconds: 103,
    layout: {
      codePackage: {left: 420, top: 215, width: 1080, height: 610},
      environment: {left: 755, top: 235},
      governance: {left: 220, top: 650},
      contract: {left: 785, top: 555, width: 350, height: 400},
      pipeline: {left: 1290, top: 650},
    },
  },
  lifecycle: {
    stepSeconds: [119.2, 123.47, 128.93, 137.93, 153.5, 168.57, 178.7],
    loopStartSeconds: 141.7,
    loop: {cx: 477, cy: 560, rx: 430, ry: 126},
    loopCaption: {left: 327, top: 700, width: 300},
  },
} as const;

export const secondsToFrames = (seconds: number, fps: number) => Math.round(seconds * fps);

export const globalSecondsToLocalFrame = (
  seconds: number,
  sceneStartFrame: number,
  fps: number,
) => secondsToFrames(seconds, fps) - sceneStartFrame;
