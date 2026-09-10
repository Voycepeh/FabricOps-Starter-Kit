import type {ReactNode} from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {CTA} from './scenes/CTA';
import {FabricOpsReveal} from './scenes/FabricOpsReveal';
import {NotebookJourney} from './scenes/NotebookJourney';
import {OpeningPlatform} from './scenes/OpeningPlatform';
import {font, theme} from './theme';
import {SCENE_STARTS, VIDEO_CONFIG} from './videoConfig';

const Scene = ({from, duration, children}: {from: number; duration: number; children: ReactNode}) => (
  <Sequence from={from} durationInFrames={duration} premountFor={30}>
    <AbsoluteFill>{children}</AbsoluteFill>
  </Sequence>
);

export const FabricOpsHero = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}} />
    <Scene from={SCENE_STARTS.opening} duration={VIDEO_CONFIG.scenes.opening}><OpeningPlatform /></Scene>
    <Scene from={SCENE_STARTS.fabricOps} duration={VIDEO_CONFIG.scenes.fabricOps}><FabricOpsReveal /></Scene>
    <Scene from={SCENE_STARTS.notebooks} duration={VIDEO_CONFIG.scenes.notebooks}><NotebookJourney /></Scene>
    <Scene from={SCENE_STARTS.cta} duration={VIDEO_CONFIG.scenes.cta}><CTA /></Scene>
  </AbsoluteFill>
);
