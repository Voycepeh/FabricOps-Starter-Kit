import {Series, useVideoConfig} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {FABRIC_OPS_PART_2_DURATION, FabricOpsPart2} from './FabricOpsPart2';

export const FABRIC_OPS_PART_1_HANDOFF_FRAME = 175 * 30;
export const FABRIC_OPS_FULL_VIDEO_DURATION = FABRIC_OPS_PART_1_HANDOFF_FRAME + FABRIC_OPS_PART_2_DURATION;

export const FabricOpsFullVideo = () => {
  const {fps} = useVideoConfig();

  return <Series>
    <Series.Sequence name="Part 1 · FabricOps overview" durationInFrames={175 * fps} premountFor={fps}>
      <FabricOpsHero />
    </Series.Sequence>
    <Series.Sequence name="Part 2 · Consumption and guided demo" durationInFrames={FABRIC_OPS_PART_2_DURATION} premountFor={fps}>
      <FabricOpsPart2 />
    </Series.Sequence>
  </Series>;
};
