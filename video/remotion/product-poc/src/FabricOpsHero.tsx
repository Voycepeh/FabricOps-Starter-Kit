import type {ReactNode} from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {CTA} from './scenes/CTA';
import {FabricOpsReveal} from './scenes/FabricOpsReveal';
import {LifecycleScene} from './scenes/LifecycleScene';
import {GovernanceFocus, NotebookStructure, PipelineSplit} from './scenes/NotebookJourney';
import {OpeningPlatform} from './scenes/OpeningPlatform';
import {font, theme} from './theme';

const Scene = ({from, duration, children}: {from: number; duration: number; children: ReactNode}) => (
  <Sequence from={from} durationInFrames={duration} premountFor={30}>
    <AbsoluteFill>{children}</AbsoluteFill>
  </Sequence>
);

export const FabricOpsHero = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}} />
    <Scene from={0} duration={240}><OpeningPlatform /></Scene>
    <Scene from={270} duration={150}><FabricOpsReveal /></Scene>
    <Scene from={450} duration={150}><NotebookStructure /></Scene>
    <Scene from={630} duration={150}><GovernanceFocus /></Scene>
    <Scene from={810} duration={210}><PipelineSplit /></Scene>
    <Scene from={1050} duration={510}><LifecycleScene /></Scene>
    <Scene from={1590} duration={180}><CTA /></Scene>
  </AbsoluteFill>
);
