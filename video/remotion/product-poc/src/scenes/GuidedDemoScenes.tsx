import {memo, type CSSProperties, type ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {NARRATION_CUE_SHEET} from '../narrationCues';
import {font, theme} from '../theme';
import {GUIDED_SCENE_DURATIONS, seconds, VIDEO_CONFIG} from '../videoConfig';
import {AnimatedDataFlow, AnimatedFlowPath} from '../components/AnimatedDataFlow';
import {DataEngineeringIcon, DataGovernanceIcon} from '../components/TeamIdentityIcons';

const {
  dataEngineers: DATA_ENGINEERS_DURATION,
  repeatablePipeline: REPEATABLE_PIPELINE_DURATION,
  sensitiveData: SENSITIVE_DATA_DURATION,
  businessRules: BUSINESS_RULES_DURATION,
  bigPicture: BIG_PICTURE_DURATION,
  promotion: PROMOTION_DURATION,
  closing: CLOSING_DURATION,
} = GUIDED_SCENE_DURATIONS;

const PIPELINE_LAYOUT = {
  left: 200,
  cardWidth: 430,
  cardHeight: 280,
  gap: 115,
  transformLeft: 745,
  writeLeft: 1290,
} as const;

const VALIDATION_LAYOUT = {
  pipelineTop: 200,
  tableTop: 650,
  tableWidth: 750,
  tableHeight: 236,
  rawLeft: 40,
  outputLeft: 1130,
  readCenter: PIPELINE_LAYOUT.left + PIPELINE_LAYOUT.cardWidth / 2,
  writeCenter: PIPELINE_LAYOUT.writeLeft + PIPELINE_LAYOUT.cardWidth / 2,
} as const;

const FLOW_COLOR = '#5FE1D0';
const BUSINESS_RULE_FONT_SCALE = 1.2;

const DATA_ENGINEER_TASKS = [
  {label: 'Connect', detail: 'Data stores', cueIndex: 1, accent: '#69b7ff'},
  {label: 'Resolve', detail: 'Paths', cueIndex: 2, accent: '#52d6c6'},
  {label: 'Profile', detail: 'Profiling + EDA', cueIndex: 3, accent: '#b487ff'},
  {label: 'Validate', detail: 'Quality checks', cueIndex: 4, accent: '#ffae66'},
] as const;

const DATA_ENGINEER_CODE_LINES = [
  {width: 76, color: '#69b7ff'},
  {width: 54, color: '#52d6c6'},
  {width: 66, color: '#b487ff'},
  {width: 43, color: '#ffae66'},
] as const;

const DATA_ENGINEER_IMPLEMENTATIONS = [
  {engineer: 'Engineer A', context: 'Prompt A · Model 1', accent: '#69b7ff', widths: [76, 48, 64, 38], offset: -9, rotate: -0.65},
  {engineer: 'Engineer B', context: 'Prompt B · Model 2', accent: '#b487ff', widths: [48, 82, 56, 70], offset: 11, rotate: 0.55},
  {engineer: 'Engineer C', context: 'Prompt C · Model 3', accent: '#ff9c72', widths: [68, 42, 78, 51], offset: -5, rotate: -0.35},
] as const;

const PIPELINE_MASCOT_FORMATION = [
  {x: 0, y: -55},
  {x: 210, y: 35},
  {x: 420, y: -25},
  {x: 630, y: 65},
] as const;

const SENSITIVE_IDENTITY_ROWS = [
  {before: 'S1234567D', after: 'S****567D'},
  {before: 'T7654321F', after: 'T****321F'},
  {before: 'F2468135N', after: 'F****135N'},
] as const;

const BIG_PICTURE_ROWS = [
  {id: '00007', nric: 'S1234567D', maskedNric: 'S****567D', order: '09:00', modified: '09:18', result: 'PASS', color: '#72e6ad'},
  {id: '00008', nric: 'T7654321F', maskedNric: 'T****321F', order: '09:00', modified: '08:00', result: 'FAIL', color: '#ff756d'},
] as const;

const MascotArtwork = memo(({pose, shadow = 'drop-shadow(0 16px 26px #0008)'}: {pose: MascotName; shadow?: string}) => <Img src={mascotSrc(pose)} style={{width: '100%', height: '100%', objectFit: 'contain', filter: shadow}} />);

const Mascot = ({pose, x, y, size, delay}: {pose: MascotName; x: number; y: number; size: number; delay: number}) => {
  const frame = useCurrentFrame();
  if (frame < delay) return null;

  const progress = interpolate(frame, [delay, delay + seconds(0.6)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <div style={{position: 'absolute', left: x, top: y, width: size, height: size, opacity: progress, translate: `0 ${(1 - progress) * 24}px`}}>
    <MascotArtwork pose={pose} />
  </div>;
};

const sceneOpacity = (frame: number, duration: number) => interpolate(
  frame,
  [0, seconds(0.7), duration - seconds(0.7), duration],
  [0, 1, 1, 0],
  {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)},
);

const enterProgress = (frame: number, fps: number, at: number) => spring({
  frame: frame - at,
  fps,
  durationInFrames: seconds(0.7),
  config: {damping: 20, stiffness: 105, mass: 0.8},
});

const Reveal = ({at, children, x = 0, y = 22}: {at: number; children: ReactNode; x?: number; y?: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (frame < at) return null;

  const progress = enterProgress(frame, fps, at);
  return <div style={{opacity: progress, translate: `${(1 - progress) * x}px ${(1 - progress) * y}px`}}>{children}</div>;
};

const SceneShell = ({duration, eyebrow, heading, subheading, accent, children}: {duration: number; eyebrow?: string; heading: string; subheading?: string; accent: string; children: ReactNode}) => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{
    opacity: sceneOpacity(frame, duration), color: theme.text, fontFamily: font,
  }}>
    <AbsoluteFill style={{opacity: 0.14, backgroundImage: 'linear-gradient(#7aa7d51a 1px, transparent 1px), linear-gradient(90deg, #7aa7d51a 1px, transparent 1px)', backgroundSize: '64px 64px'}} />
    <div style={{position: 'absolute', top: 58, left: 104, right: 104}}>
      {eyebrow ? <div style={{fontSize: 21, fontWeight: 850, letterSpacing: 2.4, color: accent}}>{eyebrow}</div> : null}
      <div style={{fontSize: 66, lineHeight: 1.05, fontWeight: 950, marginTop: eyebrow ? 20 : 0, letterSpacing: -1.4}}>{heading}</div>
      {subheading ? <div style={{fontSize: 28, color: '#afc0d5', marginTop: 20}}>{subheading}</div> : null}
    </div>
    {children}
  </AbsoluteFill>;
};

const Surface = ({children, accent, style}: {children: ReactNode; accent: string; style?: CSSProperties}) => <div style={{
  borderRadius: 26, border: `2px solid ${accent}80`,
  background: 'linear-gradient(145deg, #142b47f2, #0b1729f2)',
  boxShadow: `0 22px 55px #0008, inset 0 1px 0 ${accent}22`,
  boxSizing: 'border-box', ...style,
}}>{children}</div>;

const PipelinePattern = memo(({top, read, transform, transformScale = 1, write, firstLink, secondLink, linkColor, firstLinkOpacity = 1, secondLinkOpacity = 1, writeDetail}: {top: number; read: number; transform: number; transformScale?: number; write: number; firstLink: number; secondLink: number; linkColor?: string; firstLinkOpacity?: number; secondLinkOpacity?: number; writeDetail?: string}) => <>
  <AnimatedDataFlow style={{zIndex: 0}}>
    <AnimatedFlowPath id={`pipeline-read-${top}`} d={`M${PIPELINE_LAYOUT.left + PIPELINE_LAYOUT.cardWidth} ${top + PIPELINE_LAYOUT.cardHeight / 2} H${PIPELINE_LAYOUT.transformLeft}`} progress={firstLink} color={linkColor ?? '#52d6c6'} opacity={firstLinkOpacity} />
    <AnimatedFlowPath id={`pipeline-write-${top}`} d={`M${PIPELINE_LAYOUT.transformLeft + PIPELINE_LAYOUT.cardWidth} ${top + PIPELINE_LAYOUT.cardHeight / 2} H${PIPELINE_LAYOUT.writeLeft}`} progress={secondLink} color={linkColor ?? '#72e6ad'} opacity={secondLinkOpacity} />
  </AnimatedDataFlow>
  <div style={{position: 'absolute', left: PIPELINE_LAYOUT.left, top, width: PIPELINE_LAYOUT.writeLeft - PIPELINE_LAYOUT.left + PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, zIndex: 1}}>
    {read > 0 ? <Surface accent="#69b7ff" style={{position: 'absolute', left: 0, width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: read, translate: `0 ${(1 - read) * 24}px`}}>
      <div style={{fontSize: 20, color: '#8fc9ff', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED READ</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 34, color: '#d8ecff', fontWeight: 800, marginTop: 46}}>orchestrate_read()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 38}}>Governed source</div>
    </Surface> : null}
    {transform > 0 ? <Surface accent="#52d6c6" style={{position: 'absolute', left: PIPELINE_LAYOUT.transformLeft - PIPELINE_LAYOUT.left, zIndex: 2, width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: transform, translate: `0 ${(1 - transform) * 24}px`, scale: transformScale, transformOrigin: 'center'}}>
      <div style={{fontSize: 20, color: '#7ae4d8', letterSpacing: 1.8, fontWeight: 850}}>YOUR LOGIC</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 39, color: '#f6fbff', fontWeight: 850, marginTop: 43}}>PySpark</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 34}}>Your transformation</div>
    </Surface> : null}
    {write > 0 ? <Surface accent="#69b7ff" style={{position: 'absolute', left: PIPELINE_LAYOUT.writeLeft - PIPELINE_LAYOUT.left, width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: write, translate: `0 ${(1 - write) * 24}px`}}>
      <div style={{fontSize: 20, color: '#8fc9ff', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED WRITE</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 32, color: '#d8ecff', fontWeight: 800, marginTop: 46}}>orchestrate_write()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: writeDetail ? 24 : 38}}>Governed target</div>
      {writeDetail ? <div style={{fontSize: 16, color: '#80cdb2', marginTop: 14, lineHeight: 1.25}}>{writeDetail}</div> : null}
    </Surface> : null}
  </div>
</>);

const SpeechBubble = ({accent, eyebrow, children, style, fontScale = 1}: {accent: string; eyebrow: string; children: ReactNode; style: CSSProperties; fontScale?: number}) => <div style={{
  position: 'absolute', borderRadius: 18, border: `1px solid ${accent}99`, background: '#10243cf2',
  padding: '23px 30px', boxSizing: 'border-box', boxShadow: '0 14px 35px #0006', ...style,
}}>
  <div style={{fontSize: 18 * fontScale, fontWeight: 900, letterSpacing: 1.5, color: accent}}>{eyebrow}</div>
  <div style={{fontSize: 34 * fontScale, fontWeight: 780, lineHeight: 1.24, marginTop: 9, color: '#f3f7fc'}}>{children}</div>
  <div style={{position: 'absolute', left: -13, bottom: 31, width: 24, height: 24, background: '#10243c', borderLeft: `1px solid ${accent}99`, borderBottom: `1px solid ${accent}99`, rotate: '45deg'}} />
</div>;

export const DataEngineersScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.dataEngineers;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const introEnd = 5880 - cue.startFrame;
  const aiEnter = 6250 - cue.startFrame;
  const aiFadeAt = 600;
  const introOpacity = interpolate(frame, [0, seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const inconsistencyAt = aiFadeAt;
  const implementationsAt = localCue(7);
  const taskOpacity = interpolate(frame, [aiEnter - seconds(0.35), aiEnter + seconds(0.25)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const aiOpacity = interpolate(frame, [aiEnter, aiEnter + seconds(0.35), aiFadeAt, aiFadeAt + seconds(0.35)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const implementationOpacity = interpolate(frame, [inconsistencyAt, inconsistencyAt + seconds(0.45)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const misalignment = interpolate(frame, [implementationsAt, implementationsAt + seconds(0.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <SceneShell duration={DATA_ENGINEERS_DURATION} heading="" accent={theme.engineering}>
    {introOpacity > 0 ? <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', textAlign: 'center', fontSize: 91, fontWeight: 900, letterSpacing: 1.5, color: '#f2f7fc', opacity: introOpacity, translate: `0 ${(1 - introOpacity) * 12}px`}}>Rewriting Boilerplate Code</div> : null}

    {frame >= localCue(1) && taskOpacity > 0 ? <div style={{position: 'absolute', left: 140, right: 140, top: 405, display: 'flex', gap: 32, opacity: taskOpacity}}>
      {DATA_ENGINEER_TASKS.map(({label, detail, cueIndex, accent}) => {
        const at = localCue(cueIndex);
        const progress = enterProgress(frame, fps, at);
        return <Surface key={label} accent={accent} style={{flex: 1, height: 196, padding: '38px 34px', opacity: progress, translate: `0 ${(1 - progress) * 16}px`}}>
          <div style={{width: 48, height: 5, borderRadius: 99, background: accent}} />
          <div style={{fontSize: 34, fontWeight: 850, color: '#f2f7fc', marginTop: 27}}>{label}</div>
          <div style={{fontSize: 21, color: '#9fb1c5', marginTop: 12}}>{detail}</div>
        </Surface>;
      })}
    </div> : null}

    {aiOpacity > 0 ? <Surface accent="#52d6c6" style={{position: 'absolute', left: 520, top: 320, width: 880, height: 390, padding: '46px 54px', opacity: aiOpacity, translate: `0 ${(1 - aiOpacity) * 12}px`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 27}}>
        <div style={{width: 78, height: 78, borderRadius: 22, display: 'grid', placeItems: 'center', background: '#123f45', border: '1px solid #52d6c688', color: '#a8fff4', fontFamily: 'ui-monospace, monospace', fontSize: 30, fontWeight: 900}}>&lt;/&gt;</div>
        <div>
          <div style={{fontSize: 23, fontWeight: 900, color: '#7ae4d8', letterSpacing: 1.8}}>AI-ASSISTED</div>
          <div style={{fontSize: 43, fontWeight: 850, color: '#f2f9fb', marginTop: 7}}>Faster coding</div>
        </div>
      </div>
      <div style={{marginTop: 43, display: 'grid', gap: 18}}>
        {DATA_ENGINEER_CODE_LINES.map(({width, color}, index) => {
          const lineProgress = interpolate(frame, [aiEnter + index * seconds(0.2), aiFadeAt - (DATA_ENGINEER_CODE_LINES.length - 1 - index) * seconds(0.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          return <div key={width} style={{height: 11, width: `${width * lineProgress}%`, marginLeft: index === 0 ? 0 : 44, borderRadius: 99, background: color, opacity: 0.38 + lineProgress * 0.62}} />;
        })}
      </div>
    </Surface> : null}

    {implementationOpacity > 0 ? <div style={{position: 'absolute', left: 220, right: 220, top: 350, display: 'flex', gap: 58, opacity: implementationOpacity}}>
      {DATA_ENGINEER_IMPLEMENTATIONS.map(({engineer, context, accent, widths, offset, rotate}, index) => {
        const progress = enterProgress(frame, fps, inconsistencyAt + seconds(index * 0.13));
        return <Surface key={engineer} accent={accent} style={{flex: 1, height: 350, padding: '30px 32px', opacity: progress, translate: `0 ${(1 - progress) * 15 + offset * misalignment}px`, rotate: `${rotate * misalignment}deg`}}>
          <div style={{fontSize: 35, fontWeight: 850, color: '#f1f6fb'}}>{engineer}</div>
          <div style={{fontSize: 24, fontWeight: 750, color: accent, marginTop: 8, letterSpacing: 0.7}}>{context}</div>
          <div style={{height: 1, background: '#33465c', margin: '25px 0 27px'}} />
          <div style={{display: 'grid', gap: index === 1 ? 21 : 17}}>
            {widths.map((width, lineIndex) => <div key={`${engineer}-${lineIndex}`} style={{height: lineIndex === 0 ? 12 : 9, width: `${width}%`, marginLeft: index === 2 && lineIndex > 0 ? 28 : index === 0 && lineIndex === 2 ? 18 : 0, borderRadius: 99, background: lineIndex === 0 ? accent : '#60768d', opacity: lineIndex === 0 ? 0.9 : 0.72}} />)}
          </div>
        </Surface>;
      })}
    </div> : null}
  </SceneShell>;
};

export const RepeatablePipelineScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.repeatablePipeline;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const readAt = localCue(1);
  const transformAt = localCue(3);
  const writeAt = readAt;
  const incrementalAt = 720;
  const slowlyChangingDimensionsAt = 770;
  const read = enterProgress(frame, fps, readAt);
  const transform = enterProgress(frame, fps, transformAt);
  const write = enterProgress(frame, fps, writeAt);
  const transformScale = interpolate(
    frame,
    [transformAt - seconds(0.35), transformAt + seconds(0.45), localCue(4) - seconds(0.45), localCue(4)],
    [1, 1.2, 1.2, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)},
  );
  const firstLink = interpolate(frame, [transformAt - seconds(0.4), transformAt + seconds(0.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secondLink = interpolate(frame, [transformAt - seconds(0.2), transformAt + seconds(0.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ferryStart = 0;
  const ferryEnd = 6900 - cue.startFrame;
  const ferry = interpolate(frame, [ferryStart, ferryEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const ferryOpacity = interpolate(frame, [ferryStart, ferryEnd - seconds(0.35), ferryEnd], [1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <SceneShell duration={REPEATABLE_PIPELINE_DURATION} heading="" accent={theme.engineering}>
      <PipelinePattern top={300} read={read} transform={transform} transformScale={transformScale} write={write} firstLink={firstLink} secondLink={secondLink} />
      {ferryOpacity > 0 ? PIPELINE_MASCOT_FORMATION.map(({x, y}, index) => <div key={`pipeline-mascot-${index}`} style={{
        position: 'absolute',
        left: -460 + ferry * 2100 + x,
        top: 575 + y,
        width: 220,
        height: 220,
        opacity: ferryOpacity,
        translate: "518.2px -174.3px",
        scale: 1.8,
        rotate: "-14.9deg"
      }}><MascotArtwork pose="carrying" /></div>) : null}
      <Reveal at={localCue(4)} y={16}>
        <div style={{position: 'absolute', left: 150, right: 150, top: 800, display: 'flex', justifyContent: 'center', gap: 36}}>
          {[
            {label: '02A · Full Refresh', at: localCue(4)},
            {label: '02B · Incremental', at: incrementalAt},
            {label: '02C · SCD1 / SCD2', at: slowlyChangingDimensionsAt},
          ].map(({label, at}) => <div key={label} style={{padding: '26px 47px', borderRadius: 24, background: '#122d49', border: '1px solid #4d759c', fontSize: 36, fontWeight: 820, color: '#d5e9ff', opacity: enterProgress(frame, fps, at)}}>{label}</div>)}
        </div>
      </Reveal>
    </SceneShell>
  );
};

export const SensitiveDataScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.sensitiveData;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const policyAt = 7620 - cue.startFrame;
  const enforcedAt = 7720 - cue.startFrame;
  const introEnd = 7800 - cue.startFrame;
  const inspectionAt = 8430 - cue.startFrame;
  const maskAt = 950;
  const hashAt = localCue(3);
  const tokenizeAt = localCue(4);
  const removeAt = localCue(4) + seconds(1.2);
  const policyOpacity = interpolate(frame, [policyAt, policyAt + seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const enforcedOpacity = interpolate(frame, [enforcedAt, enforcedAt + seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sensitiveBubble = enterProgress(frame, fps, introEnd);
  const scan = enterProgress(frame, fps, inspectionAt);
  const treatment = enterProgress(frame, fps, maskAt);
  const redact = interpolate(frame, [maskAt, maskAt + seconds(0.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <SceneShell duration={SENSITIVE_DATA_DURATION} heading="" accent={theme.governance}>
    <div>
      {frame < introEnd ? <div style={{position: 'absolute', left: 340, right: 340, top: 455, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{fontSize: 82, fontWeight: 900, letterSpacing: 4, color: '#ffbe82', opacity: policyOpacity, translate: `0 ${(1 - policyOpacity) * 12}px`}}>POLICY</div>
        <div style={{fontSize: 82, fontWeight: 900, letterSpacing: 4, color: '#c5a8ff', opacity: enforcedOpacity, translate: `0 ${(1 - enforcedOpacity) * 12}px`}}>ENFORCED</div>
      </div> : null}
      {sensitiveBubble > 0 ? <SpeechBubble accent="#ffae66" eyebrow="Sensitive data requirement" style={{left: 555, top: 55, width: 810, height: 160, opacity: sensitiveBubble, scale: 1.5, transformOrigin: 'top center'}}>&ldquo;This column is sensitive.&rdquo;</SpeechBubble> : null}
      <Mascot pose="scanning" x={125} y={485} size={315} delay={inspectionAt} />
      {scan > 0 ? <Surface accent="#ffae66" style={{position: 'absolute', left: 480, top: 395, width: 850, height: 390, padding: '28px 34px', opacity: scan}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 28, color: '#ffcf9f', fontWeight: 850}}>person_nric</div><div style={{padding: '9px 18px', borderRadius: 10, background: '#5d351f', color: '#ffd2a4', fontSize: 18, fontWeight: 900, opacity: treatment}}>MASKED</div></div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', marginTop: 30, color: '#8fa7bf', fontSize: 17, fontWeight: 850}}><div>BEFORE</div><div /><div>AFTER</div></div>
        {SENSITIVE_IDENTITY_ROWS.map(({before, after}) => <div key={before} style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', alignItems: 'center', height: 72, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 29}}><div>{before}</div><div style={{color: '#66809b', textAlign: 'center'}}>→</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - redact}}>{before}</span><span style={{position: 'absolute', left: 0, opacity: redact}}>{after}</span></div></div>)}
      </Surface> : null}
      <Mascot pose="masking" x={1390} y={485} size={315} delay={maskAt} />
      {scan > 0 ? <div style={{position: 'absolute', left: 425, top: 605, width: 55, height: 5, borderRadius: 99, background: '#ffae66', scale: `${scan} 1`, transformOrigin: 'left'}} /> : null}
      {treatment > 0 ? <div style={{position: 'absolute', left: 1330, top: 605, width: 60, height: 5, borderRadius: 99, background: '#ffae66', scale: `${treatment} 1`, transformOrigin: 'left'}} /> : null}
      {frame >= hashAt ? <div style={{position: 'absolute', left: 430, right: 430, top: 810, display: 'flex', justifyContent: 'center', gap: 27}}>
        {[
          {label: 'MASK', at: maskAt},
          {label: 'HASH', at: hashAt},
          {label: 'TOKENIZE', at: tokenizeAt},
          {label: 'REMOVE', at: removeAt},
        ].map(({label, at}) => <div key={label} style={{padding: '20px 33px', borderRadius: 18, border: '1px solid #ffae66', background: '#342419', color: '#ffd4aa', fontSize: 27, fontWeight: 900, opacity: enterProgress(frame, fps, at)}}>{label}</div>)}
      </div> : null}
    </div>

  </SceneShell>;
};

export const BusinessRulesScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.businessRules;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const clockAt = 8860 - cue.startFrame;
  const mascotAt = 8960 - cue.startFrame;
  const cardsEnter = enterProgress(frame, fps, localCue(0));
  const cardsExit = interpolate(frame, [localCue(1) - seconds(1.2), localCue(1) - seconds(0.2)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const cardsOpacity = cardsEnter * cardsExit;
  const clockEnter = enterProgress(frame, fps, clockAt);
  const clockToMascotStart = mascotAt;
  const clockToMascotEnd = mascotAt + seconds(0.9);
  const clockOpacity = clockEnter * interpolate(frame, [clockToMascotStart, clockToMascotEnd], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const mascotOpacity = interpolate(frame, [clockToMascotStart, clockToMascotEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const mascotMove = interpolate(frame, [localCue(1), localCue(2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const businessBubble = enterProgress(frame, fps, localCue(2));
  const connectorMain = interpolate(frame, [localCue(3), localCue(3) + seconds(0.45)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const connectorTrunk = interpolate(frame, [localCue(3) + seconds(0.45), localCue(3) + seconds(0.95)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstBranch = interpolate(frame, [localCue(3) + seconds(0.95), localCue(3) + seconds(1.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const secondBranch = interpolate(frame, [localCue(3) + seconds(2.5), localCue(3) + seconds(2.85)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstCheck = enterProgress(frame, fps, localCue(3) + seconds(1.3));
  const secondCheck = enterProgress(frame, fps, localCue(3) + seconds(2.85));
  const review = enterProgress(frame, fps, localCue(4));

  return <SceneShell duration={BUSINESS_RULES_DURATION} heading="" accent={theme.governance}>
    <div>
      {cardsOpacity > 0 ? <div style={{position: 'absolute', inset: 0, opacity: cardsOpacity}}>
        <Surface accent="#b487ff" style={{position: 'absolute', left: 120, top: 450, width: 430, height: 180, display: 'grid', placeItems: 'center', padding: '0 36px', color: '#f0e8ff', fontSize: 34 * BUSINESS_RULE_FONT_SCALE, lineHeight: 1.15, fontWeight: 850, textAlign: 'center', translate: `${(1 - cardsEnter) * -24}px 0`}}>
          Business Requirement
        </Surface>
        <Surface accent="#69b7ff" style={{position: 'absolute', right: 120, top: 450, width: 430, height: 180, display: 'grid', placeItems: 'center', padding: '0 36px', color: '#d8ecff', fontSize: 34 * BUSINESS_RULE_FONT_SCALE, lineHeight: 1.15, fontWeight: 850, textAlign: 'center', translate: `${(1 - cardsEnter) * 24}px 0`}}>
          Executable Rule
        </Surface>
      </div> : null}

      {clockOpacity > 0 ? <div style={{position: 'absolute', left: 760, top: 332, width: 400, height: 416, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: clockOpacity}}>
        <div style={{position: 'relative', width: 250, height: 250, borderRadius: '50%', border: '8px solid #b487ff', background: '#111d33', boxSizing: 'border-box'}}>
          <div style={{position: 'absolute', left: '50%', top: 24, width: 6, height: 19, borderRadius: 99, background: '#c5a8ff', translate: '-50% 0'}} />
          <div style={{position: 'absolute', left: '50%', bottom: 24, width: 6, height: 19, borderRadius: 99, background: '#c5a8ff', translate: '-50% 0'}} />
          <div style={{position: 'absolute', left: 24, top: '50%', width: 19, height: 6, borderRadius: 99, background: '#c5a8ff', translate: '0 -50%'}} />
          <div style={{position: 'absolute', right: 24, top: '50%', width: 19, height: 6, borderRadius: 99, background: '#c5a8ff', translate: '0 -50%'}} />
          <div style={{position: 'absolute', left: '50%', top: 62, width: 7, height: 70, borderRadius: 99, background: '#f3edff', transformOrigin: '50% 100%', rotate: '-18deg', translate: '-50% 0'}} />
          <div style={{position: 'absolute', left: '50%', top: 116, width: 76, height: 7, borderRadius: 99, background: '#72e6ad', transformOrigin: '0 50%', rotate: '24deg'}} />
          <div style={{position: 'absolute', left: '50%', top: '50%', width: 20, height: 20, borderRadius: '50%', background: '#72e6ad', translate: '-50% -50%'}} />
        </div>
        <div style={{marginTop: 34, color: '#e9ddff', fontSize: 27 * BUSINESS_RULE_FONT_SCALE, lineHeight: 1.2, fontWeight: 820, textAlign: 'center'}}>
          Time to translate requirements into code
        </div>
      </div> : null}

      {mascotOpacity > 0 ? <div style={{position: 'absolute', left: 105, top: 505, zIndex: 3, width: 320, height: 320, opacity: mascotOpacity, translate: `${interpolate(mascotMove, [0, 1], [695, 0])}px ${interpolate(mascotMove, [0, 1], [-165, 0])}px`, scale: interpolate(mascotMove, [0, 1], [0.94, 1])}}>
        <MascotArtwork pose="coding" />
      </div> : null}

      {businessBubble > 0 ? <SpeechBubble accent="#b487ff" eyebrow="Business rule requirement" fontScale={BUSINESS_RULE_FONT_SCALE} style={{left: 430, top: 175, width: 1260, height: 195, opacity: businessBubble}}>&ldquo;Every completed order must have a delivery date, and it cannot be earlier than the order date.&rdquo;</SpeechBubble> : null}

      {connectorMain > 0 ? <svg aria-hidden="true" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', zIndex: 1, filter: 'drop-shadow(0 0 7px #b487ff88)'}}>
        <path d="M420 617 H455" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorMain} />
        <path d="M455 617 V492" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorTrunk} />
        <path d="M455 617 V685" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorTrunk} />
        <path d="M455 492 H499" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - firstBranch} />
        <path d="M455 685 H499" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - secondBranch} />
        <circle cx="497" cy="492" r="5" fill="#d8c9ff" opacity={interpolate(firstBranch, [0.82, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        <circle cx="497" cy="685" r="5" fill="#d8c9ff" opacity={interpolate(secondBranch, [0.82, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      </svg> : null}

      {firstCheck > 0 ? <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 415, width: 1235, height: 155, padding: '22px 28px', opacity: firstCheck, translate: `${(1 - firstCheck) * 24}px 0`, zIndex: 2}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{fontSize: 17 * BUSINESS_RULE_FONT_SCALE, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.3}}>CHECK 1</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 20 * BUSINESS_RULE_FONT_SCALE, color: '#d8c9ff'}}>conditional_completeness</div></div>
        <div style={{marginTop: 20, borderRadius: 12, padding: '15px 20px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 24 * BUSINESS_RULE_FONT_SCALE, color: '#f1ebff'}}>status = &apos;Completed&apos; → delivery_date IS NOT NULL</div>
      </Surface> : null}

      {secondCheck > 0 ? <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 590, width: 1235, height: 190, padding: '22px 28px', opacity: secondCheck, translate: `${(1 - secondCheck) * 24}px 0`, zIndex: 2}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{fontSize: 17 * BUSINESS_RULE_FONT_SCALE, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.3}}>CHECK 2</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 20 * BUSINESS_RULE_FONT_SCALE, color: '#d8c9ff'}}>custom_expression · PySpark</div></div>
        <div style={{marginTop: 17, borderRadius: 12, padding: '14px 20px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 20 * BUSINESS_RULE_FONT_SCALE, lineHeight: 1.45, color: '#f1ebff'}}><div>(F.col(&quot;status&quot;) != &quot;Completed&quot;) |</div><div>(F.col(&quot;delivery_date&quot;) &gt;= F.col(&quot;order_date&quot;))</div></div>
      </Surface> : null}

      {review > 0 ? <div style={{position: 'absolute', left: 785, top: 810, width: 620, padding: '17px 24px', borderRadius: 15, background: '#153c2e', border: '2px solid #55bd89', boxSizing: 'border-box', textAlign: 'center', color: '#baffd8', fontSize: 21 * BUSINESS_RULE_FONT_SCALE, fontWeight: 900, letterSpacing: 1.1, opacity: review, translate: `0 ${(1 - review) * 15}px`}}>✓ HUMAN REVIEWED &amp; APPROVED</div> : null}
    </div>
  </SceneShell>;
};

export const BigPictureScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.bigPicture;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const openingTransitionStart = localCue(1) - seconds(1.6);
  const openingTransitionEnd = localCue(1) + seconds(0.25);
  const sideEnter = enterProgress(frame, fps, seconds(0.35));
  const contractEnter = enterProgress(frame, fps, 10180 - cue.startFrame);
  const contractArrowEnd = interpolate(contractEnter, [0, 1], [24, 626], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const openingOpacity = interpolate(frame, [openingTransitionStart, openingTransitionEnd], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const contractCarry = interpolate(frame, [openingTransitionStart, openingTransitionEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const sourceAt = 380;
  const sourceToReadStart = sourceAt;
  const sourceToReadEnd = sourceAt + seconds(0.9);
  const readToTransformStart = localCue(2) - seconds(1.1);
  const transformToWriteStart = localCue(3) - seconds(1.1);
  const writeToOutputStart = localCue(4) - seconds(1.1);
  const source = enterProgress(frame, fps, sourceAt);
  const read = enterProgress(frame, fps, localCue(1));
  const transform = enterProgress(frame, fps, localCue(2));
  const write = enterProgress(frame, fps, localCue(3));
  const output = enterProgress(frame, fps, localCue(4));
  const sourceToRead = interpolate(frame, [sourceToReadStart, sourceToReadEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const readToTransform = interpolate(frame, [readToTransformStart, localCue(2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const transformToWrite = interpolate(frame, [transformToWriteStart, localCue(3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const writeToOutput = interpolate(frame, [writeToOutputStart, localCue(4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const masking = interpolate(frame, [localCue(7) + seconds(1.8), localCue(7) + seconds(3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const results = enterProgress(frame, fps, localCue(7) + seconds(4.2));
  const violation = enterProgress(frame, fps, localCue(8));
  const connectorOpacity = (start: number) => interpolate(frame, [start - seconds(0.2), start], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <SceneShell duration={BIG_PICTURE_DURATION} heading="" accent="#72e6ad">
    {openingOpacity > 0 ? <div style={{position: 'absolute', inset: 0, opacity: openingOpacity}}>
      <div style={{position: 'absolute', left: 245, top: 382, width: 320, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: sideEnter, translate: `${(1 - sideEnter) * -28}px 0`}}>
        <DataGovernanceIcon />
        <div style={{marginTop: 26, color: '#e9ddff', fontSize: 31, fontWeight: 850}}>Data Governance</div>
      </div>

      <div style={{position: 'absolute', right: 245, top: 382, width: 320, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: sideEnter, translate: `${(1 - sideEnter) * 28}px 0`}}>
        <DataEngineeringIcon />
        <div style={{marginTop: 26, color: '#d8ecff', fontSize: 31, fontWeight: 850}}>Data Engineering</div>
      </div>

      <div style={{position: 'absolute', left: 635, top: 414, width: 650, height: 80, opacity: contractEnter}}>
        <svg aria-hidden="true" width="650" height="80" viewBox="0 0 650 80">
          <line x1="24" y1="40" x2={contractArrowEnd} y2="40" stroke="#72e6ad" strokeWidth="7" strokeLinecap="round" />
          <path d={`M${contractArrowEnd - 23} 26 ${contractArrowEnd + 1} 40 ${contractArrowEnd - 23} 54Z`} fill="#69b7ff" opacity={contractEnter} />
        </svg>
      </div>
    </div> : null}

    {contractEnter > 0 ? <div style={{position: 'absolute', left: interpolate(contractCarry, [0, 1], [780, 235]), top: 105, zIndex: 3, width: 360, color: '#baffd8', fontSize: 30, fontWeight: 900, letterSpacing: 0.3, textAlign: 'center', opacity: contractEnter, translate: `0 ${interpolate(contractCarry, [0, 1], [430, 0])}px`, scale: interpolate(contractCarry, [0, 1], [1.18, 1])}}>
      <div style={{height: 3, margin: '0 74px 14px', borderRadius: 99, background: '#72e6ad'}} />
      Data Contract
    </div> : null}

    {contractCarry > 0 ? <div style={{position: 'absolute', left: interpolate(contractCarry, [0, 1], [780, 1325]), top: 105, zIndex: 3, width: 360, color: '#baffd8', fontSize: 30, fontWeight: 900, letterSpacing: 0.3, textAlign: 'center', opacity: contractEnter * contractCarry, translate: `0 ${interpolate(contractCarry, [0, 1], [430, 0])}px`, scale: interpolate(contractCarry, [0, 1], [1.18, 1])}}>
      <div style={{height: 3, margin: '0 74px 14px', borderRadius: 99, background: '#72e6ad'}} />
      Data Contract
    </div> : null}

    <PipelinePattern
      top={VALIDATION_LAYOUT.pipelineTop}
      read={read}
      transform={transform}
      write={write}
      firstLink={readToTransform}
      secondLink={transformToWrite}
      linkColor={FLOW_COLOR}
      firstLinkOpacity={connectorOpacity(readToTransformStart)}
      secondLinkOpacity={connectorOpacity(transformToWriteStart)}
      writeDetail="Sensitive-data treatment + governed checks"
    />

    <AnimatedDataFlow style={{zIndex: 0}}>
      <AnimatedFlowPath
        id="source-to-read"
        d={`M${VALIDATION_LAYOUT.readCenter} ${VALIDATION_LAYOUT.tableTop} V${VALIDATION_LAYOUT.pipelineTop + PIPELINE_LAYOUT.cardHeight}`}
        progress={sourceToRead}
        color={FLOW_COLOR}
        opacity={connectorOpacity(sourceToReadStart + seconds(0.2))}
      />
      <AnimatedFlowPath
        id="write-to-output"
        d={`M${VALIDATION_LAYOUT.writeCenter} ${VALIDATION_LAYOUT.pipelineTop + PIPELINE_LAYOUT.cardHeight} V${VALIDATION_LAYOUT.tableTop}`}
        progress={writeToOutput}
        color={FLOW_COLOR}
        opacity={connectorOpacity(writeToOutputStart)}
      />
    </AnimatedDataFlow>

    {source > 0 ? <Surface accent="#69b7ff" style={{position: 'absolute', left: VALIDATION_LAYOUT.rawLeft, top: VALIDATION_LAYOUT.tableTop, width: VALIDATION_LAYOUT.tableWidth, height: VALIDATION_LAYOUT.tableHeight, padding: '20px 24px', opacity: source, translate: `0 ${(1 - source) * 18}px`}}>
      <div style={{fontSize: 17, fontWeight: 900, color: '#8fc9ff', letterSpacing: 1.5}}>RAW SOURCE</div>
      <div style={{display: 'grid', gridTemplateColumns: '100px 155px 1fr 1.2fr', gap: 10, marginTop: 17, color: '#8fa7bf', fontSize: 21, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76'}}>person_nric</div><div>order_datetime</div><div>modified_datetime</div></div>
      {BIG_PICTURE_ROWS.map((row) => <div key={row.id} style={{display: 'grid', gridTemplateColumns: '100px 155px 1fr 1.2fr', gap: 10, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 27}}><div>{row.id}</div><div style={{color: '#ffbd76'}}>{row.nric}</div><div>{row.order}</div><div>{row.modified}</div></div>)}
    </Surface> : null}

    {output > 0 ? <Surface accent="#72e6ad" style={{position: 'absolute', left: VALIDATION_LAYOUT.outputLeft, top: VALIDATION_LAYOUT.tableTop, width: VALIDATION_LAYOUT.tableWidth, height: VALIDATION_LAYOUT.tableHeight, padding: '20px 24px', opacity: output, translate: `0 ${(1 - output) * 18}px`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><div style={{fontSize: 17, fontWeight: 900, color: '#72e6ad', letterSpacing: 1.5}}>GOVERNED OUTPUT</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 13, color: '#cfc3ef'}}>VALIDATION RESULT · modified_datetime &gt;= order_datetime</div></div>
      <div style={{display: 'grid', gridTemplateColumns: '90px 150px 1fr 1.25fr 88px', gap: 8, marginTop: 17, color: '#8fa7bf', fontSize: 20, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76', background: '#5d351f99', borderRadius: 7, padding: '3px 8px'}}>person_nric</div><div>order_datetime</div><div>modified_datetime</div><div>result</div></div>
      {BIG_PICTURE_ROWS.map((row, index) => <div key={`output-${row.id}`} style={{position: 'relative', display: 'grid', gridTemplateColumns: '90px 150px 1fr 1.25fr 88px', gap: 8, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', borderRadius: 8, background: index === 1 ? `rgba(109, 40, 49, ${violation * 0.48})` : 'transparent', fontFamily: 'ui-monospace, monospace', fontSize: 26}}><div>{row.id}</div><div style={{alignSelf: 'stretch', display: 'flex', alignItems: 'center', color: '#ffbd76', position: 'relative', background: `rgba(93, 53, 31, ${0.38 + masking * 0.42})`, borderRadius: 8, padding: '0 8px'}}><span style={{opacity: 1 - masking}}>{row.nric}</span><span style={{position: 'absolute', left: 8, opacity: masking}}>{row.maskedNric}</span></div><div>{row.order}</div><div style={{color: index === 1 ? '#ff9c8c' : '#dcecff'}}>{row.modified}</div><div style={{opacity: results, color: row.color, fontWeight: 900}}>{row.result}</div></div>)}
    </Surface> : null}
  </SceneShell>;
};

export const PromotionScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.promotion;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const devEnter = enterProgress(frame, fps, seconds(0.4));
  const nodeLabels = ['00 Env Config', '02 Pipeline', 'Data Contract'];
  const nodePositions = [480, 800, 1120];
  const nodeDelays = [localCue(2), localCue(3), localCue(4)];
  const connectorSegments = [
    {left: 418, width: 62, delay: localCue(0)},
    {left: 740, width: 60, delay: localCue(2) + seconds(0.65)},
    {left: 1060, width: 60, delay: localCue(3) + seconds(0.65)},
    {left: 1380, width: 112, delay: localCue(4) + seconds(0.65)},
  ];
  const productionEnter = enterProgress(frame, fps, localCue(6));
  const sentenceEnter = enterProgress(frame, fps, 180);
  const pulseTravel = interpolate(frame, [localCue(5), localCue(6)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const pulseOpacity = interpolate(
    frame,
    [localCue(5) - seconds(0.25), localCue(5), localCue(6), localCue(6) + seconds(0.35)],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return <AbsoluteFill style={{
    opacity: sceneOpacity(frame, PROMOTION_DURATION),
    color: theme.text,
    fontFamily: font,
  }}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 54%, #12365099 0%, #07101f00 58%)'}} />

    <div style={{
      position: 'absolute', top: 132, left: 240, right: 240,
      color: '#f7f9fd', fontSize: 52, fontWeight: 850, letterSpacing: -0.7,
      lineHeight: 1.15, textAlign: 'center', opacity: sentenceEnter,
      translate: `0 ${(1 - sentenceEnter) * 16}px`,
    }}>
      The data pipeline is promoted from Development to Production.
    </div>

    {connectorSegments.map(({left, width, delay}) => {
      const progress = interpolate(frame, [delay, delay + seconds(0.65)], [0, 1], {
        extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
      });
      if (progress <= 0) return null;

      return <div key={left} style={{
        position: 'absolute', left, top: 538, width, height: 4, borderRadius: 99,
        background: FLOW_COLOR, boxShadow: `0 0 18px ${FLOW_COLOR}99`, opacity: progress,
        scale: `${progress} 1`, transformOrigin: 'left center',
      }}>
        <div style={{
          position: 'absolute', right: -1, top: -7, width: 0, height: 0,
          borderTop: '9px solid transparent', borderBottom: '9px solid transparent',
          borderLeft: `13px solid ${FLOW_COLOR}`,
        }} />
      </div>;
    })}

    {pulseOpacity > 0 ? <div aria-hidden="true" style={{
      position: 'absolute', left: 420 + pulseTravel * 1058, top: 529, zIndex: 1,
      width: 22, height: 22, borderRadius: '50%', background: '#c7fff8',
      boxShadow: `0 0 10px #ffffff, 0 0 28px ${FLOW_COLOR}`, opacity: pulseOpacity,
    }} /> : null}

    {devEnter > 0 ? <div style={{
      position: 'absolute', left: 88, top: 350, zIndex: 2, width: 340, height: 430,
      opacity: devEnter, translate: `${(1 - devEnter) * -32}px 0`,
    }}><MascotArtwork pose="dev" shadow="drop-shadow(0 20px 34px #0009) drop-shadow(0 0 18px #ff8a2844)" /></div> : null}

    {nodeLabels.map((label, index) => {
      const progress = enterProgress(frame, fps, nodeDelays[index]);
      if (progress <= 0) return null;

      return <div key={label} style={{
        position: 'absolute', left: nodePositions[index], top: 465, zIndex: 2,
        width: 260, height: 150, boxSizing: 'border-box', display: 'flex',
        alignItems: 'center', justifyContent: 'center', padding: '0 28px', borderRadius: 24,
        border: `2px solid ${FLOW_COLOR}99`, background: 'linear-gradient(145deg, #15304a, #0b192c)',
        boxShadow: `0 20px 44px #0008, inset 0 1px 0 #ffffff18, 0 0 22px ${FLOW_COLOR}18`,
        color: '#eefcfb', fontSize: 29, fontWeight: 850, lineHeight: 1.15,
        textAlign: 'center', opacity: progress, translate: `0 ${(1 - progress) * 20}px`, scale: progress,
      }}>
        {label}
      </div>;
    })}

    {productionEnter > 0 ? <div style={{
      position: 'absolute', left: 1492, top: 350, zIndex: 2, width: 340, height: 430,
      opacity: productionEnter, translate: `${(1 - productionEnter) * 32}px 0`,
    }}><MascotArtwork pose="prod" shadow="drop-shadow(0 20px 34px #0009) drop-shadow(0 0 18px #38d99144)" /></div> : null}
  </AbsoluteFill>;
};

export const ClosingScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.closing;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const brandEnter = enterProgress(frame, fps, seconds(0.5));
  const plugIn = localCue(1);
  const governanceIn = localCue(2);
  const collaborationIn = localCue(3);
  const documentationIn = localCue(6);
  const demoIn = localCue(7);
  const narrationEnd = cue.endFrame - cue.startFrame;
  const teamFlashStart = 140;
  const teamFade = interpolate(frame, [plugIn, plugIn + seconds(0.35)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const governanceTeamAt = 172;
  const businessTeamAt = 200;
  const triangleCloseAt = 228;
  const engineerToGovernance = interpolate(frame, [teamFlashStart, governanceTeamAt], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const governanceToBusiness = interpolate(frame, [governanceTeamAt, businessTeamAt], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const businessToEngineer = interpolate(frame, [businessTeamAt, triangleCloseAt], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const teamTriangle = [
    {label: 'Data Engineers', accent: '#69b7ff', left: 700, top: 250, at: teamFlashStart},
    {label: 'Data Governance', accent: '#b487ff', left: 270, top: 720, at: governanceTeamAt},
    {label: 'Business Users', accent: '#ffae66', left: 1130, top: 720, at: businessTeamAt},
  ] as const;
  const documentationEnter = enterProgress(frame, fps, documentationIn);
  const demoEnter = enterProgress(frame, fps, demoIn);
  const plugFlash = interpolate(frame, [plugIn, plugIn + seconds(0.25), governanceIn - seconds(0.25), governanceIn], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const governanceFlash = interpolate(frame, [governanceIn, governanceIn + seconds(0.25), collaborationIn - seconds(0.25), collaborationIn], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const collaborateFlash = interpolate(frame, [470, 478, 500, 512], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const standardsFlash = interpolate(frame, [610, 618, 640, 652], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const highQualityFlash = interpolate(frame, [720, 728, 772, 784], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const trustworthyFlash = interpolate(frame, [740, 748, 792, 804], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const dataFoundationFlash = interpolate(frame, [835, 843, 873, 885], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const dataAgentFlash = interpolate(frame, [940, 948, 960, 972], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const machineLearningFlash = interpolate(frame, [970, 978, 990, 1002], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const applicationsFlash = interpolate(frame, [1015, 1023, 1035, 1047], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const fadeOpacity = interpolate(frame, [narrationEnd, CLOSING_DURATION - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <AbsoluteFill style={{color: theme.text, fontFamily: font}}>
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
      {teamFade > 0 ? <svg aria-hidden="true" width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, zIndex: 0, opacity: teamFade}}>
        <path d="M960 330 530 700" pathLength="1" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - engineerToGovernance} />
        <path d="M530 700 1390 700" pathLength="1" fill="none" stroke="#ffae66" strokeWidth="5" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - governanceToBusiness} />
        <path d="M1390 700 960 330" pathLength="1" fill="none" stroke="#69b7ff" strokeWidth="5" strokeLinecap="round" strokeDasharray="1" strokeDashoffset={1 - businessToEngineer} />
      </svg> : null}

      <div style={{position: 'absolute', inset: 0, zIndex: 2, display: 'grid', placeItems: 'center', opacity: brandEnter}}>
        <div style={{fontSize: VIDEO_CONFIG.text.hero, lineHeight: 1, fontWeight: 840, letterSpacing: -8, whiteSpace: 'nowrap'}}>
          <span style={{color: theme.production}}>Fabric</span>
          <span style={{color: '#fff'}}>Ops</span>
        </div>
      </div>

      {collaborateFlash > 0 ? <div style={{position: 'absolute', left: 230, top: 448, zIndex: 3, width: 430, color: '#c5a8ff', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: collaborateFlash, rotate: '-18deg', scale: 0.9 + collaborateFlash * 0.1, translate: `${(1 - collaborateFlash) * -22}px 0`, textShadow: '0 0 24px #9e74ff99'}}>
        Collaborate
      </div> : null}

      {standardsFlash > 0 ? <div style={{position: 'absolute', right: 190, top: 448, zIndex: 3, width: 470, color: '#8fc9ff', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: standardsFlash, rotate: '18deg', scale: 0.9 + standardsFlash * 0.1, translate: `${(1 - standardsFlash) * 22}px 0`, textShadow: '0 0 24px #69b7ff99'}}>
        Data Standards
      </div> : null}

      {plugFlash > 0 ? <div style={{position: 'absolute', left: 120, top: 448, zIndex: 3, width: 650, color: '#72e6ad', fontSize: 48, fontWeight: 900, letterSpacing: 1.8, opacity: plugFlash, rotate: '-18deg', scale: 0.9 + plugFlash * 0.1, translate: `${(1 - plugFlash) * -22}px 0`, textShadow: '0 0 24px #38d99199'}}>
        Plug-and-Play Data Pipelines
      </div> : null}

      {governanceFlash > 0 ? <div style={{position: 'absolute', right: 150, top: 448, zIndex: 3, width: 570, color: '#c5a8ff', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: governanceFlash, rotate: '18deg', scale: 0.9 + governanceFlash * 0.1, translate: `${(1 - governanceFlash) * 22}px 0`, textShadow: '0 0 24px #9e74ff99'}}>
        Governance as Code
      </div> : null}

      {highQualityFlash > 0 ? <div style={{position: 'absolute', left: 190, top: 448, zIndex: 3, width: 470, color: '#72e6ad', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: highQualityFlash, rotate: '-18deg', scale: 0.9 + highQualityFlash * 0.1, translate: `${(1 - highQualityFlash) * -22}px 0`, textShadow: '0 0 24px #38d99199'}}>
        High Quality
      </div> : null}

      {trustworthyFlash > 0 ? <div style={{position: 'absolute', right: 190, top: 448, zIndex: 3, width: 470, color: '#c5a8ff', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: trustworthyFlash, rotate: '18deg', scale: 0.9 + trustworthyFlash * 0.1, translate: `${(1 - trustworthyFlash) * 22}px 0`, textShadow: '0 0 24px #9e74ff99'}}>
        Trustworthy
      </div> : null}

      {dataFoundationFlash > 0 ? <div style={{position: 'absolute', left: 110, top: 448, zIndex: 3, width: 700, color: '#72e6ad', fontSize: 50, fontWeight: 900, letterSpacing: 1.8, opacity: dataFoundationFlash, rotate: '-18deg', scale: 0.9 + dataFoundationFlash * 0.1, translate: `${(1 - dataFoundationFlash) * -22}px 0`, textShadow: '0 0 24px #38d99199'}}>
        Lay the Data Foundation
      </div> : null}

      {dataAgentFlash > 0 ? <div style={{position: 'absolute', left: 260, top: 300, zIndex: 3, width: 410, color: '#8fc9ff', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: dataAgentFlash, rotate: '-11deg', scale: 0.9 + dataAgentFlash * 0.1, translate: `${(1 - dataAgentFlash) * -18}px ${(1 - dataAgentFlash) * -12}px`, textShadow: '0 0 24px #69b7ff99'}}>
        Data Agent
      </div> : null}

      {machineLearningFlash > 0 ? <div style={{position: 'absolute', right: 90, top: 790, zIndex: 3, width: 720, color: '#c5a8ff', fontSize: 48, fontWeight: 900, letterSpacing: 1.8, opacity: machineLearningFlash, rotate: '7deg', scale: 0.9 + machineLearningFlash * 0.1, translate: `${(1 - machineLearningFlash) * 22}px ${(1 - machineLearningFlash) * 14}px`, textShadow: '0 0 24px #9e74ff99'}}>
        Machine Learning Model
      </div> : null}

      {applicationsFlash > 0 ? <div style={{position: 'absolute', left: 170, top: 790, zIndex: 3, width: 470, color: '#ffbd76', fontSize: 54, fontWeight: 900, letterSpacing: 2.4, opacity: applicationsFlash, rotate: '-8deg', scale: 0.9 + applicationsFlash * 0.1, translate: `${(1 - applicationsFlash) * -20}px ${(1 - applicationsFlash) * 12}px`, textShadow: '0 0 24px #ffae6699'}}>
        Applications
      </div> : null}

      {teamFade > 0 ? teamTriangle.map(({label, accent, left, top, at}) => {
        const progress = enterProgress(frame, fps, at);
        const flash = interpolate(frame, [at, at + 6, at + 12], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
        if (progress <= 0) return null;

        return <div key={label} style={{position: 'absolute', left, top, zIndex: 3, width: 520, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 21, color: accent, fontSize: 46.5, fontWeight: 850, letterSpacing: 0.2, opacity: progress * teamFade, scale: 0.88 + progress * 0.12}}>
          <div aria-hidden="true" style={{width: 22.5, height: 22.5, borderRadius: '50%', background: accent, opacity: 0.65 + flash * 0.35, scale: 1 + flash * 0.75, boxShadow: `0 0 ${10 + flash * 28}px ${accent}`}} />
          {label}
        </div>;
      }) : null}

      {documentationEnter > 0 || demoEnter > 0 ? <div style={{position: 'absolute', top: 680, display: 'flex', alignItems: 'center', gap: 36}}>
        <div style={{minWidth: 495, padding: '29px 51px', borderRadius: 21, border: '3px solid #72e6ad', color: '#dfffee', fontSize: 42, fontWeight: 800, boxSizing: 'border-box', opacity: documentationEnter, translate: `0 ${(1 - documentationEnter) * 24}px`}}>Read the documentation</div>
        <div style={{minWidth: 375, padding: '29px 51px', borderRadius: 21, border: '3px solid #c5a8ff', color: '#f0e8ff', fontSize: 42, fontWeight: 800, boxSizing: 'border-box', opacity: demoEnter, translate: `0 ${(1 - demoEnter) * 24}px`}}>Guided Demo</div>
      </div> : null}
    </div>

    {fadeOpacity > 0 ? <AbsoluteFill style={{background: '#000', opacity: fadeOpacity}} /> : null}
  </AbsoluteFill>;
};
