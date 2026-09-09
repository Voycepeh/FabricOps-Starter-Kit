import React from 'react';
import {Composition} from 'remotion';
import {FabricOpsHero} from './FabricOpsHero';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FabricOpsHero"
      component={FabricOpsHero}
      durationInFrames={750}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
