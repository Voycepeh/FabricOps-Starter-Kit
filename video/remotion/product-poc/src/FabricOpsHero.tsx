import type {ReactNode} from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {CTA} from './scenes/CTA';
import {FabricOpsReveal} from './scenes/FabricOpsReveal';
import {LifecycleScene} from './scenes/LifecycleScene';
import {OpeningPlatform} from './scenes/OpeningPlatform';
import {OutcomeScene} from './scenes/OutcomeScene';
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
    <Scene from={0} duration={270}><OpeningPlatform /></Scene>
    <Scene from={240} duration={180}><QuestionScene /></Scene>
    <Scene from={390} duration={210}><FabricOpsReveal /></Scene>
    <Scene from={570} duration={540}><LifecycleScene /></Scene>
    <Scene from={1080} duration={240}><OutcomeScene /></Scene>
    <Scene from={1290} duration={210}><CTA /></Scene>
  </AbsoluteFill>
);
