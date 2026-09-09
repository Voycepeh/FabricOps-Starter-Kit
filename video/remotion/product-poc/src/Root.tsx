import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';

export const Root = () => (
  <Composition
    id="FabricOpsHero"
    component={FabricOpsHero}
    durationInFrames={900}
    fps={30}
    width={1920}
    height={1080}
  />
);
