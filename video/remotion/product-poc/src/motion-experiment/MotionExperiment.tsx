import type {ReactNode} from 'react';
import {Audio} from '@remotion/media';
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {LifecycleScene} from '../scenes/LifecycleScene';
import {font, theme} from '../theme';
import {
  EXPERIMENT_DURATION,
  EXPERIMENT_TIMELINE,
  SOURCE_LOCAL_START_FRAME,
  SOURCE_START_FRAME,
  clamp01,
  easeIn,
  easeInOut,
  easeOut,
  fonts,
  mix,
  palette,
  progress,
  settle,
} from './motion';

const narration = staticFile('audio/FabricOps_narration_master_numbered.m4a');
const soundDesign = staticFile('generated/motion-experiment-sfx.wav');

const Grain = ({frame}: {frame: number}) => (
  <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'soft-light', opacity: 0.075}}>
    <svg width="100%" height="100%">
      <filter id="motion-grain">
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.72"
          numOctaves={2}
          seed={Math.floor(frame / 2) % 89}
          stitchTiles="stitch"
        />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#motion-grain)" />
    </svg>
  </AbsoluteFill>
);

const Stage = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const handoff = progress(time, 7.5, 14.5, easeInOut);
  const consumer = progress(time, 25.2, 27, easeInOut);
  const cameraX = mix(0, -1370, handoff) - mix(0, 1370, consumer);
  const cameraScale = mix(1.06, 0.9, handoff) + mix(0, 0.08, consumer);

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: 4660,
        height: 1080,
        translate: `${cameraX}px 0px`,
        scale: cameraScale,
        transformOrigin: '960px 540px',
      }}
    >
      <GovernanceWorld frame={frame} />
      <ProductionWorld frame={frame} />
      <ConsumerWorld frame={frame} />
      <PersistentRoute frame={frame} />
    </div>
  );
};

const AmbientBackground = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const glow = progress(time, 7.5, 22.1, easeInOut);
  return (
    <AbsoluteFill style={{background: palette.background}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${28 + glow * 42}% 58%, rgba(56,217,145,${0.04 + glow * 0.1}) 0%, rgba(78,161,255,0.045) 32%, transparent 66%)`,
        }}
      />
      <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        <defs>
          <pattern id="experiment-grid" width="48" height="48" patternUnits="userSpaceOnUse" patternTransform={`translate(${-time * 2} ${-time * 3})`}>
            <circle cx="24" cy="24" r="1.2" fill="rgba(174,202,232,0.13)" />
          </pattern>
          <radialGradient id="grid-mask-gradient">
            <stop offset="0%" stopColor="white" />
            <stop offset="78%" stopColor="white" stopOpacity="0.22" />
            <stop offset="100%" stopColor="black" stopOpacity="0" />
          </radialGradient>
          <mask id="grid-mask"><rect width="100%" height="100%" fill="url(#grid-mask-gradient)" /></mask>
        </defs>
        <rect width="100%" height="100%" fill="url(#experiment-grid)" mask="url(#grid-mask)" />
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.58) 100%)'}} />
    </AbsoluteFill>
  );
};

const Eyebrow = ({color, children}: {color: string; children: ReactNode}) => (
  <div style={{fontFamily: fonts.mono, fontSize: 18, fontWeight: 700, letterSpacing: '0.18em', color, textTransform: 'uppercase'}}>
    {children}
  </div>
);

const StepBadge = ({number, color}: {number: number; color: string}) => (
  <div
    style={{
      width: 68,
      height: 68,
      borderRadius: 22,
      display: 'grid',
      placeItems: 'center',
      background: color,
      color: palette.background,
      fontFamily: fonts.display,
      fontSize: 34,
      fontWeight: 900,
      boxShadow: `0 0 42px ${color}55`,
    }}
  >
    {number}
  </div>
);

const PriorSteps = ({frame}: {frame: number}) => {
  const enter = 0.78 + settle(frame, 0.1, EXPERIMENT_TIMELINE.fps, {damping: 20}) * 0.22;
  const items = [
    ['1', 'Data Agreement', palette.governance],
    ['2', 'ETL, Profile & Catalogue', palette.engineering],
    ['3', 'Data Contract', palette.governance],
    ['4', 'Contract Guardrails', palette.engineering],
  ] as const;
  return (
    <div style={{position: 'absolute', left: 150, top: 92, display: 'flex', alignItems: 'center', gap: 14, opacity: enter * 0.78}}>
      {items.map(([number, label, color], index) => (
        <div key={number} style={{display: 'flex', alignItems: 'center', gap: 14}}>
          <div style={{height: 44, padding: '0 17px', borderRadius: 22, display: 'flex', alignItems: 'center', gap: 10, background: `${color}12`, border: `1px solid ${color}38`, color: palette.muted, fontFamily: fonts.display, fontSize: 17, fontWeight: 650}}>
            <span style={{color, fontFamily: fonts.mono, fontWeight: 800}}>{number}</span>{label}
          </div>
          {index < items.length - 1 ? <span style={{color: palette.muted, fontSize: 20}}>→</span> : null}
        </div>
      ))}
    </div>
  );
};

const GovernanceWorld = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const enter = 0.72 + settle(frame, 0, EXPERIMENT_TIMELINE.fps, {damping: 21, stiffness: 155}) * 0.28;
  const activate = settle(frame, 1.1, EXPERIMENT_TIMELINE.fps, {damping: 12, stiffness: 190, mass: 0.75});
  const exit = progress(time, 7.8, 11.4, easeIn);
  const stampScale = 0.84 + activate * 0.16;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, opacity: 1 - exit}}>
      <PriorSteps frame={frame} />
      <div style={{position: 'absolute', left: 150, top: 215, opacity: enter, translate: `0px ${(1 - enter) * 46}px`}}>
        <Eyebrow color={palette.governance}>Governance workspace</Eyebrow>
        <div style={{fontFamily: fonts.display, fontSize: 92, lineHeight: 0.98, letterSpacing: '-0.045em', fontWeight: 800, color: palette.text, marginTop: 20}}>
          Activate the contract.<br /><span style={{color: palette.governance}}>Promote with intent.</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 150, top: 515, width: 1050, height: 350, borderRadius: 42, background: 'linear-gradient(145deg, rgba(26,30,57,0.96), rgba(10,20,36,0.94))', border: `1px solid ${palette.governance}55`, boxShadow: '0 38px 100px rgba(0,0,0,0.38)', opacity: enter, scale: 0.96 + enter * 0.04, transformOrigin: 'left center'}}>
        <div style={{position: 'absolute', left: 56, top: 54, display: 'flex', alignItems: 'center', gap: 26}}>
          <StepBadge number={5} color={palette.governance} />
          <div>
            <div style={{fontFamily: fonts.display, fontSize: 48, fontWeight: 800, color: palette.text}}>Activate &amp; Promote</div>
            <div style={{fontFamily: fonts.display, fontSize: 25, color: palette.muted, marginTop: 8}}>Governed approval moves the pipeline toward Production.</div>
          </div>
        </div>
        <div style={{position: 'absolute', left: 56, right: 56, bottom: 48, height: 104, borderRadius: 24, background: 'rgba(6,13,25,0.72)', border: `1px solid ${palette.line}`, display: 'flex', alignItems: 'center', padding: '0 30px', gap: 24}}>
          <div style={{width: 46, height: 54, borderRadius: 9, background: `${palette.governance}24`, border: `2px solid ${palette.governance}`, position: 'relative'}}>
            <div style={{position: 'absolute', left: 9, right: 9, top: 14, height: 3, borderRadius: 2, background: palette.governance}} />
            <div style={{position: 'absolute', left: 9, right: 15, top: 25, height: 3, borderRadius: 2, background: `${palette.governance}aa`}} />
            <div style={{position: 'absolute', left: 9, right: 11, top: 36, height: 3, borderRadius: 2, background: `${palette.governance}77`}} />
          </div>
          <div style={{fontFamily: fonts.display, color: palette.text, fontSize: 26, fontWeight: 700}}>Data Contract</div>
          <div style={{height: 1, flex: 1, background: `linear-gradient(90deg, ${palette.governance}66, transparent)`}} />
          <div style={{padding: '13px 21px', borderRadius: 999, border: `1px solid ${palette.production}66`, color: palette.production, background: `${palette.production}12`, fontFamily: fonts.mono, fontSize: 17, letterSpacing: '0.12em', fontWeight: 800, opacity: activate, scale: stampScale}}>ACTIVATED</div>
        </div>
      </div>
    </div>
  );
};

const DataPacket = ({x, y, color, opacity = 1, scale = 1}: {x: number; y: number; color: string; opacity?: number; scale?: number}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 20, height: 20, borderRadius: 6, background: color, boxShadow: `0 0 24px ${color}`, opacity, scale}} />
);

const ProductionWorld = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const enter = progress(time, 10.5, 14.5, easeOut);
  const run = progress(time, 14.5, 22.1, easeInOut);
  const approved = settle(frame, 22.1, EXPERIMENT_TIMELINE.fps, {damping: 10, stiffness: 200});
  const exit = progress(time, 25.2, 27, easeInOut);
  const checks = EXPERIMENT_TIMELINE.beats.pipelineChecks.map((beat) => settle(frame, beat, EXPERIMENT_TIMELINE.fps, {damping: 12, stiffness: 190}));
  const nodes = [
    {x: 2240, label: 'Read', caption: 'Prepared input'},
    {x: 2660, label: 'Transform', caption: 'Project logic'},
    {x: 3080, label: 'Write', caption: 'Governed target'},
  ] as const;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 4660, height: 1080, opacity: 1 - exit}}>
      <div style={{position: 'absolute', left: 2130, top: 132, opacity: enter, translate: `0px ${(1 - enter) * 36}px`}}>
        <Eyebrow color={palette.production}>Engineering Production workspace</Eyebrow>
        <div style={{fontFamily: fonts.display, fontSize: 88, lineHeight: 1, letterSpacing: '-0.04em', fontWeight: 820, color: palette.text, marginTop: 20}}>Run the Production pipeline.</div>
        <div style={{fontFamily: fonts.display, fontSize: 29, color: palette.muted, marginTop: 22}}>The same contract guardrails travel with the governed workflow.</div>
      </div>
      <div style={{position: 'absolute', left: 2110, top: 370, width: 1275, height: 435, borderRadius: 50, background: 'linear-gradient(145deg, rgba(11,31,39,0.96), rgba(8,18,32,0.95))', border: `1px solid ${palette.production}52`, boxShadow: `0 40px 120px rgba(0,0,0,0.42), inset 0 0 90px ${palette.production}08`, opacity: enter}}>
        <div style={{position: 'absolute', left: 58, top: 50, display: 'flex', alignItems: 'center', gap: 24}}>
          <StepBadge number={6} color={palette.production} />
          <div style={{fontFamily: fonts.display, fontSize: 42, fontWeight: 820, color: palette.text}}>Run Production Pipeline</div>
        </div>
        <svg width="1275" height="435" style={{position: 'absolute', inset: 0}}>
          <defs>
            <linearGradient id="production-route" x1="0" x2="1"><stop stopColor={palette.engineering} /><stop offset="1" stopColor={palette.production} /></linearGradient>
          </defs>
          <path d="M145 284 H1125" fill="none" stroke={palette.line} strokeWidth="8" strokeLinecap="round" />
          <path d="M145 284 H1125" pathLength="1" fill="none" stroke="url(#production-route)" strokeWidth="8" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - run} style={{filter: `drop-shadow(0 0 14px ${palette.production})`}} />
        </svg>
        {nodes.map((node, index) => {
          const nodeEnter = checks[index];
          return (
            <div key={node.label} style={{position: 'absolute', left: node.x - 2110 - 100, top: 215, width: 200, textAlign: 'center', opacity: 0.24 + nodeEnter * 0.76, translate: `0px ${(1 - nodeEnter) * 18}px`}}>
              <div style={{width: 74, height: 74, margin: '0 auto', borderRadius: 24, display: 'grid', placeItems: 'center', background: nodeEnter > 0.5 ? palette.production : palette.surfaceHigh, border: `2px solid ${nodeEnter > 0.5 ? palette.production : palette.line}`, color: nodeEnter > 0.5 ? palette.background : palette.muted, fontSize: 34, fontWeight: 900, boxShadow: nodeEnter > 0.5 ? `0 0 34px ${palette.production}55` : 'none'}}>{nodeEnter > 0.5 ? '✓' : index + 1}</div>
              <div style={{fontFamily: fonts.display, fontSize: 25, fontWeight: 800, color: palette.text, marginTop: 20}}>{node.label}</div>
              <div style={{fontFamily: fonts.display, fontSize: 18, color: palette.muted, marginTop: 6}}>{node.caption}</div>
            </div>
          );
        })}
        {[0, 1, 2, 3, 4].map((index) => {
          const packetProgress = clamp01(run * 1.35 - index * 0.13);
          return <DataPacket key={index} x={145 + packetProgress * 980} y={274} color={index % 2 === 0 ? palette.engineering : palette.production} opacity={enter * (packetProgress > 0 && packetProgress < 1 ? 1 : 0)} scale={0.75 + index * 0.07} />;
        })}
        <div style={{position: 'absolute', right: 58, top: 52, padding: '12px 18px', borderRadius: 999, border: `1px solid ${palette.production}66`, background: `${palette.production}12`, color: palette.production, fontFamily: fonts.mono, fontSize: 16, fontWeight: 800, letterSpacing: '0.12em', opacity: approved, scale: 0.85 + approved * 0.15}}>GUARDRAILS PASSED</div>
      </div>
    </div>
  );
};

const ConsumerWorld = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const enter = progress(time, 24.6, 27, easeOut);
  const settleIn = settle(frame, 25.2, EXPERIMENT_TIMELINE.fps, {damping: 12, stiffness: 175});
  const exit = progress(time, 29.1, 29.5, easeIn);
  return (
    <div style={{position: 'absolute', left: 2740, top: 0, width: 1920, height: 1080, opacity: enter * (1 - exit)}}>
      <div style={{position: 'absolute', left: 575, top: 150, width: 980, textAlign: 'center'}}>
        <Eyebrow color={palette.consumer}>Consumer workspace</Eyebrow>
        <div style={{fontFamily: fonts.display, fontSize: 86, lineHeight: 1.02, letterSpacing: '-0.045em', fontWeight: 820, color: palette.text, marginTop: 20}}>
          Consume approved<br /><span style={{color: palette.consumer}}>Production data.</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 720, top: 535, width: 700, height: 300, borderRadius: 44, background: 'linear-gradient(145deg, rgba(47,33,21,0.94), rgba(10,18,31,0.97))', border: `1px solid ${palette.consumer}66`, boxShadow: `0 46px 140px rgba(0,0,0,0.48), 0 0 90px ${palette.consumer}16`, opacity: settleIn, translate: `${(1 - settleIn) * -110}px 0px`, scale: 0.92 + settleIn * 0.08}}>
        <div style={{position: 'absolute', left: 48, top: 48, display: 'flex', alignItems: 'center', gap: 24}}>
          <StepBadge number={7} color={palette.consumer} />
          <div>
            <div style={{fontFamily: fonts.display, fontSize: 38, fontWeight: 820, color: palette.text}}>Approved Production data</div>
            <div style={{fontFamily: fonts.display, fontSize: 23, color: palette.muted, marginTop: 8}}>Ready for governed consumption</div>
          </div>
        </div>
        <div style={{position: 'absolute', left: 48, right: 48, bottom: 48, display: 'flex', gap: 14}}>
          {['Approved', 'Production', 'Traceable'].map((label, index) => (
            <div key={label} style={{flex: 1, height: 54, borderRadius: 15, display: 'grid', placeItems: 'center', border: `1px solid ${palette.consumer}${index === 0 ? '70' : '35'}`, background: `${palette.consumer}${index === 0 ? '18' : '0c'}`, color: index === 0 ? palette.consumer : palette.muted, fontFamily: fonts.mono, fontSize: 15, letterSpacing: '0.08em', fontWeight: 750}}>{label.toUpperCase()}</div>
          ))}
        </div>
      </div>
    </div>
  );
};

const PersistentRoute = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const travel = progress(time, 7.5, 25.2, easeInOut);
  const x = mix(1130, 3460, travel);
  const color = travel < 0.55 ? palette.governance : travel < 0.94 ? palette.production : palette.consumer;
  return (
    <>
      <svg width="4660" height="1080" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <path d="M1130 900 C1580 900 1650 650 2100 650 H3390" fill="none" stroke={palette.line} strokeWidth="4" strokeDasharray="10 16" />
      </svg>
      {time >= 7.5 && time <= 25.5 ? (
        <div style={{position: 'absolute', left: x, top: mix(890, 640, clamp01(travel * 2.1)), width: 30, height: 30, borderRadius: 10, background: color, boxShadow: `0 0 18px ${color}, 0 0 58px ${color}88`, rotate: `${travel * 220}deg`, scale: 0.82 + Math.sin(frame * 0.18) * 0.08}} />
      ) : null}
    </>
  );
};

const ChapterMarker = ({frame}: {frame: number}) => {
  const time = frame / EXPERIMENT_TIMELINE.fps;
  const active = time < 14.5 ? 5 : time < 25.2 ? 6 : 7;
  return (
    <div style={{position: 'absolute', left: 78, bottom: 56, display: 'flex', alignItems: 'center', gap: 18, padding: '15px 22px', borderRadius: 20, background: 'rgba(5,11,22,0.7)', border: `1px solid ${palette.line}`, backdropFilter: 'blur(18px)'}}>
      <div style={{fontFamily: fonts.mono, color: palette.muted, fontSize: 14, letterSpacing: '0.18em'}}>FABRICOPS LIFECYCLE</div>
      {[5, 6, 7].map((step) => {
        const color = step === 5 ? palette.governance : step === 6 ? palette.production : palette.consumer;
        const isActive = active === step;
        return <div key={step} style={{width: isActive ? 50 : 12, height: 12, borderRadius: 999, background: isActive ? color : palette.faint, boxShadow: isActive ? `0 0 18px ${color}88` : 'none'}} />;
      })}
    </div>
  );
};

const EnhancedVisual = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: palette.background, color: palette.text, fontFamily: fonts.display}}>
      <AmbientBackground frame={frame} />
      <Stage frame={frame} />
      <ChapterMarker frame={frame} />
      <Grain frame={frame} />
    </AbsoluteFill>
  );
};

const OriginalVisual = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}} />
      <Sequence from={-SOURCE_LOCAL_START_FRAME} durationInFrames={SOURCE_LOCAL_START_FRAME + EXPERIMENT_DURATION} premountFor={fps}>
        <LifecycleScene />
      </Sequence>
    </AbsoluteFill>
  );
};

export const FabricOpsPart1OriginalSample = () => (
  <AbsoluteFill>
    <OriginalVisual />
    <Audio name="Original narration" src={narration} trimBefore={SOURCE_START_FRAME} durationInFrames={EXPERIMENT_DURATION} />
  </AbsoluteFill>
);

export const FabricOpsPart1MotionExperiment = () => {
  return (
    <AbsoluteFill>
      <EnhancedVisual />
      <Audio name="Original narration" src={narration} trimBefore={SOURCE_START_FRAME} durationInFrames={EXPERIMENT_DURATION} />
      <Audio name="Motion sound design" src={soundDesign} volume={0.42} />
    </AbsoluteFill>
  );
};

const ComparisonLabel = ({children, color}: {children: ReactNode; color: string}) => (
  <div style={{position: 'absolute', left: 64, top: 54, zIndex: 20, padding: '15px 24px', borderRadius: 999, background: 'rgba(5,11,22,0.82)', border: `1px solid ${color}88`, color, fontFamily: fonts.mono, fontSize: 19, fontWeight: 800, letterSpacing: '0.14em', boxShadow: '0 16px 40px rgba(0,0,0,0.32)'}}>{children}</div>
);

export const FabricOpsPart1MotionComparison = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: palette.background}}>
      <Sequence name="Original" width={1920} height={1080} premountFor={fps}>
        <OriginalVisual />
        <ComparisonLabel color={palette.muted}>VERSION A · ORIGINAL</ComparisonLabel>
      </Sequence>
      <Sequence name="Claude Motion enhanced" from={0} width={1920} height={1080} premountFor={fps} style={{left: 1920}}>
        <EnhancedVisual />
        <ComparisonLabel color={palette.production}>VERSION B · MOTION ENHANCED</ComparisonLabel>
      </Sequence>
      <Audio name="Original narration" src={narration} trimBefore={SOURCE_START_FRAME} durationInFrames={EXPERIMENT_DURATION} />
      <Audio name="Motion sound design" src={soundDesign} volume={0.42} />
      <div style={{position: 'absolute', left: 1917, top: 0, bottom: 0, width: 6, background: 'linear-gradient(180deg, transparent, rgba(255,255,255,0.45), transparent)', zIndex: 30}} />
    </AbsoluteFill>
  );
};
