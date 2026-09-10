import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {text, timing, scenes} = VIDEO_CONFIG;
  const hero = spring({frame, fps, config: {damping: 20, stiffness: 68}});
  const heroExit = interpolate(frame, [190, timing.openingQuestionAt], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const push = interpolate(frame, [190, 245], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const finalExit = interpolate(frame, [260, scenes.opening], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const question = spring({frame: frame - timing.openingQuestionAt, fps, config: {damping: 19, stiffness: 78}});
  return <div style={{position: 'absolute', inset: 0}}>
    {OPENING_ARTIFACTS.map((item, index) => {
      const delay = timing.openingHeroHold + index * timing.itemStagger + Math.floor(index / 6) * timing.openingWavePause;
      const enter = spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 92}});
      const angle = Math.atan2(item.y - 456, item.x - 850);
      return <div key={`${item.label}-${index}`} style={{position: 'absolute', left: item.x, top: item.y, opacity: enter * finalExit, transform: `translate(${Math.cos(angle) * push * 85}px, ${Math.sin(angle) * push * 70 + (1 - enter) * 42}px) scale(${0.72 + enter * 0.28 - push * 0.08})`}}><Artifact icon={item.icon} label={item.label} /></div>;
    })}
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: hero * heroExit, transform: `scale(${0.9 + hero * 0.1 - (1 - heroExit) * 0.08})`}}>
      <div style={{fontSize: text.fabricHero, lineHeight: 1, fontWeight: 840, letterSpacing: -7, textShadow: '0 24px 80px #000'}}><span style={{color: '#fff'}}>Microsoft</span> <span style={{color: '#38d991'}}>Fabric</span></div>
    </div>
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: question * finalExit, transform: `scale(${0.9 + question * 0.1})`}}><div style={{fontSize: 126, fontWeight: 840, letterSpacing: -5, color: '#fff', textShadow: '0 20px 60px #000'}}>Where do I start?</div></div>
  </div>;
};
