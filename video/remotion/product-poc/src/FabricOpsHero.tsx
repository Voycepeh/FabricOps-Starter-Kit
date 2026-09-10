import type {ReactNode} from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {CTA} from './scenes/CTA';
import {CodeWorkflow} from './scenes/CodeWorkflow';
import {FabricOpsReveal} from './scenes/FabricOpsReveal';
import {NotebookWorkflow} from './scenes/NotebookWorkflow';
import {OpeningPlatform} from './scenes/OpeningPlatform';
import {QuestionScene} from './scenes/QuestionScene';
import {font, theme} from './theme';

const Scene = ({from, duration, children}: {from: number; duration: number; children: ReactNode}) => (
  <Sequence from={from} durationInFrames={duration} premountFor={30}>
    <AbsoluteFill>{children}</AbsoluteFill>
  </Sequence>
);

export const FabricOpsHero = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}} />
    <Scene from={0} duration={330}><OpeningPlatform /></Scene>
    <Scene from={270} duration={240}><QuestionScene /></Scene>
    <Scene from={465} duration={255}><FabricOpsReveal /></Scene>
    <Scene from={675} duration={420}><NotebookWorkflow /></Scene>
    <Scene from={1050} duration={510}><CodeWorkflow /></Scene>
    <Scene from={1515} duration={285}><CTA /></Scene>
  </AbsoluteFill>
);
