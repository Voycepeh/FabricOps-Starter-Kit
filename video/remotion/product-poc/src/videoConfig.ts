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
    sceneGap: 0,
    itemStagger: 7,
    openingWavePause: 12,
    openingHeroHold: 42,
    openingQuestionAt: 469,
    openingPushAt: 553,
    fabricOpsWhyAt: 387,
    fabricOpsWhyExitAt: 473,
    fabricOpsHowAt: 743,
    notebookEnvironmentAt: 75,
    notebookRelationshipAt: 245,
    notebookContractAt: 360,
    notebookFlowAt: 500,
    workflowStepEnter: 18,
    sceneExit: 24,
  },
  scenes: {
    opening: 573,
    fabricOps: 857,
    notebooks: 891,
    workflow: 2033,
    cta: 472,
  },
} as const;

const {scenes, timing} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: 0,
  fabricOps: scenes.opening + timing.sceneGap,
  notebooks: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap,
  workflow: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap,
  cta: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap + scenes.workflow + timing.sceneGap,
} as const;

export const VIDEO_DURATION = SCENE_STARTS.cta + scenes.cta;
