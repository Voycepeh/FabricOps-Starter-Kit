import {FINAL_VIDEO_FRAME, NARRATION_CUE_SHEET, VIDEO_FPS, narrationFrame} from './narrationCues';

export {VIDEO_FPS};
export const seconds = narrationFrame;
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
  promotion: NARRATION_CUE_SHEET.promotion.transitionFrame - NARRATION_CUE_SHEET.promotion.startFrame,
  closing: NARRATION_CUE_SHEET.closing.transitionFrame - NARRATION_CUE_SHEET.closing.startFrame,
} as const;

export const FULL_VIDEO_TIMELINE = {
  opening: {start: SCENE_STARTS.opening, duration: scenes.opening},
  fabricOps: {start: SCENE_STARTS.fabricOps, duration: scenes.fabricOps},
  notebooks: {start: SCENE_STARTS.notebooks, duration: scenes.notebooks},
  lifecycle: {start: SCENE_STARTS.workflow, duration: LIFECYCLE_HANDOFF_LOCAL_FRAME},
  consumption: {start: NARRATION_CUE_SHEET.consumption.startFrame, duration: GUIDED_SCENE_DURATIONS.consumption},
  dataEngineers: {start: NARRATION_CUE_SHEET.dataEngineers.startFrame, duration: GUIDED_SCENE_DURATIONS.dataEngineers},
  repeatablePipeline: {start: NARRATION_CUE_SHEET.repeatablePipeline.startFrame, duration: GUIDED_SCENE_DURATIONS.repeatablePipeline},
  sensitiveData: {start: NARRATION_CUE_SHEET.sensitiveData.startFrame, duration: GUIDED_SCENE_DURATIONS.sensitiveData},
  businessRules: {start: NARRATION_CUE_SHEET.businessRules.startFrame, duration: GUIDED_SCENE_DURATIONS.businessRules},
  bigPicture: {start: NARRATION_CUE_SHEET.bigPicture.startFrame, duration: GUIDED_SCENE_DURATIONS.bigPicture},
  promotion: {start: NARRATION_CUE_SHEET.promotion.startFrame, duration: GUIDED_SCENE_DURATIONS.promotion},
  closing: {start: NARRATION_CUE_SHEET.closing.startFrame, duration: GUIDED_SCENE_DURATIONS.closing},
} as const;

export const FULL_VIDEO_DURATION = FINAL_VIDEO_FRAME;
