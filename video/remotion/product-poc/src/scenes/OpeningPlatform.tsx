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
    {OPENING_ARTIFACTS.map((item, index) => {
      const enter = spring({frame: frame - 30 - index * timing.itemStagger, fps, config: {damping: 18, stiffness: 90}});
      const angle = Math.atan2(item.y - 465, item.x - 870);
      const rotation = (index % 2 === 0 ? -1 : 1) * (1 - enter) * 3;
      return <div key={item.label} style={{position: 'absolute', left: item.x, top: item.y, opacity: enter * (1 - artifactExit), transform: `translate(${Math.cos(angle) * artifactExit * 95}px, ${Math.sin(angle) * artifactExit * 95 + (1 - enter) * 45}px) scale(${0.72 + enter * 0.28 - artifactExit * 0.08}) rotate(${rotation}deg)`}}><Artifact icon={item.icon} label={item.label} /></div>;
    })}
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: 1 - heroExit, transform: `scale(${0.9 + platform * 0.1 - heroExit * 0.05})`}}>
      <div style={{fontSize: text.fabricHero, lineHeight: 1, fontWeight: 840, letterSpacing: -7, textAlign: 'center', textShadow: '0 24px 80px #000'}}><span style={{color: '#fff'}}>Microsoft</span> <span style={{color: '#38d991'}}>Fabric</span></div>
    </div>
  </div>;
};
