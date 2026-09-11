import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const Brand = () => (
  <div
    style={{
      fontSize: VIDEO_CONFIG.text.hero,
      lineHeight: 1,
      fontWeight: 840,
      letterSpacing: -8,
      whiteSpace: 'nowrap',
    }}
  >
    <span style={{color: theme.production}}>Fabric</span>
    <span style={{color: '#fff'}}>Ops</span>
  </div>
);

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const brand = spring({frame, fps, config: {damping: 18, stiffness: 72}});
  const whyEnter = spring({frame: frame - 36, fps, config: {damping: 18, stiffness: 88}});
  const whyExit = interpolate(frame, [112, 158], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const howEnter = spring({frame: frame - 166, fps, config: {damping: 18, stiffness: 88}});
  const worksEnter = spring({frame: frame - 192, fps, config: {damping: 14, stiffness: 105}});
  const exit = interpolate(
    frame,
    [VIDEO_CONFIG.scenes.fabricOps - 35, VIDEO_CONFIG.scenes.fabricOps],
    [1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    }
  );

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'grid',
        placeItems: 'center',
        opacity: exit,
      }}
    >
      <div
        style={{
          position: 'relative',
          width: 1040,
          height: 430,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: brand,
          transform: `translateX(${(1 - brand) * -180}px) scale(${0.86 + brand * 0.14})`,
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: 65,
            top: 36,
            fontSize: VIDEO_CONFIG.text.title,
            fontWeight: 820,
            color: '#fff',
            opacity: whyEnter,
            transform: `translate(${(1 - whyEnter) * -100 - whyExit * 980}px, ${(1 - whyEnter) * -40}px)`,
          }}
        >
          Why
        </div>

        <div
          style={{
            position: 'absolute',
            right: 78,
            bottom: 34,
            fontSize: VIDEO_CONFIG.text.title,
            fontWeight: 820,
            color: '#fff',
            opacity: whyEnter,
            transform: `translate(${(1 - whyEnter) * 100 + whyExit * 980}px, ${(1 - whyEnter) * 40}px)`,
          }}
        >
          ?
        </div>

        <Brand />

        <div
          style={{
            position: 'absolute',
            left: 65,
            top: 36,
            fontSize: VIDEO_CONFIG.text.title,
            fontWeight: 820,
            color: '#fff',
            opacity: howEnter,
            transform: `translate(${(1 - howEnter) * -110}px, ${(1 - howEnter) * -45}px)`,
          }}
        >
          How
        </div>

        <div
          style={{
            position: 'absolute',
            right: 75,
            bottom: 34,
            fontSize: VIDEO_CONFIG.text.title,
            fontWeight: 820,
            color: '#fff',
            opacity: worksEnter,
            transform: `translate(${(1 - worksEnter) * 110}px, ${(1 - worksEnter) * 45}px)`,
          }}
        >
          works?
        </div>
      </div>
    </div>
  );
};
