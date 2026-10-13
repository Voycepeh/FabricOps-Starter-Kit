import {Easing, Img, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc} from '../mascotAssets';
import {NARRATION_CUE_SHEET} from '../narrationCues';
import {VIDEO_CONFIG} from '../videoConfig';
import {VIDEO_TUNING} from '../videoTuning';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {text, timing, scenes} = VIDEO_CONFIG;
  const {opening} = VIDEO_TUNING;
  const cue = NARRATION_CUE_SHEET.opening;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const featureListAt = localCue(1);
  const questionAt = localCue(2);
  const fabricOpacity = interpolate(
    frame,
    [0, questionAt - Math.round(0.35 * fps), questionAt],
    [1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const questionOpacity = interpolate(frame, [questionAt, questionAt + timing.openingQuestionEnterFrames, timing.openingPushAt, scenes.opening], [0, 1, 1, 0], {
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
    [featureListAt, featureListAt + opening.platformEntryFrames],
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
          scale: 0.977,
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
