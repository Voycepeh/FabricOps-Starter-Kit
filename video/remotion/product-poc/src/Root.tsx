import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {FabricOpsOverview, OVERVIEW_DURATION_IN_FRAMES} from './FabricOpsOverview';

export const Root = () => (<>
  <Composition
    id="FabricOpsHero"
    component={FabricOpsHero}
    durationInFrames={900}
    fps={30}
    width={1920}
    height={1080}
  />
  <Composition id="FabricOpsOverview" component={FabricOpsOverview} durationInFrames={OVERVIEW_DURATION_IN_FRAMES} fps={30} width={1920} height={1080} />
</>);
