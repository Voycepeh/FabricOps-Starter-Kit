import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 78}});
  const subtitle = interpolate(frame, [35, 60], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const works = interpolate(frame, [68, 95], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const exit = interpolate(frame, [120, 150], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: '#07101ff5', opacity: exit}}>
    <div style={{display: 'flex', alignItems: 'center', flexDirection: 'column', transform: `scale(${0.92 + enter * 0.08})`, opacity: enter}}>
      <div style={{fontSize: 156, lineHeight: 1, fontWeight: 830, letterSpacing: -8}}><span style={{color: '#fff'}}>Fabric</span><span style={{color: theme.production}}>Ops</span></div>
      <div style={{marginTop: 32, fontSize: 46, fontWeight: 650, color: '#dce7f5', opacity: subtitle, transform: `translateY(${(1 - subtitle) * 16}px)`}}>Fabric Operations</div>
      <div style={{marginTop: 68, fontSize: 64, fontWeight: 780, color: '#fff', opacity: works, transform: `translateY(${(1 - works) * 18}px)`}}>How FabricOps works</div>
    </div>
  </div>;
};
