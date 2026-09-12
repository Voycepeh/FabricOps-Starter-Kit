import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Artifact, OPENING_ARTIFACTS} from '../components/FabricIcons';
import {VIDEO_CONFIG} from '../videoConfig';
import {VIDEO_TUNING, secondsToFrames} from '../videoTuning';

const OPENING_CENTER = {x: 960, y: 540} as const;
const PUSH_DISTANCE = 1500;

const OPENING_POSITION_KEYS = [
  'Notebook',
  'Lakehouse',
  'Warehouse',
  'Environment',
  'Data Pipeline',
  'Dataflow Gen2',
  'Data Engineering',
  'Data Science',
  'SQL Database',
  'Eventstream',
  'Eventhouse',
  'Semantic Model',
  'Report',
  'Dashboard',
  'Mirrored Database',
  'ML Model',
  'OneLake',
  'Graph Intelligence',
] as const;

const FEATURED_POSITION_KEYS = new Set([
  'Notebook',
  'Data Pipeline',
  'Lakehouse',
  'Warehouse',
  'Environment',
  'Eventstream',
] as const);

const entryVectors = [
  {x: -145, y: -65},
  {x: 105, y: -125},
  {x: 15, y: -150},
  {x: -155, y: 55},
  {x: 150, y: 45},
  {x: 35, y: 145},
] as const;

export const OpeningPlatform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sizes, text, timing, scenes} = VIDEO_CONFIG;
  const {opening} = VIDEO_TUNING;
  const hero = spring({frame, fps, config: {damping: 20, stiffness: 68}});
  const heroExit = interpolate(frame, [timing.openingQuestionAt - 36, timing.openingQuestionAt], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const iconExit = interpolate(frame, [timing.openingQuestionAt - 18, timing.openingQuestionAt], [1, 0], {
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
        const positionKey = OPENING_POSITION_KEYS[index];
        const tunedPosition = positionKey ? opening.positions[positionKey] : {left: item.x, top: item.y};
        const burstStart = secondsToFrames(
          opening.iconPopulationStartSeconds + opening.iconBurstOffsetsSeconds[index],
          fps,
        );
        const enter = interpolate(frame, [burstStart, burstStart + opening.iconEntryFrames], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.back(1.15)),
        });
        const vector = entryVectors[index % entryVectors.length];
        const cardCenterX = tunedPosition.left + sizes.openingArtifactWidth / 2;
        const cardCenterY = tunedPosition.top + sizes.openingArtifactHeight / 2;
        const deltaX = cardCenterX - OPENING_CENTER.x;
        const deltaY = cardCenterY - OPENING_CENTER.y;
        const magnitude = Math.max(1, Math.hypot(deltaX, deltaY));
        const pushX = (deltaX / magnitude) * PUSH_DISTANCE * push;
        const pushY = (deltaY / magnitude) * PUSH_DISTANCE * push;
        const entryX = vector.x * (1 - enter);
        const entryY = vector.y * (1 - enter);
        const scale = 0.78 + enter * 0.22;

        const featuredKeys = OPENING_POSITION_KEYS.filter((key) => FEATURED_POSITION_KEYS.has(key));
        const featuredIndex = positionKey ? featuredKeys.indexOf(positionKey) : -1;
        const gleamWindowFrames = (opening.featuredGleam.end - opening.featuredGleam.start) * fps;
        const gleamStagger =
          (gleamWindowFrames - opening.featuredGleam.perIconDurationFrames) / Math.max(1, featuredKeys.length - 1);
        const gleamStart = opening.featuredGleam.start * fps + Math.max(featuredIndex, 0) * gleamStagger;
        const gleamProgress =
          featuredIndex >= 0
            ? interpolate(frame, [gleamStart, gleamStart + opening.featuredGleam.perIconDurationFrames], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
                easing: Easing.inOut(Easing.cubic),
              })
            : 0;

        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              position: 'absolute',
              left: tunedPosition.left,
              top: tunedPosition.top,
              opacity: enter * iconExit,
              transform: `translate(${pushX + entryX}px, ${pushY + entryY}px) scale(${scale})`,
              zIndex: 1,
            }}
          >
            <Artifact icon={item.icon} label={item.label} iconScale={item.iconScale} />
            {featuredIndex >= 0 ? (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: 30,
                  overflow: 'hidden',
                  pointerEvents: 'none',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    top: -55,
                    bottom: -55,
                    left: -95,
                    width: 62,
                    opacity: 0.34,
                    background: 'linear-gradient(90deg, transparent, #ffffffcc, transparent)',
                    filter: 'blur(5px)',
                    transform: `skewX(-18deg) translateX(${gleamProgress * 440}px)`,
                  }}
                />
              </div>
            ) : null}
          </div>
        );
      })}

      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: opening.heroCenterY,
          display: 'flex',
          justifyContent: 'center',
          opacity: hero * heroExit,
          transform: `translateY(-50%) scale(${0.9 + hero * 0.1 - (1 - heroExit) * 0.08})`,
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
