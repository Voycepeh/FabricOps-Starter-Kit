export const VIDEO_CONFIG = {
  sizes: {
    openingArtifactFootprint: 220,
    openingArtifactIcon: 112,
    notebookWidth: 440,
    notebookHeight: 230,
    contractWidth: 360,
    contractHeight: 180,
  },
  text: {
    fabricHero: 126,
    artifactLabel: 28,
    hero: 164,
    title: 66,
    subtitle: 46,
    notebook: 38,
    notebookEnvironment: 28,
    cta: 30,
  },
  timing: {
    sceneGap: 30,
    itemStagger: 22,
    cloneOverlap: 14,
    cloneDuration: 45,
    cloneTravelX: 0,
    cloneTravelY: 280,
    operatingContractDelay: 105,
    operatingPromotionDelay: 185,
    sceneExit: 30,
  },
  scenes: {
    opening: 270,
    fabricOps: 270,
    notebooks: 420,
    cta: 150,
  },
} as const;

const {scenes, timing} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: 0,
  fabricOps: scenes.opening + timing.sceneGap,
  notebooks: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap,
  cta: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap,
} as const;

export const VIDEO_DURATION = SCENE_STARTS.cta + scenes.cta;
