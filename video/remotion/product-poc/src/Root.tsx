import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {VIDEO_DURATION} from './videoConfig';

export const Root = () => (
  <Composition
    id="FabricOpsHero"
    component={FabricOpsHero}
    durationInFrames={VIDEO_DURATION}
    fps={30}
    width={1920}
    height={1080}
  />
);
