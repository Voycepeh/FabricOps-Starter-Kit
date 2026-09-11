export const VIDEO_CONFIG = {
  sizes: {
    openingArtifactWidth: 240,
    openingArtifactHeight: 184,
    openingArtifactIcon: 132,
    notebookWidth: 440,
    notebookHeight: 230,
    contractWidth: 360,
    contractHeight: 180,
    workflowCardWidth: 340,
    workflowCardHeight: 150,
  },
  text: {
    fabricHero: 126,
    artifactLabel: 24,
    hero: 164,
    title: 66,
    subtitle: 46,
    notebook: 38,
    notebookEnvironment: 28,
    workflow: 27,
    cta: 30,
  },
  timing: {
    sceneGap: 30,
    itemStagger: 7,
    openingWavePause: 12,
    openingHeroHold: 42,
    openingQuestionAt: 172,
    operatingContractDelay: 115,
    operatingHandshakeDelay: 165,
    workflowStepGap: 45,
    workflowStepEnter: 18,
    validationLoopDuration: 35,
    sceneExit: 30,
  },
  scenes: {
    opening: 300,
    fabricOps: 210,
    notebooks: 300,
    workflow: 480,
    cta: 150,
  },
} as const;

const {scenes, timing} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: 0,
  fabricOps: scenes.opening,
  notebooks: scenes.opening + scenes.fabricOps + timing.sceneGap,
  workflow: scenes.opening + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap,
  cta: scenes.opening + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap + scenes.workflow + timing.sceneGap,
} as const;

export const VIDEO_DURATION = SCENE_STARTS.cta + scenes.cta;
