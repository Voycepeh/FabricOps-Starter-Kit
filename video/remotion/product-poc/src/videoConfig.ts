import {FINAL_VIDEO_FRAME, NARRATION_CUE_SHEET, VIDEO_FPS, narrationFrame} from './narrationCues';

export {VIDEO_FPS};
export const seconds = narrationFrame;
export const NARRATION_START_FRAME = seconds(0);
export const WORKSPACE_ARCHITECTURE_DURATION_SECONDS = 96;
export const WORKSPACE_ARCHITECTURE_DURATION = seconds(WORKSPACE_ARCHITECTURE_DURATION_SECONDS);

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
    opening: NARRATION_CUE_SHEET.opening.transitionFrame - NARRATION_CUE_SHEET.opening.startFrame,
    fabricOps: NARRATION_CUE_SHEET.fabricOps.transitionFrame - NARRATION_CUE_SHEET.fabricOps.startFrame,
    notebooks: NARRATION_CUE_SHEET.notebooks.transitionFrame - NARRATION_CUE_SHEET.notebooks.startFrame,
    workflow: NARRATION_CUE_SHEET.lifecycle.transitionFrame - NARRATION_CUE_SHEET.lifecycle.startFrame,
  },
} as const;

const {scenes} = VIDEO_CONFIG;

export const SCENE_STARTS = {
  opening: NARRATION_CUE_SHEET.opening.startFrame,
  fabricOps: NARRATION_CUE_SHEET.fabricOps.startFrame,
  notebooks: NARRATION_CUE_SHEET.notebooks.startFrame,
  workflow: NARRATION_CUE_SHEET.lifecycle.startFrame,
} as const;

export const OVERVIEW_HANDOFF_FRAME = NARRATION_CUE_SHEET.consumption.startFrame;
export const LIFECYCLE_HANDOFF_LOCAL_FRAME = OVERVIEW_HANDOFF_FRAME - SCENE_STARTS.workflow;

export const GUIDED_SCENE_DURATIONS = {
  consumption: NARRATION_CUE_SHEET.consumption.transitionFrame - NARRATION_CUE_SHEET.consumption.startFrame,
  dataEngineers: NARRATION_CUE_SHEET.dataEngineers.transitionFrame - NARRATION_CUE_SHEET.dataEngineers.startFrame,
  repeatablePipeline: NARRATION_CUE_SHEET.repeatablePipeline.transitionFrame - NARRATION_CUE_SHEET.repeatablePipeline.startFrame,
  sensitiveData: NARRATION_CUE_SHEET.sensitiveData.transitionFrame - NARRATION_CUE_SHEET.sensitiveData.startFrame,
  businessRules: NARRATION_CUE_SHEET.businessRules.transitionFrame - NARRATION_CUE_SHEET.businessRules.startFrame,
  bigPicture: NARRATION_CUE_SHEET.bigPicture.transitionFrame - NARRATION_CUE_SHEET.bigPicture.startFrame,
  closing: NARRATION_CUE_SHEET.closing.transitionFrame - NARRATION_CUE_SHEET.closing.startFrame,
} as const;

export const REMOVED_PROMOTION_DURATION = NARRATION_CUE_SHEET.closing.startFrame - NARRATION_CUE_SHEET.bigPicture.transitionFrame;
export const CTA_TRIM_START_FRAMES = 75;

export const FULL_VIDEO_TIMELINE = {
  opening: {start: SCENE_STARTS.opening, duration: scenes.opening},
  fabricOps: {start: SCENE_STARTS.fabricOps, duration: scenes.fabricOps},
  notebooks: {start: SCENE_STARTS.notebooks, duration: scenes.notebooks},
  workspaceArchitecture: {
    start: NARRATION_CUE_SHEET.notebooks.transitionFrame,
    duration: WORKSPACE_ARCHITECTURE_DURATION,
  },
  lifecycle: {
    start: SCENE_STARTS.workflow + WORKSPACE_ARCHITECTURE_DURATION,
    duration: LIFECYCLE_HANDOFF_LOCAL_FRAME,
  },
  consumption: {
    start: NARRATION_CUE_SHEET.consumption.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.consumption,
  },
  dataEngineers: {
    start: NARRATION_CUE_SHEET.dataEngineers.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.dataEngineers,
  },
  repeatablePipeline: {
    start: NARRATION_CUE_SHEET.repeatablePipeline.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.repeatablePipeline,
  },
  sensitiveData: {
    start: NARRATION_CUE_SHEET.sensitiveData.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.sensitiveData,
  },
  businessRules: {
    start: NARRATION_CUE_SHEET.businessRules.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.businessRules,
  },
  bigPicture: {
    start: NARRATION_CUE_SHEET.bigPicture.startFrame + WORKSPACE_ARCHITECTURE_DURATION,
    duration: GUIDED_SCENE_DURATIONS.bigPicture,
  },
  closing: {
    start: NARRATION_CUE_SHEET.bigPicture.transitionFrame + WORKSPACE_ARCHITECTURE_DURATION,
    sourceStart: NARRATION_CUE_SHEET.closing.startFrame + CTA_TRIM_START_FRAMES,
    duration: GUIDED_SCENE_DURATIONS.closing - CTA_TRIM_START_FRAMES,
  },
} as const;

export const FULL_VIDEO_DURATION = FINAL_VIDEO_FRAME + WORKSPACE_ARCHITECTURE_DURATION - REMOVED_PROMOTION_DURATION - CTA_TRIM_START_FRAMES;
