import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const Brand = () => <div style={{fontSize: VIDEO_CONFIG.text.hero, lineHeight: 1, fontWeight: 840, letterSpacing: -8, whiteSpace: 'nowrap'}}><span style={{color: theme.production}}>Fabric</span><span style={{color: '#fff'}}>Ops</span></div>;

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const brand = spring({frame, fps, config: {damping: 18, stiffness: 72}});
  const how = spring({frame: frame - 65, fps, config: {damping: 18, stiffness: 88}});
  const works = spring({frame: frame - 92, fps, config: {damping: 14, stiffness: 105}});
  const exit = interpolate(frame, [VIDEO_CONFIG.scenes.fabricOps - 35, VIDEO_CONFIG.scenes.fabricOps], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: exit}}>
    <div style={{width: 920, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: brand, transform: `translateX(${(1 - brand) * -180}px) scale(${0.86 + brand * 0.14})`}}>
      <div style={{alignSelf: 'flex-start', marginLeft: 65, fontSize: VIDEO_CONFIG.text.title, fontWeight: 820, color: '#fff', opacity: how, transform: `translateY(${(1 - how) * -90}px)`}}>How</div>
      <Brand />
      <div style={{alignSelf: 'flex-end', marginRight: 75, fontSize: VIDEO_CONFIG.text.title, fontWeight: 820, color: '#fff', opacity: works, transform: `translateY(${(1 - works) * 80}px)`}}>works</div>
    </div>
  </div>;
};
