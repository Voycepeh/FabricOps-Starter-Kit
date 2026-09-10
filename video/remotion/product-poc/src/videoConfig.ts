export const VIDEO_CONFIG = {
  sizes: {
    openingArtifactCardWidth: 340,
    openingArtifactCardHeight: 160,
    openingArtifactIcon: 72,
    notebookWidth: 440,
    notebookHeight: 230,
    contractWidth: 300,
    contractHeight: 150,
  },
  text: {
    fabricHero: 126,
    artifactLabel: 32,
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
    cloneTravelX: 520,
    cloneTravelY: 180,
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
