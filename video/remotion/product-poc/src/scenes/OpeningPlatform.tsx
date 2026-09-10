import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, FABRIC_ICON, OPENING_ARTIFACTS} from '../components/FabricIcons';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const platform = spring({frame, fps, config: {damping: 20, stiffness: 65}});
  const exit = interpolate(frame, [270, 330], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, opacity: exit, transform: `scale(${1 - frame * 0.00009})`}}>
    <div style={{position: 'absolute', left: 105, top: 70, width: 1710, height: 900, borderRadius: 76, background: 'linear-gradient(145deg, #122744dd, #0a1629ee)', border: '2px solid #668bb866', boxShadow: 'inset 0 1px #ffffff18, 0 50px 120px #0009', transform: `scale(${0.94 + platform * 0.06})`}} />
    {OPENING_ARTIFACTS.map((item, index) => {
      const enter = spring({frame: frame - 16 - index * 8, fps, config: {damping: 18, stiffness: 90}});
      return <div key={`${item.label}-${index}`} style={{position: 'absolute', left: item.x, top: item.y, opacity: enter, transform: `translateY(${(1 - enter) * 38}px) scale(${0.8 + enter * 0.2})`}}><Artifact icon={item.icon} label={item.label} /></div>;
    })}
    <div style={{position: 'absolute', left: 790, top: 365, width: 340, height: 300, borderRadius: 55, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 18, background: '#0d1b30', border: '2px solid #7da7d477', boxShadow: '0 25px 80px #000b'}}>
      <FABRIC_ICON width={150} height={150} aria-hidden="true" />
      <div style={{fontSize: 38, fontWeight: 780}}>Microsoft Fabric</div>
    </div>
  </div>;
};
