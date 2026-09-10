import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 78}});
  const resolve = interpolate(frame, [85, 145], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const exit = interpolate(frame, [215, 255], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: '#07101ff5', opacity: exit}}>
    <div style={{position: 'relative', height: 160, width: 1300, transform: `scale(${0.92 + enter * 0.08})`, opacity: enter}}>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 116, fontWeight: 800, letterSpacing: -5, opacity: 1 - resolve, transform: `scaleX(${1 - resolve * 0.12})`}}>Fabric&nbsp;<span style={{color: theme.production}}>Operations</span></div>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 150, fontWeight: 820, letterSpacing: -7, opacity: resolve, transform: `scale(${0.92 + resolve * 0.08})`}}><span style={{color: '#fff'}}>Fabric</span><span style={{color: theme.production}}>Ops</span></div>
    </div>
  </div>;
};
