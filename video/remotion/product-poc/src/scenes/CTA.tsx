import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

const Action = ({label, focus}: {label: string; focus: number}) => <div style={{padding: '20px 34px', borderRadius: 999, border: `2px solid ${focus > 0.4 ? theme.production : '#71839d'}`, background: focus > 0.4 ? `${theme.production}1f` : '#101c2d', color: focus > 0.4 ? '#fff' : '#c3cfdd', fontSize: 28, fontWeight: 700, boxShadow: focus > 0.4 ? `0 0 42px ${theme.production}44` : 'none', transform: `scale(${1 + focus * 0.06})`}}>{label}&nbsp; →</div>;

export const CTA = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 76}});
  const how = interpolate(frame, [70, 105, 135, 165], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const demo = interpolate(frame, [160, 200], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', background: '#07101ff8', opacity: enter, transform: `scale(${0.97 + enter * 0.03})`}}>
    <div style={{fontSize: 148, fontWeight: 830, letterSpacing: -8}}><span style={{color: '#fff'}}>Fabric</span><span style={{color: theme.production}}>Ops</span></div>
    <div style={{marginTop: 20, fontSize: 32, color: '#c8d5e5', letterSpacing: 0.2}}>Lightweight. Self-contained. Built for Microsoft Fabric.</div>
    <div style={{display: 'flex', gap: 30, marginTop: 75}}><Action label="How FabricOps works" focus={how} /><Action label="Guided Demo" focus={demo} /></div>
  </div>;
};
