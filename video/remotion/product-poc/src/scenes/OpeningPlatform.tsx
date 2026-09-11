import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';

const OPENING_CENTER = {x: 960, y: 540} as const;
const PUSH_DISTANCE = 1500;

const ICON_POPULATION_START_SECONDS = 4;
const ICON_ENTRY_FRAMES = 14;
// Deliberately grouped rather than sequential: all 18 cards land by eight seconds.
const burstOffsets = [0, 0, 3, 3, 18, 18, 37, 37, 40, 61, 61, 64, 82, 82, 85, 101, 101, 105] as const;
const entryVectors = [
  {x: -145, y: -65},
  {x: 105, y: -125},
  {x: 15, y: -150},
  {x: -155, y: 55},
  {x: 150, y: 45},
  {x: 35, y: 145},
] as const;

const emphasisCues = [
  {label: 'Notebook', at: 8.7},
  {label: 'Data Pipeline', at: 9.55},
  {label: 'Lakehouse', at: 10.45},
  {label: 'Warehouse', at: 11.2},
  {label: 'Environment', at: 12.15},
] as const;

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
        const burstStart = Math.round(ICON_POPULATION_START_SECONDS * fps) + burstOffsets[index];
        const enter = interpolate(frame, [burstStart, burstStart + ICON_ENTRY_FRAMES], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.back(1.35)),
        });
        const cue = emphasisCues.find((entry) => entry.label === item.label);
        const cueFrame = cue ? cue.at * fps : -9999;
        const emphasis = cue
          ? interpolate(frame, [cueFrame - 2, cueFrame + 4, cueFrame + 10, cueFrame + 16], [0, 1, 1, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: Easing.inOut(Easing.cubic),
            })
          : 0;
        const vector = entryVectors[index % entryVectors.length];
        const cardCenterX = item.x + sizes.openingArtifactWidth / 2;
        const cardCenterY = item.y + sizes.openingArtifactHeight / 2;
        const deltaX = cardCenterX - OPENING_CENTER.x;
        const deltaY = cardCenterY - OPENING_CENTER.y;
        const magnitude = Math.max(1, Math.hypot(deltaX, deltaY));
        const pushX = (deltaX / magnitude) * PUSH_DISTANCE * push;
        const pushY = (deltaY / magnitude) * PUSH_DISTANCE * push;
        const entryX = vector.x * (1 - enter);
        const entryY = vector.y * (1 - enter);
        const scale = (0.78 + enter * 0.22) * (1 + emphasis * 0.16);

        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              position: 'absolute',
              left: item.x,
              top: item.y,
              opacity: enter,
              transform: `translate(${pushX + entryX}px, ${pushY + entryY}px) scale(${scale})`,
              zIndex: emphasis > 0 ? 4 : 1,
              filter: emphasis > 0 ? `drop-shadow(0 0 ${18 + emphasis * 18}px #35bdf0aa)` : 'none',
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
