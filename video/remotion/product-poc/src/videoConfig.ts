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
    openingQuestionAt: 455,
    openingPushAt: 527,
    fabricOpsWhyAt: 629,
    fabricOpsWhyExitAt: 705,
    fabricOpsHowAt: 961,
    fabricOpsWorksAt: 982,
    notebookEnvironmentAt: 415,
    notebookFoundationAt: 715,
    notebookLowerAt: 715,
    notebookContractAt: 964,
    notebookRelationshipAt: 1005,
    workflowStepTimes: [100, 228, 392, 662, 1129, 1581, 1885],
    workflowLoopStart: 775,
    workflowLoopEnd: 1085,
    workflowStepEnter: 18,
    ctaHowAt: 170,
    ctaDemoAt: 304,
    sceneExit: 24,
  },
  scenes: {
    opening: 556,
    fabricOps: 1069,
    notebooks: 1851,
    workflow: 2147,
    cta: 464,
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
