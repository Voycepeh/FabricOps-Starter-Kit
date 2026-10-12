import {Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc} from '../mascotAssets';
import {VIDEO_CONFIG} from '../videoConfig';
import {VIDEO_TUNING, secondsToFrames} from '../videoTuning';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {text, timing, scenes} = VIDEO_CONFIG;
  const {opening} = VIDEO_TUNING;
  const hero = spring({frame, fps, config: {damping: 20, stiffness: 68}});
  const heroExit = interpolate(frame, [timing.openingQuestionAt - 36, timing.openingQuestionAt], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const push = interpolate(frame, [timing.openingPushAt, scenes.opening], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const question = spring({
    frame: frame - timing.openingQuestionAt,
    fps,
    config: {damping: 19, stiffness: 78},
  });
  const platformEntryStart = secondsToFrames(opening.platformEntryStartSeconds, fps);
  const platformEntry = interpolate(
    frame,
    [platformEntryStart, platformEntryStart + opening.platformEntryFrames],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  return (
    <div style={{position: 'absolute', inset: 0}}>
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
          opacity: hero * heroExit,
          scale: 0.9 + hero * 0.1 - (1 - heroExit) * 0.08,
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
          <span style={{color: '#fff'}}>Microsoft</span>{' '}
          <span style={{color: '#38d991'}}>Fabric</span>
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'grid',
          placeItems: 'center',
          opacity: question,
          scale: 0.9 + question * 0.1,
          translate: `0 ${opening.questionOffsetY - 760 * push}px`,
          zIndex: 2,
        }}
      >
        <div
          style={{
            fontSize: 126,
            lineHeight: 1,
            fontWeight: 840,
            letterSpacing: -5,
            textShadow: '0 20px 60px #000',
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
