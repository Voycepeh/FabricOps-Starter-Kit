import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {LONG_FORM_STORY_FRAMES} from './scenes/LongFormStory';

export const Root = () => (
  <Composition
    id="FabricOpsHero"
    component={FabricOpsHero}
    durationInFrames={LONG_FORM_STORY_FRAMES}
    fps={30}
    width={1920}
    height={1080}
  />
);
