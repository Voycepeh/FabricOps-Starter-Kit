import {Easing, Img, interpolate, useCurrentFrame} from 'remotion';
import {mascotSrc} from '../mascotAssets';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';
import {VIDEO_TUNING} from '../videoTuning';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {text, timing, scenes} = VIDEO_CONFIG;
  const {opening} = VIDEO_TUNING;
  const fabricOpacity = interpolate(
    frame,
    [0, timing.openingFabricExitAt, timing.openingQuestionAt],
    [1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const questionOpacity = interpolate(frame, [timing.openingQuestionAt, timing.openingQuestionAt + timing.openingQuestionEnterFrames, timing.openingPushAt, scenes.opening], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const push = interpolate(frame, [timing.openingPushAt, scenes.opening], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const platformEntry = interpolate(
    frame,
    [timing.openingMascotAt, timing.openingMascotAt + opening.platformEntryFrames],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  return (
    <div style={{position: 'absolute', inset: 0, background: theme.background}}>
      <Img
        src={mascotSrc('dragging')}
        style={{
          position: 'absolute',
          left: opening.platformLeft,
          top: opening.platformTop,
          width: opening.platformWidth,
          height: 'auto',
          opacity: platformEntry,
          translate: `${(1 - platformEntry) * opening.platformEntryDistance - push * 2200}px 0`,
          zIndex: 1,
          scale: 0.833,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: opening.heroCenterY,
          display: 'flex',
          justifyContent: 'center',
          opacity: fabricOpacity,
          translate: '0 -50%',
          zIndex: 3,
        }}
      >
        <div
          style={{
            fontSize: text.fabricHero,
            lineHeight: 1,
            fontWeight: 840,
            letterSpacing: -5,
            textShadow: '0 20px 60px #000',
          }}
        >
          <span style={{color: '#fff'}}>Microsoft</span>{' '}
          <span style={{color: '#38d991'}}>Fabric</span>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: opening.heroCenterY,
          display: 'flex',
          justifyContent: 'center',
          opacity: questionOpacity,
          translate: '0 -50%',
          zIndex: 3,
        }}
      >
        <div
          style={{
            fontSize: text.fabricHero,
            lineHeight: 1,
            fontWeight: 840,
            letterSpacing: -7,
            textShadow: '0 24px 80px #000',
          }}
        >
          <span style={{color: '#fff'}}>Where do we </span>
          <span
            style={{
              background: 'linear-gradient(90deg, #ffffff 0%, #55c8ff 45%, #20b8ff 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            start?
          </span>
        </div>
      </div>
    </div>
  );
};
