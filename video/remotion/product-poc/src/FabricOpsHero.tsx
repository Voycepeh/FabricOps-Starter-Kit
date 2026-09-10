import type {ReactNode} from 'react';
import {AbsoluteFill, Easing, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {FinishScene} from './scenes/FinishScene';
import {FortsScene} from './scenes/FortsScene';
import {WallPathScene} from './scenes/WallPathScene';
import {font, theme} from './theme';

const Scene = ({from, duration, fadeIn = 24, fadeOut = 28, children}: {from: number; duration: number; fadeIn?: number; fadeOut?: number; children: ReactNode}) => {
  const frame = useCurrentFrame();
  const local = frame - from;
  const opacity = interpolate(local, [0, fadeIn, duration-fadeOut, duration], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <Sequence from={from} durationInFrames={duration}><AbsoluteFill style={{opacity}}>{children}</AbsoluteFill></Sequence>;
};

export const FabricOpsHero = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: theme.background, fontFamily: font, overflow: 'hidden'}}>
    <div style={{position: 'absolute', inset: -200, background: `radial-gradient(circle at ${42+interpolate(frame,[0,900],[0,15])}% 40%, #15325a88 0, transparent 35%), radial-gradient(circle at 65% 72%, #4a237140 0, transparent 32%), linear-gradient(145deg,#07101f,#091427 60%,#07111d)`}} />
    <div style={{position: 'absolute', inset: 0, opacity: .12, backgroundImage: 'linear-gradient(#91a7c30c 1px,transparent 1px),linear-gradient(90deg,#91a7c30c 1px,transparent 1px)', backgroundSize: '64px 64px', transform: `translate(${frame%64}px,${frame%64}px)`}} />
    <Scene from={0} duration={475} fadeIn={12} fadeOut={45}><WallPathScene /></Scene>
    <Scene from={425} duration={340} fadeIn={45} fadeOut={45}><FortsScene /></Scene>
    <Scene from={720} duration={180} fadeIn={45} fadeOut={1}><FinishScene /></Scene>
    <div style={{position: 'absolute', left: 52, bottom: 38, color: '#607089', fontSize: 15, letterSpacing: 2}}>FABRICOPS STARTER KIT</div>
  </AbsoluteFill>;
};
