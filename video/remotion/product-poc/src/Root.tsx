import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {FABRIC_OPS_PART_2_DURATION, FabricOpsPart2} from './FabricOpsPart2';
import {VIDEO_DURATION} from './videoConfig';

export const Root = () => (
  <>
    <Composition
      id="FabricOpsHero"
      component={FabricOpsHero}
      durationInFrames={VIDEO_DURATION}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="FabricOpsPart2"
      component={FabricOpsPart2}
      durationInFrames={FABRIC_OPS_PART_2_DURATION}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);
