import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile, useVideoConfig} from 'remotion';
import {font, theme} from '../theme';
import {
  FULL_VIDEO_DURATION,
  FULL_VIDEO_TIMELINE,
  NARRATION_START_FRAME,
} from '../videoConfig';
import {
  BigPictureScene,
  BusinessRulesScene,
  ClosingScene,
  DataEngineersScene,
  PromotionScene,
  RepeatablePipelineScene,
  SensitiveDataScene,
} from '../scenes/GuidedDemoScenes';
import {ConsumptionScene} from '../scenes/ConsumptionScene';
import {FabricOpsReveal} from '../scenes/FabricOpsReveal';
import {LifecycleScene} from '../scenes/LifecycleScene';
import {NotebookJourney} from '../scenes/NotebookJourney';
import {OpeningPlatform} from '../scenes/OpeningPlatform';

export const FabricOpsFullVideo = () => {
  const {fps} = useVideoConfig();
  const timeline = FULL_VIDEO_TIMELINE;

  return (
    <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
      <Audio
        name="Normalized master narration"
        from={NARRATION_START_FRAME}
        src={staticFile('audio/FabricOps_full_narration_normalized.m4a')}
        volume={1}
      />
      <Sequence
        name="Overview background"
        from={0}
        durationInFrames={FULL_VIDEO_DURATION}
        premountFor={fps}>
        <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}} />
      </Sequence>
      <Sequence name="Opening" from={timeline.opening.start} durationInFrames={timeline.opening.duration} premountFor={fps}>
        <OpeningPlatform />
      </Sequence>
      <Sequence name="FabricOps solution" from={timeline.fabricOps.start} durationInFrames={timeline.fabricOps.duration} premountFor={fps}>
        <FabricOpsReveal />
      </Sequence>
      <Sequence name="Notebook journey" from={timeline.notebooks.start} durationInFrames={timeline.notebooks.duration} premountFor={fps}>
        <NotebookJourney />
      </Sequence>
      <Sequence name="Lifecycle" from={timeline.lifecycle.start} durationInFrames={timeline.lifecycle.duration} premountFor={fps}>
        <LifecycleScene />
      </Sequence>
      <Sequence name="Consumption" from={timeline.consumption.start} durationInFrames={timeline.consumption.duration} premountFor={fps}>
        <ConsumptionScene />
      </Sequence>
      <Sequence name="Data engineers" from={timeline.dataEngineers.start} durationInFrames={timeline.dataEngineers.duration} premountFor={fps}>
        <DataEngineersScene />
      </Sequence>
      <Sequence name="Repeatable pipeline" from={timeline.repeatablePipeline.start} durationInFrames={timeline.repeatablePipeline.duration} premountFor={fps}>
        <RepeatablePipelineScene />
      </Sequence>
      <Sequence name="Sensitive data" from={timeline.sensitiveData.start} durationInFrames={timeline.sensitiveData.duration} premountFor={fps}>
        <SensitiveDataScene />
      </Sequence>
      <Sequence name="Business rules" from={timeline.businessRules.start} durationInFrames={timeline.businessRules.duration} premountFor={fps}>
        <BusinessRulesScene />
      </Sequence>
      <Sequence name="The big picture" from={timeline.bigPicture.start} durationInFrames={timeline.bigPicture.duration} premountFor={fps}>
        <BigPictureScene />
      </Sequence>
      <Sequence name="Promotion" from={timeline.promotion.start} durationInFrames={timeline.promotion.duration} premountFor={fps}>
        <PromotionScene />
      </Sequence>
      <Sequence name="CTA" from={timeline.closing.start} durationInFrames={timeline.closing.duration} premountFor={fps}>
        <ClosingScene />
      </Sequence>
    </AbsoluteFill>
  );
};
