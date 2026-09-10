import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const Brand = ({operations = false}: {operations?: boolean}) => <div style={{fontSize: VIDEO_CONFIG.text.hero, lineHeight: 1, fontWeight: 840, letterSpacing: -8, whiteSpace: 'nowrap'}}><span style={{color: theme.production}}>Fabric</span><span style={{color: '#fff'}}>{operations ? ' Operations' : 'Ops'}</span></div>;

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes} = VIDEO_CONFIG;
  const brandIn = spring({frame, fps, config: {damping: 20, stiffness: 78}});
  const expand = interpolate(frame, [42, 82], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const resolve = interpolate(frame, [105, 140], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const lockup = spring({frame: frame - 145, fps, config: {damping: 18, stiffness: 82}});
  const how = spring({frame: frame - 152, fps, config: {damping: 17, stiffness: 105}});
  const works = spring({frame: frame - 165, fps, config: {damping: 14, stiffness: 115}});
  const exit = interpolate(frame, [scenes.fabricOps - 35, scenes.fabricOps], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const transitionOpacity = 1 - interpolate(frame, [135, 158], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: exit}}>
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: brandIn * transitionOpacity, transform: `scale(${0.9 + brandIn * 0.1 - expand * 0.04 + resolve * 0.04})`}}>
      <div style={{position: 'relative', width: 1500, height: 190}}>
        <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: 1 - expand + resolve}}><Brand /></div>
        <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: expand * (1 - resolve)}}><Brand operations /></div>
      </div>
    </div>
    <div style={{width: 920, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: lockup, transform: `scale(${0.9 + lockup * 0.1})`}}>
      <div style={{alignSelf: 'flex-start', marginLeft: 65, fontSize: VIDEO_CONFIG.text.title, fontWeight: 820, color: '#fff', opacity: how, transform: `translateY(${(1 - how) * -80}px)`}}>How</div>
      <Brand />
      <div style={{alignSelf: 'flex-end', marginRight: 75, fontSize: VIDEO_CONFIG.text.title, fontWeight: 820, color: '#fff', opacity: works, transform: `translateY(${(1 - works) * 70}px)`}}>works</div>
    </div>
  </div>;
};
