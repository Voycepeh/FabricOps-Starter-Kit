import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const platform = spring({frame, fps, config: {damping: 20, stiffness: 65}});
  const {text, timing, scenes} = VIDEO_CONFIG;
  const artifactExit = interpolate(frame, [scenes.opening - 65, scenes.opening - 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const heroExit = interpolate(frame, [scenes.opening - 30, scenes.opening], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', left: 90, top: 55, width: 1740, height: 970, borderRadius: 76, background: 'linear-gradient(145deg, #122744dd, #0a1629ee)', border: '2px solid #668bb866', boxShadow: 'inset 0 1px #ffffff18, 0 50px 120px #0009', opacity: 1 - heroExit, transform: `scale(${0.94 + platform * 0.06 - heroExit * 0.04})`}} />
    {OPENING_ARTIFACTS.map((item, index) => {
      const enter = spring({frame: frame - 30 - index * timing.itemStagger, fps, config: {damping: 18, stiffness: 90}});
      const angle = Math.atan2(item.y - 465, item.x - 870);
      return <div key={item.label} style={{position: 'absolute', left: item.x, top: item.y, opacity: enter * (1 - artifactExit), transform: `translate(${Math.cos(angle) * artifactExit * 95}px, ${Math.sin(angle) * artifactExit * 95 + (1 - enter) * 38}px) scale(${0.8 + enter * 0.2 - artifactExit * 0.08})`}}><Artifact icon={item.icon} label={item.label} /></div>;
    })}
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: 1 - heroExit, transform: `scale(${0.9 + platform * 0.1 - heroExit * 0.05})`}}>
      <div style={{fontSize: text.fabricHero, lineHeight: 0.92, fontWeight: 840, letterSpacing: -7, textAlign: 'center', color: '#fff', textShadow: '0 24px 80px #000'}}>Microsoft<br />Fabric</div>
    </div>
  </div>;
};
