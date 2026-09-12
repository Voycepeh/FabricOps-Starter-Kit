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
      Notebook: {left: 120, top: 500},
      'Data Pipeline': {left: 380, top: 500},
      Lakehouse: {left: 640, top: 500},
      Warehouse: {left: 900, top: 500},
      Environment: {left: 1160, top: 500},
      Eventstream: {left: 1420, top: 500},
      'Dataflow Gen2': {left: 70, top: 55},
      'Data Engineering': {left: 360, top: 70},
      'Data Science': {left: 1490, top: 60},
      'SQL Database': {left: 70, top: 790},
      Eventhouse: {left: 360, top: 820},
      'Semantic Model': {left: 1490, top: 790},
      Report: {left: 70, top: 285},
      Dashboard: {left: 70, top: 535},
      'Mirrored Database': {left: 1490, top: 285},
      'ML Model': {left: 1490, top: 535},
      OneLake: {left: 660, top: 815},
      'Graph Intelligence': {left: 1020, top: 815},
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
