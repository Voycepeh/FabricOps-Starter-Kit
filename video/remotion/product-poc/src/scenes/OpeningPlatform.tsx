import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

const OPENING_CENTER = {x: 960, y: 540} as const;
const PUSH_DISTANCE = 1500;

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sizes, text, timing, scenes} = VIDEO_CONFIG;
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

  return (
    <div style={{position: 'absolute', inset: 0}}>
      {OPENING_ARTIFACTS.map((item, index) => {
        const delay =
          timing.openingHeroHold +
          index * timing.itemStagger +
          Math.floor(index / 6) * timing.openingWavePause;
        const enter = spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 92}});
        const cardCenterX = item.x + sizes.openingArtifactWidth / 2;
        const cardCenterY = item.y + sizes.openingArtifactHeight / 2;
        const deltaX = cardCenterX - OPENING_CENTER.x;
        const deltaY = cardCenterY - OPENING_CENTER.y;
        const magnitude = Math.max(1, Math.hypot(deltaX, deltaY));
        const pushX = (deltaX / magnitude) * PUSH_DISTANCE * push;
        const pushY = (deltaY / magnitude) * PUSH_DISTANCE * push;

        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              position: 'absolute',
              left: item.x,
              top: item.y,
              opacity: enter,
              transform: `translate(${pushX}px, ${pushY + (1 - enter) * 42}px) scale(${0.72 + enter * 0.28})`,
            }}
          >
            <Artifact icon={item.icon} label={item.label} iconScale={item.iconScale} />
          </div>
        );
      })}

      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'grid',
          placeItems: 'center',
          opacity: hero * heroExit,
          transform: `scale(${0.9 + hero * 0.1 - (1 - heroExit) * 0.08})`,
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
          transform: `translateY(${-760 * push}px) scale(${0.9 + question * 0.1})`,
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
          <span style={{color: '#fff'}}>Where do I </span>
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
