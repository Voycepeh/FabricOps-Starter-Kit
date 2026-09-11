import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sizes, text, timing} = VIDEO_CONFIG;
  const hero = spring({frame, fps, config: {damping: 20, stiffness: 68}});
  const heroExit = interpolate(frame, [145, timing.openingQuestionAt], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const push = interpolate(frame, [224, 284], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const finalExit = interpolate(push, [0.88, 1], [1, 0], {
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
        const offsetX = cardCenterX - 960;
        const offsetY = cardCenterY - 540;
        const distance = Math.hypot(offsetX, offsetY);
        const pushX = (offsetX / distance) * push * 720;
        const pushY = (offsetY / distance) * push * 720;

        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              position: 'absolute',
              left: item.x,
              top: item.y,
              opacity: enter * finalExit,
              transform: `translate(${pushX}px, ${pushY + (1 - enter) * 42}px) scale(${0.72 + enter * 0.28})`,
            }}
          >
            <Artifact icon={item.icon} label={item.label} scale={item.scale} />
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
          opacity: question * interpolate(push, [0.15, 0.7], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          transform: `translateY(${-push * 110}px) scale(${0.9 + question * 0.1 + push * 0.04})`,
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
