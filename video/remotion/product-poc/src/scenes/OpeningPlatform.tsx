import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, FABRIC_ICON, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const platform = spring({frame, fps, config: {damping: 20, stiffness: 65}});
  const {sizes, text, timing, scenes} = VIDEO_CONFIG;
  const exit = interpolate(frame, [scenes.opening - 40, scenes.opening], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', left: 90, top: 55, width: 1740, height: 970, borderRadius: 76, background: 'linear-gradient(145deg, #122744dd, #0a1629ee)', border: '2px solid #668bb866', boxShadow: 'inset 0 1px #ffffff18, 0 50px 120px #0009', opacity: 1 - exit, transform: `scale(${0.94 + platform * 0.06 - exit * 0.04})`}} />
    {OPENING_ARTIFACTS.map((item, index) => {
      const enter = spring({frame: frame - 30 - index * timing.itemStagger, fps, config: {damping: 18, stiffness: 90}});
      const angle = Math.atan2(item.y - 465, item.x - 870);
      return <div key={item.label} style={{position: 'absolute', left: item.x, top: item.y, opacity: enter * (1 - exit), transform: `translate(${Math.cos(angle) * exit * 95}px, ${Math.sin(angle) * exit * 95 + (1 - enter) * 38}px) scale(${0.8 + enter * 0.2 - exit * 0.08})`}}><Artifact icon={item.icon} label={item.label} /></div>;
    })}
    <div style={{position: 'absolute', left: (1920 - sizes.fabricHeroCardWidth) / 2, top: (1080 - sizes.fabricHeroCardHeight) / 2, width: sizes.fabricHeroCardWidth, height: sizes.fabricHeroCardHeight, borderRadius: 78, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 30, background: '#0d1b30', border: '3px solid #8eb9e499', boxShadow: '0 35px 110px #000c, inset 0 1px #fff1', opacity: 1 - exit, transform: `scale(${0.88 + platform * 0.12 - exit * 0.06})`}}>
      <FABRIC_ICON width={sizes.fabricHeroIcon} height={sizes.fabricHeroIcon} aria-hidden="true" />
      <div style={{fontSize: text.fabricLabel, fontWeight: 820}}>Microsoft Fabric</div>
    </div>
  </div>;
};
