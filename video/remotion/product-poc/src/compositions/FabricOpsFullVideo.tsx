import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile, useVideoConfig} from 'remotion';
import {font, theme} from '../theme';
import {
  FULL_VIDEO_TIMELINE,
  OVERVIEW_HANDOFF_FRAME,
} from '../videoConfig';
import {ActivationScene, ClosingScene, EngineeringScene, GovernanceScene, ValidationScene} from '../scenes/GuidedDemoScenes';
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
      <Sequence name="Narration" from={0} durationInFrames={OVERVIEW_HANDOFF_FRAME} premountFor={fps}>
        <Audio src={staticFile('audio/FabricOps_narration_master_numbered.m4a')} volume={1} />
      </Sequence>

      <Sequence name="Overview background" from={0} durationInFrames={OVERVIEW_HANDOFF_FRAME} premountFor={fps}>
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
      <Sequence name="Engineering" from={timeline.engineering.start} durationInFrames={timeline.engineering.duration} premountFor={fps}>
        <EngineeringScene />
      </Sequence>
      <Sequence name="Governance" from={timeline.governance.start} durationInFrames={timeline.governance.duration} premountFor={fps}>
        <GovernanceScene />
      </Sequence>
      <Sequence name="Validation" from={timeline.validation.start} durationInFrames={timeline.validation.duration} premountFor={fps}>
        <ValidationScene />
      </Sequence>
      <Sequence name="Activation and production" from={timeline.activation.start} durationInFrames={timeline.activation.duration} premountFor={fps}>
        <ActivationScene />
      </Sequence>
      <Sequence name="CTA" from={timeline.closing.start} durationInFrames={timeline.closing.duration} premountFor={fps}>
        <ClosingScene />
      </Sequence>
    </AbsoluteFill>
  );
};
