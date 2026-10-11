import {Composition, Folder} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';
import {FabricOpsPart1Motion} from './motion-experiment/MotionExperiment';
import timeline from './motion-experiment/timeline.json';
import {VIDEO_DURATION} from './videoConfig';

export const Root = () => {
  const durationInFrames = Math.round(timeline.durationSeconds * timeline.fps);

  return (
    <>
      <Composition
        id="FabricOpsHero"
        component={FabricOpsHero}
        durationInFrames={VIDEO_DURATION}
        fps={30}
        width={1920}
        height={1080}
      />
      <Folder name="Motion-Experiment">
        <Composition
          id="FabricOpsPart1Motion"
          component={FabricOpsPart1Motion}
          durationInFrames={durationInFrames}
          fps={30}
          width={1920}
          height={1080}
        />
      </Folder>
    </>
  );
};
