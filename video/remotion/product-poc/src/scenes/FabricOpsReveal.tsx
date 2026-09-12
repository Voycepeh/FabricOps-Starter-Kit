import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
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

export const FabricOpsReveal = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {timing} = VIDEO_CONFIG;
  const {floatingWords: wordTiming, relationship, prompts} = VIDEO_TUNING.fabricOps;

  const floatingWords = [
    {text: 'Operations', at: wordTiming.operations, left: 250, top: 250, rotate: -4},
    {text: 'Plug and play', at: wordTiming.plugAndPlay, left: 1280, top: 275, rotate: 4},
    {text: 'Self-contained', at: wordTiming.selfContained, left: 250, top: 705, rotate: 3},
    {text: 'Python', at: wordTiming.python, left: 210, top: 660, rotate: -5},
    {text: 'Notebook', at: wordTiming.notebook, left: 1320, top: 245, rotate: 4},
    {text: 'PySpark', at: wordTiming.pyspark, left: 245, top: 255, rotate: 5},
    {text: 'Lakehouse', at: wordTiming.lakehouse, left: 1285, top: 690, rotate: -4},
  ] as const;

  const brand = spring({frame, fps, config: {damping: 18, stiffness: 72}});
  const whyAt = fabricOpsFrame(prompts.why, fps);
  const whyExitAt = fabricOpsFrame(prompts.whyExit, fps);
  const howAt = fabricOpsFrame(prompts.how, fps);
  const worksAt = fabricOpsFrame(prompts.works, fps);
  const whyEnter = spring({frame: frame - whyAt, fps, config: {damping: 18, stiffness: 88}});
  const whyExit = interpolate(frame, [whyExitAt - 20, whyExitAt], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const howEnter = spring({frame: frame - howAt, fps, config: {damping: 18, stiffness: 88}});
  const worksEnter = spring({frame: frame - worksAt, fps, config: {damping: 14, stiffness: 105}});
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
        const start = fabricOpsFrame(word.at, fps);
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
        return (
          <div style={{position: 'absolute', top: 675, width: '100%', textAlign: 'center', opacity, transform: `scale(${scale})`, fontSize: 54, fontWeight: 760, color: '#dcecff', textShadow: '0 0 30px #38d99155'}}>
            Governance into Code
          </div>
        );
      })()}

      {(() => {
        const governanceStart = fabricOpsFrame(relationship.governance, fps);
        const engineeringStart = fabricOpsFrame(relationship.engineering, fps);
        const orbitStart = fabricOpsFrame(relationship.orbitStart, fps);
        const end = fabricOpsFrame(relationship.end, fps);
        const fadeOut = interpolate(frame, [end - 8, end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const orbitVisible = frame >= orbitStart && frame < end;
        const conceptStyle = (start: number) => {
          const enter = spring({frame: frame - start, fps, config: {damping: 16, stiffness: 100}});
          return {opacity: enter * fadeOut, transform: `scale(${0.82 + enter * 0.18})`};
        };
        const orbitProgress = interpolate(frame, [orbitStart, orbitStart + 24], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        });
        return (
          <div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
            {orbitVisible ? (
              <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, opacity: fadeOut}}>
                <ellipse cx="960" cy="540" rx="760" ry="245" fill="none" stroke={theme.production} strokeWidth="7" strokeLinecap="round" strokeDasharray="3300" strokeDashoffset={3300 * (1 - orbitProgress)} style={{filter: 'drop-shadow(0 0 12px #38d99188)'}} />
                <circle cx="200" cy="540" r="10" fill={theme.production} opacity={orbitProgress} />
                <circle cx="1720" cy="540" r="10" fill={theme.production} opacity={orbitProgress} />
              </svg>
            ) : null}
            <div style={{position: 'absolute', left: 105, top: 505, width: 310, textAlign: 'center', fontSize: 52, fontWeight: 780, color: '#fff', textShadow: '0 0 26px #38d99166', ...conceptStyle(governanceStart)}}>Governance</div>
            <div style={{position: 'absolute', right: 85, top: 505, width: 340, textAlign: 'center', fontSize: 52, fontWeight: 780, color: '#fff', textShadow: '0 0 26px #38d99166', ...conceptStyle(engineeringStart)}}>Engineering</div>
          </div>
        );
      })()}

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
