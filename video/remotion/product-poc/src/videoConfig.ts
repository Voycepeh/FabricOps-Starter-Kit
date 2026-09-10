export const VIDEO_CONFIG = {
  sizes: {
    fabricHeroIcon: 340,
    fabricHeroCardWidth: 860,
    fabricHeroCardHeight: 600,
    openingArtifactIcon: 112,
    openingArtifactCard: 156,
    notebookWidth: 440,
    notebookHeight: 240,
    notebookIcon: 120,
    notebookFocusScale: 1.42,
    workflowCardWidth: 340,
    workflowCardHeight: 150,
  },
  text: {
    fabricLabel: 68,
    artifactLabel: 32,
    hero: 164,
    title: 66,
    subtitle: 46,
    question: 136,
    notebook: 38,
    notebookEnvironment: 28,
    workflow: 27,
    cta: 30,
  },
  timing: {
    sceneGap: 30,
    itemStagger: 15,
    focusIn: 30,
    focusHold: 35,
    focusOut: 30,
    splitOverlap: 14,
    splitMove: 45,
    workflowStepGap: 45,
    workflowStepEnter: 18,
    validationLoopDuration: 35,
  },
  scenes: {
    opening: 210,
    question: 120,
    fabricOps: 150,
    notebooks: 420,
    workflow: 480,
    cta: 150,
  },
} as const;

const {scenes, timing} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: 0,
  question: scenes.opening + timing.sceneGap,
  fabricOps: scenes.opening + timing.sceneGap + scenes.question + timing.sceneGap,
  notebooks: scenes.opening + timing.sceneGap + scenes.question + timing.sceneGap + scenes.fabricOps + timing.sceneGap,
  workflow: scenes.opening + timing.sceneGap + scenes.question + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap,
  cta: scenes.opening + timing.sceneGap + scenes.question + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap + scenes.workflow + timing.sceneGap,
} as const;

export const VIDEO_DURATION = SCENE_STARTS.cta + scenes.cta;
