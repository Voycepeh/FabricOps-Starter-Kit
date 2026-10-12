export const VIDEO_FPS = 30;
export const seconds = (value: number) => Math.round(value * VIDEO_FPS);
export const NARRATION_START_FRAME = seconds(0);

export const VIDEO_CONFIG = {
  sizes: {
    workflowCardWidth: 340,
    workflowCardHeight: 150,
  },
  text: {
    fabricHero: 126,
    hero: 164,
    title: 66,
    workflow: 24,
  },
  timing: {
    sceneGap: 0,
    openingMascotAt: 160,
    openingFabricExitAt: 470,
    openingQuestionAt: 480,
    openingQuestionEnterFrames: 12,
    openingPushAt: 527,
    workflowStepEnter: 18,
    sceneExit: 24,
  },
  scenes: {
    opening: 556,
    fabricOps: 1069,
    notebooks: 1851,
    workflow: 2147,
  },
} as const;

const {scenes, timing} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: 0,
  fabricOps: scenes.opening + timing.sceneGap,
  notebooks: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap,
  workflow: scenes.opening + timing.sceneGap + scenes.fabricOps + timing.sceneGap + scenes.notebooks + timing.sceneGap,
} as const;

export const OVERVIEW_HANDOFF_FRAME = seconds(175);
export const LIFECYCLE_HANDOFF_LOCAL_FRAME = OVERVIEW_HANDOFF_FRAME - SCENE_STARTS.workflow;

export const GUIDED_SCENE_DURATIONS = {
  consumption: seconds(24),
  engineering: seconds(13),
  governance: seconds(20),
  validation: seconds(12),
  activation: seconds(13),
  closing: seconds(7.4),
} as const;

export const FULL_VIDEO_TIMELINE = {
  opening: {start: SCENE_STARTS.opening, duration: scenes.opening},
  fabricOps: {start: SCENE_STARTS.fabricOps, duration: scenes.fabricOps},
  notebooks: {start: SCENE_STARTS.notebooks, duration: scenes.notebooks},
  lifecycle: {start: SCENE_STARTS.workflow, duration: LIFECYCLE_HANDOFF_LOCAL_FRAME},
  consumption: {start: OVERVIEW_HANDOFF_FRAME, duration: GUIDED_SCENE_DURATIONS.consumption},
  engineering: {
    start: OVERVIEW_HANDOFF_FRAME + GUIDED_SCENE_DURATIONS.consumption,
    duration: GUIDED_SCENE_DURATIONS.engineering,
  },
  governance: {
    start: OVERVIEW_HANDOFF_FRAME + GUIDED_SCENE_DURATIONS.consumption + GUIDED_SCENE_DURATIONS.engineering,
    duration: GUIDED_SCENE_DURATIONS.governance,
  },
  validation: {
    start: OVERVIEW_HANDOFF_FRAME + GUIDED_SCENE_DURATIONS.consumption + GUIDED_SCENE_DURATIONS.engineering + GUIDED_SCENE_DURATIONS.governance,
    duration: GUIDED_SCENE_DURATIONS.validation,
  },
  activation: {
    start: OVERVIEW_HANDOFF_FRAME + GUIDED_SCENE_DURATIONS.consumption + GUIDED_SCENE_DURATIONS.engineering + GUIDED_SCENE_DURATIONS.governance + GUIDED_SCENE_DURATIONS.validation,
    duration: GUIDED_SCENE_DURATIONS.activation,
  },
  closing: {
    start: OVERVIEW_HANDOFF_FRAME + GUIDED_SCENE_DURATIONS.consumption + GUIDED_SCENE_DURATIONS.engineering + GUIDED_SCENE_DURATIONS.governance + GUIDED_SCENE_DURATIONS.validation + GUIDED_SCENE_DURATIONS.activation,
    duration: GUIDED_SCENE_DURATIONS.closing,
  },
} as const;

export const FULL_VIDEO_DURATION = FULL_VIDEO_TIMELINE.closing.start + FULL_VIDEO_TIMELINE.closing.duration;
