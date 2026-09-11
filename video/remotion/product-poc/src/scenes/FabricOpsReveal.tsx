import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {SCENE_STARTS, VIDEO_CONFIG} from '../videoConfig';

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

const floatingWords = [
  {text: 'Python', at: 31.5, left: 210, top: 660, rotate: -5},
  {text: 'Notebook', at: 32.5, left: 1320, top: 245, rotate: 4},
  {text: 'PySpark', at: 33.5, left: 245, top: 255, rotate: 5},
  {text: 'Lakehouse', at: 35, left: 1285, top: 690, rotate: -4},
] as const;

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {timing} = VIDEO_CONFIG;

  const brand = spring({frame, fps, config: {damping: 18, stiffness: 72}});
  const whyEnter = spring({frame: frame - timing.fabricOpsWhyAt, fps, config: {damping: 18, stiffness: 88}});
  const whyExit = interpolate(frame, [timing.fabricOpsWhyExitAt - 20, timing.fabricOpsWhyExitAt], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const howEnter = spring({frame: frame - timing.fabricOpsHowAt, fps, config: {damping: 18, stiffness: 88}});
  const worksEnter = spring({frame: frame - timing.fabricOpsWorksAt, fps, config: {damping: 14, stiffness: 105}});
  const exit = interpolate(
    frame,
    [VIDEO_CONFIG.scenes.fabricOps - timing.sceneExit, VIDEO_CONFIG.scenes.fabricOps],
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
      {floatingWords.map((word) => {
        const start = Math.round(word.at * fps - SCENE_STARTS.fabricOps);
        const opacity = interpolate(frame, [start, start + 5, start + 24, start + 30], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        });
        const scale = interpolate(frame, [start, start + 7, start + 30], [0.82, 1.08, 0.96], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });

        return (
          <div
            key={word.text}
            style={{
              position: 'absolute',
              left: word.left,
              top: word.top,
              fontSize: 52,
              lineHeight: 1,
              fontWeight: 760,
              letterSpacing: -1.2,
              color: '#dcecff',
              opacity,
              transform: `rotate(${word.rotate}deg) scale(${scale})`,
              textShadow: '0 10px 34px #000b, 0 0 28px #279ee055',
            }}
          >
            {word.text}
          </div>
        );
      })}

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
