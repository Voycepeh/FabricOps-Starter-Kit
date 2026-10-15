import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {DataEngineeringIcon, DataGovernanceIcon} from '../components/TeamIdentityIcons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';
import {fabricOpsFrame, VIDEO_TUNING} from '../videoTuning';

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

const FLOATING_WORD_LABELS = {
  operations: 'Operations',
  plugAndPlay: 'Plug and play',
  selfContained: 'Self-contained',
  python: 'Python',
  notebook: 'Notebook',
  pyspark: 'PySpark',
  lakehouse: 'Lakehouse',
} as const;

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {timing} = VIDEO_CONFIG;
  const {floatingWords, relationship, prompts} = VIDEO_TUNING.fabricOps;

  const brand = spring({frame, fps, config: {damping: 18, stiffness: 72}});
  const whyAt = fabricOpsFrame(prompts.why, fps);
  const whyExitAt = fabricOpsFrame(prompts.whyExit, fps);
  const howAt = fabricOpsFrame(prompts.how, fps);
  const worksAt = fabricOpsFrame(prompts.works, fps);
  const relationshipAt = 800;
  const relationshipCircleAt = 870;
  const whyEnter = spring({frame: frame - whyAt, fps, config: {damping: 18, stiffness: 88}});
  const whyExit = interpolate(frame, [whyExitAt - 20, whyExitAt], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const howEnter = spring({frame: frame - howAt, fps, config: {damping: 18, stiffness: 88}});
  const worksEnter = spring({frame: frame - worksAt, fps, config: {damping: 14, stiffness: 105}});
  const relationshipEnter = spring({frame: frame - relationshipAt, fps, config: {damping: 16, stiffness: 100}});
  const relationshipFade = interpolate(frame, [howAt - 30, howAt - 10], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const relationshipCircle = interpolate(frame, [relationshipCircleAt, relationshipCircleAt + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
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
      {Object.entries(floatingWords).map(([key, word]) => {
        const start = fabricOpsFrame(word.start, fps);
        const fadeOutStart = start + Math.round(word.duration * fps);
        const end = fadeOutStart + 6;
        const opacity = interpolate(frame, [start, start + 5, fadeOutStart, end], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        });
        const scale = interpolate(frame, [start, start + 7, end], [0.82, 1.08, 0.96], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });
        if (frame < start || frame >= end) return null;

        return (
          <div
            key={key}
            style={{
              position: 'absolute',
              left: word.left,
              top: word.top,
              fontSize: 62.4,
              lineHeight: 1,
              fontWeight: 760,
              letterSpacing: -1.2,
              color: '#dcecff',
              opacity,
              transform: `rotate(${word.rotate}deg) scale(${scale})`,
              textShadow: '0 10px 34px #000b, 0 0 28px #279ee055',
            }}
          >
            {FLOATING_WORD_LABELS[key as keyof typeof FLOATING_WORD_LABELS]}
          </div>
        );
      })}

      {(() => {
        const start = fabricOpsFrame(relationship.governanceAsCodeStart, fps);
        const end = fabricOpsFrame(relationship.governanceAsCodeEnd, fps);
        const opacity = interpolate(frame, [start, start + 7, end - 8, end], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const scale = interpolate(frame, [start, start + 9], [0.86, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.back(1.2)),
        });
        if (opacity <= 0) return null;

        return (
          <div style={{position: 'absolute', top: 675, width: '100%', textAlign: 'center', opacity, transform: `scale(${scale})`, fontSize: 64.8, fontWeight: 760, color: '#dcecff', textShadow: '0 0 30px #38d99155'}}>
            Governance into Code
          </div>
        );
      })()}

      {frame >= relationshipAt && relationshipFade > 0 ? <div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
        {frame >= relationshipCircleAt ? <svg aria-hidden="true" width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, zIndex: 0, opacity: relationshipFade}}>
          <ellipse cx="960" cy="540" rx="830" ry="330" pathLength="1" fill="none" stroke={theme.production} strokeWidth="15" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - relationshipCircle} opacity={0.12 * relationshipCircle} />
          <ellipse cx="960" cy="540" rx="830" ry="330" pathLength="1" fill="none" stroke={theme.production} strokeWidth="7" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - relationshipCircle} opacity={relationshipCircle} />
        </svg> : null}
        <div style={{position: 'absolute', left: 63, top: 473, zIndex: 1, display: 'flex', alignItems: 'center', gap: 24, opacity: relationshipEnter * relationshipFade, scale: 0.82 + relationshipEnter * 0.18, transformOrigin: 'left center'}}>
          <DataGovernanceIcon size={134.4} />
          <div style={{color: theme.governance, fontSize: 38, fontWeight: 820, letterSpacing: 0.4, textShadow: '0 0 24px #a879ff66'}}>
            Governance
          </div>
        </div>
        <div style={{position: 'absolute', right: 63, top: 473, zIndex: 1, display: 'flex', alignItems: 'center', gap: 24, opacity: relationshipEnter * relationshipFade, scale: 0.82 + relationshipEnter * 0.18, transformOrigin: 'right center'}}>
          <div style={{color: theme.engineering, fontSize: 38, fontWeight: 820, letterSpacing: 0.4, textShadow: '0 0 24px #4ea1ff66'}}>
            Engineering
          </div>
          <DataEngineeringIcon size={134.4} />
        </div>
      </div> : null}

      <div
        style={{
          position: 'relative',
          width: 1040,
          height: 430,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: brand,
          scale: 0.86 + brand * 0.14,
        }}
      >
        {frame >= whyAt && frame <= whyExitAt ? <div
          style={{
            position: 'absolute',
            left: 65,
            top: 36,
            fontSize: VIDEO_CONFIG.text.title * 1.2,
            fontWeight: 820,
            color: '#fff',
            opacity: whyEnter,
            transform: `translate(${(1 - whyEnter) * -100 - whyExit * 980}px, ${(1 - whyEnter) * -40}px)`,
          }}
        >
          Why
        </div> : null}

        {frame >= whyAt && frame <= whyExitAt ? <div
          style={{
            position: 'absolute',
            right: 78,
            bottom: 34,
            fontSize: VIDEO_CONFIG.text.title * 1.2,
            fontWeight: 820,
            color: '#fff',
            opacity: whyEnter,
            transform: `translate(${(1 - whyEnter) * 100 + whyExit * 980}px, ${(1 - whyEnter) * 40}px)`,
          }}
        >
          ?
        </div> : null}

        <Brand />

        {frame >= howAt ? <div
          style={{
            position: 'absolute',
            left: 65,
            top: 36,
            fontSize: VIDEO_CONFIG.text.title * 1.2,
            fontWeight: 820,
            color: '#fff',
            opacity: howEnter,
            transform: `translate(${(1 - howEnter) * -110}px, ${(1 - howEnter) * -45}px)`,
          }}
        >
          How
        </div> : null}

        {frame >= worksAt ? <div
          style={{
            position: 'absolute',
            right: 75,
            bottom: 34,
            fontSize: VIDEO_CONFIG.text.title * 1.2,
            fontWeight: 820,
            color: '#fff',
            opacity: worksEnter,
            transform: `translate(${(1 - worksEnter) * 110}px, ${(1 - worksEnter) * 45}px)`,
          }}
        >
          works?
        </div> : null}
      </div>
    </div>
  );
};
