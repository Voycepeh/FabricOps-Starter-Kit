import {Composition} from 'remotion';
import {FabricOpsFullVideo} from './compositions/FabricOpsFullVideo';
import {FULL_VIDEO_DURATION, VIDEO_FPS} from './videoConfig';

export const Root = () => (
  <>
    <Composition
      id="FabricOpsFullVideo"
      component={FabricOpsFullVideo}
      durationInFrames={FULL_VIDEO_DURATION}
      fps={VIDEO_FPS}
      width={1920}
      height={1080}
    />
  </>
);
