import {Composition, Folder} from 'remotion';
import {FabricOpsFullVideo} from './compositions/FabricOpsFullVideo';
import {WorkspaceArchitecture} from './scenes/WorkspaceArchitecture';
import {FULL_VIDEO_DURATION, VIDEO_FPS, WORKSPACE_ARCHITECTURE_DURATION_SECONDS} from './videoConfig';

export const Root = () => (
  <>
    <Folder name="Scenes">
      <Composition
        id="WorkspaceArchitecture"
        component={WorkspaceArchitecture}
        durationInFrames={WORKSPACE_ARCHITECTURE_DURATION_SECONDS * VIDEO_FPS}
        fps={VIDEO_FPS}
        width={1920}
        height={1080}
      />
    </Folder>
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
