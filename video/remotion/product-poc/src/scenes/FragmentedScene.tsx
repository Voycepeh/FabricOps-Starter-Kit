import type {ReactNode} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {DataContract, EnvironmentConfig, Notebook, Pipeline} from '../components/Primitives';
import {theme} from '../theme';

const Fragment = ({children, x, y, rotate, delay, scale = 1}: {children: ReactNode; x: number; y: number; rotate: number; delay: number; scale?: number}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig();
  const arrive = spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 85}});
  const organise = interpolate(frame, [118, 172], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', left: x, top: y, opacity: arrive, transform: `translateY(${(1-arrive)*80}px) rotate(${rotate*(1-organise)}deg) scale(${scale + organise * (1-scale)})`, filter: `blur(${(1-arrive)*8}px)`}}>{children}</div>;
};

export const FragmentedScene = () => {
  const frame = useCurrentFrame();
  const title = interpolate(frame, [55, 90, 135, 170], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const layer = interpolate(frame, [112, 168], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', inset: 0, transform: `scale(${interpolate(frame, [0, 180], [1.05, .93])}) translateY(${layer*120}px)`, opacity: 1-layer*.76}}>
      <Fragment x={185} y={165} rotate={-7} delay={0}><Notebook label="Notebook" /></Fragment>
      <Fragment x={1340} y={165} rotate={6} delay={9} scale={.9}><DataContract /></Fragment>
      <Fragment x={790} y={120} rotate={-3} delay={17}><EnvironmentConfig /></Fragment>
      <Fragment x={1280} y={650} rotate={-5} delay={25}><Pipeline /></Fragment>
      <Fragment x={300} y={650} rotate={7} delay={32}><div style={{width: 255, padding: 25, borderRadius: 18, background: '#132036', border: `1px solid ${theme.neutral}66`, color: theme.text, fontSize: 21}}>▦ &nbsp; Lakehouse table</div></Fragment>
      {[0,1,2,3].map(i => <div key={i} style={{position: 'absolute', left: 520+i*245, top: 480+(i%2)*85, width: 155, height: 2, background: '#52627a55', transform: `rotate(${i%2 ? -13 : 17}deg) scaleX(${1-layer})`, transformOrigin: 'left'}} />)}
    </div>
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: title, transform: `translateY(${interpolate(title,[0,1],[24,0])}px)`}}>
      <div style={{fontSize: 110, fontWeight: 760, letterSpacing: -6, color: theme.text}}>Fabric<span style={{color: theme.production}}>Ops</span></div>
      <div style={{display: 'flex', gap: 19, marginTop: 24, fontSize: 27, color: theme.muted}}><span>Microsoft Fabric gives the platform.</span><span style={{color: '#52627a'}}>—</span><b style={{color: theme.text}}>FabricOps gives the operating practice.</b></div>
    </div>
    <div style={{position: 'absolute', left: 110, right: 110, top: 98, bottom: 98, border: `1px solid ${theme.production}`, borderRadius: 55, opacity: layer*.55, boxShadow: `inset 0 0 90px ${theme.production}10, 0 0 70px ${theme.production}12`, transform: `scale(${.95+layer*.05})`}} />
  </div>;
};
