import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {NARRATION_CUE_SHEET} from '../narrationCues';
import {font, theme} from '../theme';
import {GUIDED_SCENE_DURATIONS, seconds, VIDEO_CONFIG} from '../videoConfig';
import {AnimatedDataFlow, AnimatedFlowPath} from '../components/AnimatedDataFlow';

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

const Mascot = ({pose, x, y, size, delay}: {pose: MascotName; x: number; y: number; size: number; delay: number}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + seconds(0.6)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <Img src={mascotSrc(pose)} style={{
    position: 'absolute', left: x, top: y, width: size, height: size,
    objectFit: 'contain', opacity: progress, translate: `0 ${(1 - progress) * 24}px`,
    filter: 'drop-shadow(0 16px 26px #0008)',
  }} />;
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

const PipelinePattern = ({top, read, transform, write, firstLink, secondLink, linkColor, firstLinkOpacity = 1, secondLinkOpacity = 1, writeDetail}: {top: number; read: number; transform: number; write: number; firstLink: number; secondLink: number; linkColor?: string; firstLinkOpacity?: number; secondLinkOpacity?: number; writeDetail?: string}) => <>
  <AnimatedDataFlow style={{zIndex: 0}}>
    <AnimatedFlowPath id={`pipeline-read-${top}`} d={`M${PIPELINE_LAYOUT.left + PIPELINE_LAYOUT.cardWidth} ${top + PIPELINE_LAYOUT.cardHeight / 2} H${PIPELINE_LAYOUT.transformLeft}`} progress={firstLink} color={linkColor ?? '#52d6c6'} opacity={firstLinkOpacity} />
    <AnimatedFlowPath id={`pipeline-write-${top}`} d={`M${PIPELINE_LAYOUT.transformLeft + PIPELINE_LAYOUT.cardWidth} ${top + PIPELINE_LAYOUT.cardHeight / 2} H${PIPELINE_LAYOUT.writeLeft}`} progress={secondLink} color={linkColor ?? '#72e6ad'} opacity={secondLinkOpacity} />
  </AnimatedDataFlow>
  <div style={{position: 'absolute', left: PIPELINE_LAYOUT.left, top, display: 'flex', alignItems: 'center', gap: PIPELINE_LAYOUT.gap, zIndex: 1}}>
    <Surface accent="#69b7ff" style={{width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: read, translate: `0 ${(1 - read) * 24}px`}}>
      <div style={{fontSize: 20, color: '#8fc9ff', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED READ</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 34, color: '#d8ecff', fontWeight: 800, marginTop: 46}}>orchestrate_read()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 38}}>Governed source</div>
    </Surface>
    <Surface accent="#52d6c6" style={{width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: transform, translate: `0 ${(1 - transform) * 24}px`}}>
      <div style={{fontSize: 20, color: '#7ae4d8', letterSpacing: 1.8, fontWeight: 850}}>YOUR LOGIC</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 39, color: '#f6fbff', fontWeight: 850, marginTop: 43}}>PySpark</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 34}}>Your transformation</div>
    </Surface>
    <Surface accent="#72e6ad" style={{width: PIPELINE_LAYOUT.cardWidth, height: PIPELINE_LAYOUT.cardHeight, padding: '34px 36px', opacity: write, translate: `0 ${(1 - write) * 24}px`}}>
      <div style={{fontSize: 20, color: '#72e6ad', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED WRITE</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 32, color: '#dcffec', fontWeight: 800, marginTop: 46}}>orchestrate_write()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: writeDetail ? 24 : 38}}>Governed target</div>
      {writeDetail ? <div style={{fontSize: 16, color: '#80cdb2', marginTop: 14, lineHeight: 1.25}}>{writeDetail}</div> : null}
    </Surface>
  </div>
</>;

const SpeechBubble = ({accent, eyebrow, children, style}: {accent: string; eyebrow: string; children: ReactNode; style: CSSProperties}) => <div style={{
  position: 'absolute', borderRadius: 18, border: `1px solid ${accent}99`, background: '#10243cf2',
  padding: '23px 30px', boxSizing: 'border-box', boxShadow: '0 14px 35px #0006', ...style,
}}>
  <div style={{fontSize: 18, fontWeight: 900, letterSpacing: 1.5, color: accent}}>{eyebrow}</div>
  <div style={{fontSize: 34, fontWeight: 780, lineHeight: 1.24, marginTop: 9, color: '#f3f7fc'}}>{children}</div>
  <div style={{position: 'absolute', left: -13, bottom: 31, width: 24, height: 24, background: '#10243c', borderLeft: `1px solid ${accent}99`, borderBottom: `1px solid ${accent}99`, rotate: '45deg'}} />
</div>;

export const DataEngineersScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.dataEngineers;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const introEnd = 5880 - cue.startFrame;
  const aiWritingEnd = 6200 - cue.startFrame;
  const introOpacity = interpolate(frame, [0, seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const taskExit = localCue(5);
  const inconsistencyAt = 6250 - cue.startFrame;
  const implementationsAt = localCue(7);
  const taskOpacity = interpolate(frame, [taskExit - seconds(0.35), taskExit + seconds(0.25)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const aiOpacity = interpolate(frame, [taskExit - seconds(0.15), taskExit + seconds(0.35), inconsistencyAt - seconds(0.35), inconsistencyAt + seconds(0.25)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const implementationOpacity = interpolate(frame, [inconsistencyAt - seconds(0.1), inconsistencyAt + seconds(0.45)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const misalignment = interpolate(frame, [implementationsAt, implementationsAt + seconds(0.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const tasks = [
    {label: 'Connect', detail: 'Data stores', at: localCue(1), accent: '#69b7ff'},
    {label: 'Resolve', detail: 'Paths', at: localCue(2), accent: '#52d6c6'},
    {label: 'Profile', detail: 'Profiling + EDA', at: localCue(3), accent: '#b487ff'},
    {label: 'Validate', detail: 'Quality checks', at: localCue(4), accent: '#ffae66'},
  ];
  const codeLines = [
    {width: 76, color: '#69b7ff'},
    {width: 54, color: '#52d6c6'},
    {width: 66, color: '#b487ff'},
    {width: 43, color: '#ffae66'},
  ];
  const implementations = [
    {engineer: 'Engineer A', context: 'Prompt A · Model 1', accent: '#69b7ff', widths: [76, 48, 64, 38], offset: -9, rotate: -0.65},
    {engineer: 'Engineer B', context: 'Prompt B · Model 2', accent: '#b487ff', widths: [48, 82, 56, 70], offset: 11, rotate: 0.55},
    {engineer: 'Engineer C', context: 'Prompt C · Model 3', accent: '#ff9c72', widths: [68, 42, 78, 51], offset: -5, rotate: -0.35},
  ];

  return <SceneShell duration={DATA_ENGINEERS_DURATION} heading="" accent={theme.engineering}>
    <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', textAlign: 'center', fontSize: 91, fontWeight: 900, letterSpacing: 1.5, color: '#f2f7fc', opacity: introOpacity, translate: `0 ${(1 - introOpacity) * 12}px`}}>Rewriting Boilerplate Code</div>

    <div style={{position: 'absolute', left: 140, right: 140, top: 405, display: 'flex', gap: 32, opacity: taskOpacity}}>
      {tasks.map(({label, detail, at, accent}) => {
        const progress = enterProgress(frame, fps, at);
        return <Surface key={label} accent={accent} style={{flex: 1, height: 196, padding: '38px 34px', opacity: progress, translate: `0 ${(1 - progress) * 16}px`}}>
          <div style={{width: 48, height: 5, borderRadius: 99, background: accent}} />
          <div style={{fontSize: 34, fontWeight: 850, color: '#f2f7fc', marginTop: 27}}>{label}</div>
          <div style={{fontSize: 21, color: '#9fb1c5', marginTop: 12}}>{detail}</div>
        </Surface>;
      })}
    </div>

    <Surface accent="#52d6c6" style={{position: 'absolute', left: 520, top: 320, width: 880, height: 390, padding: '46px 54px', opacity: aiOpacity, translate: `0 ${(1 - aiOpacity) * 12}px`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 27}}>
        <div style={{width: 78, height: 78, borderRadius: 22, display: 'grid', placeItems: 'center', background: '#123f45', border: '1px solid #52d6c688', color: '#a8fff4', fontFamily: 'ui-monospace, monospace', fontSize: 30, fontWeight: 900}}>&lt;/&gt;</div>
        <div>
          <div style={{fontSize: 23, fontWeight: 900, color: '#7ae4d8', letterSpacing: 1.8}}>AI-ASSISTED</div>
          <div style={{fontSize: 43, fontWeight: 850, color: '#f2f9fb', marginTop: 7}}>Faster coding</div>
        </div>
      </div>
      <div style={{marginTop: 43, display: 'grid', gap: 18}}>
        {codeLines.map(({width, color}, index) => {
          const lineProgress = interpolate(frame, [taskExit + index * seconds(0.2), aiWritingEnd - (codeLines.length - 1 - index) * seconds(0.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          return <div key={width} style={{height: 11, width: `${width * lineProgress}%`, marginLeft: index === 0 ? 0 : 44, borderRadius: 99, background: color, opacity: 0.38 + lineProgress * 0.62}} />;
        })}
      </div>
    </Surface>

    <div style={{position: 'absolute', left: 220, right: 220, top: 350, display: 'flex', gap: 58, opacity: implementationOpacity}}>
      {implementations.map(({engineer, context, accent, widths, offset, rotate}, index) => {
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
    </div>
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
  const read = enterProgress(frame, fps, readAt);
  const transform = enterProgress(frame, fps, transformAt);
  const write = enterProgress(frame, fps, writeAt);
  const firstLink = interpolate(frame, [transformAt - seconds(0.4), transformAt + seconds(0.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secondLink = interpolate(frame, [transformAt - seconds(0.2), transformAt + seconds(0.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ferryStart = 0;
  const ferryEnd = 6900 - cue.startFrame;
  const ferry = interpolate(frame, [ferryStart, ferryEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const ferryOpacity = interpolate(frame, [ferryStart, ferryEnd - seconds(0.35), ferryEnd], [1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <SceneShell duration={REPEATABLE_PIPELINE_DURATION} heading="" accent={theme.engineering}>
      <PipelinePattern top={300} read={read} transform={transform} write={write} firstLink={firstLink} secondLink={secondLink} />
      <Img src={mascotSrc('carrying')} style={{
        position: 'absolute',
        left: 260 + ferry * 1265,
        top: 575,
        width: 220,
        height: 220,
        objectFit: 'contain',
        opacity: ferryOpacity,
        filter: 'drop-shadow(0 16px 26px #0008)',
        translate: "-12.1px -245px"
      }} />
      <Reveal at={localCue(4)} y={16}>
        <div style={{position: 'absolute', left: 150, right: 150, top: 800, display: 'flex', justifyContent: 'center', gap: 36}}>
          {[
            {label: '02A · Full Refresh', at: localCue(4)},
            {label: '02B · Incremental', at: localCue(5)},
            {label: '02C · SCD1 / SCD2', at: localCue(6)},
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
  const policyOpacity = interpolate(frame, [policyAt, policyAt + seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const enforcedOpacity = interpolate(frame, [enforcedAt, enforcedAt + seconds(0.4), introEnd - seconds(0.4), introEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sensitiveBubble = enterProgress(frame, fps, introEnd);
  const scan = enterProgress(frame, fps, localCue(1));
  const treatment = enterProgress(frame, fps, localCue(2));
  const redact = interpolate(frame, [localCue(2), localCue(2) + seconds(0.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const identityRows = [
    {before: 'S1234567D', after: 'S****567D'},
    {before: 'T7654321F', after: 'T****321F'},
    {before: 'F2468135N', after: 'F****135N'},
  ];
  return <SceneShell duration={SENSITIVE_DATA_DURATION} heading="" accent={theme.governance}>
    <div>
      <div style={{position: 'absolute', left: 340, right: 340, top: 455, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{fontSize: 82, fontWeight: 900, letterSpacing: 4, color: '#ffbe82', opacity: policyOpacity, translate: `0 ${(1 - policyOpacity) * 12}px`}}>POLICY</div>
        <div style={{fontSize: 82, fontWeight: 900, letterSpacing: 4, color: '#c5a8ff', opacity: enforcedOpacity, translate: `0 ${(1 - enforcedOpacity) * 12}px`}}>ENFORCED</div>
      </div>
      <SpeechBubble accent="#ffae66" eyebrow="Sensitive data requirement" style={{left: 555, top: 55, width: 810, height: 160, opacity: sensitiveBubble, scale: 1.5, transformOrigin: 'top center'}}>&ldquo;This column is sensitive.&rdquo;</SpeechBubble>
      <Mascot pose="scanning" x={125} y={485} size={315} delay={localCue(1)} />
      <Surface accent="#ffae66" style={{position: 'absolute', left: 480, top: 395, width: 850, height: 390, padding: '28px 34px', opacity: scan}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 28, color: '#ffcf9f', fontWeight: 850}}>person_nric</div><div style={{padding: '9px 18px', borderRadius: 10, background: '#5d351f', color: '#ffd2a4', fontSize: 18, fontWeight: 900, opacity: treatment}}>MASKED</div></div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', marginTop: 30, color: '#8fa7bf', fontSize: 17, fontWeight: 850}}><div>BEFORE</div><div /><div>AFTER</div></div>
        {identityRows.map(({before, after}) => <div key={before} style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', alignItems: 'center', height: 72, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 29}}><div>{before}</div><div style={{color: '#66809b', textAlign: 'center'}}>→</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - redact}}>{before}</span><span style={{position: 'absolute', left: 0, opacity: redact}}>{after}</span></div></div>)}
      </Surface>
      <Mascot pose="masking" x={1390} y={485} size={315} delay={localCue(2)} />
      <div style={{position: 'absolute', left: 425, top: 605, width: 55, height: 5, borderRadius: 99, background: '#ffae66', scale: `${scan} 1`, transformOrigin: 'left'}} />
      <div style={{position: 'absolute', left: 1330, top: 605, width: 60, height: 5, borderRadius: 99, background: '#ffae66', scale: `${treatment} 1`, transformOrigin: 'left'}} />
      <div style={{position: 'absolute', left: 430, right: 430, top: 810, display: 'flex', justifyContent: 'center', gap: 27}}>
        {[
          {label: 'MASK', at: localCue(2)},
          {label: 'HASH', at: localCue(3)},
          {label: 'TOKENIZE', at: localCue(4)},
          {label: 'REMOVE', at: localCue(4) + seconds(1.2)},
        ].map(({label, at}) => <div key={label} style={{padding: '20px 33px', borderRadius: 18, border: '1px solid #ffae66', background: '#342419', color: '#ffd4aa', fontSize: 27, fontWeight: 900, opacity: enterProgress(frame, fps, at)}}>{label}</div>)}
      </div>
    </div>

  </SceneShell>;
};

export const BusinessRulesScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.businessRules;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const businessBubble = enterProgress(frame, fps, localCue(2));
  const connectorMain = interpolate(frame, [localCue(3), localCue(3) + seconds(0.45)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const connectorTrunk = interpolate(frame, [localCue(3) + seconds(0.45), localCue(3) + seconds(0.95)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstBranch = interpolate(frame, [localCue(3) + seconds(0.95), localCue(3) + seconds(1.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const secondBranch = interpolate(frame, [localCue(3) + seconds(2.5), localCue(3) + seconds(2.85)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstCheck = enterProgress(frame, fps, localCue(3) + seconds(1.3));
  const secondCheck = enterProgress(frame, fps, localCue(3) + seconds(2.85));
  const review = enterProgress(frame, fps, localCue(4));
  const engineerReview = enterProgress(frame, fps, localCue(5));

  return <SceneShell duration={BUSINESS_RULES_DURATION} heading="" accent={theme.governance}>
    <div>
      <SpeechBubble accent="#b487ff" eyebrow="Business rule requirement" style={{left: 430, top: 175, width: 1260, height: 195, opacity: businessBubble}}>&ldquo;Every completed order must have a delivery date, and it cannot be earlier than the order date.&rdquo;</SpeechBubble>
      <Mascot pose="coding" x={105} y={505} size={320} delay={localCue(1)} />

      <svg aria-hidden="true" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', zIndex: 1, filter: 'drop-shadow(0 0 7px #b487ff88)'}}>
        <path d="M420 617 H455" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorMain} />
        <path d="M455 617 V492" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorTrunk} />
        <path d="M455 617 V685" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - connectorTrunk} />
        <path d="M455 492 H499" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - firstBranch} />
        <path d="M455 685 H499" fill="none" stroke="#b487ff" strokeWidth="5" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - secondBranch} />
        <circle cx="497" cy="492" r="5" fill="#d8c9ff" opacity={interpolate(firstBranch, [0.82, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        <circle cx="497" cy="685" r="5" fill="#d8c9ff" opacity={interpolate(secondBranch, [0.82, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      </svg>

      <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 415, width: 1235, height: 155, padding: '22px 28px', opacity: firstCheck, translate: `${(1 - firstCheck) * 24}px 0`, zIndex: 2}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{fontSize: 17, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.3}}>CHECK 1</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 20, color: '#d8c9ff'}}>conditional_completeness</div></div>
        <div style={{marginTop: 20, borderRadius: 12, padding: '15px 20px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 24, color: '#f1ebff'}}>status = &apos;Completed&apos; → delivery_date IS NOT NULL</div>
      </Surface>

      <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 590, width: 1235, height: 190, padding: '22px 28px', opacity: secondCheck, translate: `${(1 - secondCheck) * 24}px 0`, zIndex: 2}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{fontSize: 17, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.3}}>CHECK 2</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 20, color: '#d8c9ff'}}>custom_expression · PySpark</div></div>
        <div style={{marginTop: 17, borderRadius: 12, padding: '14px 20px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 20, lineHeight: 1.45, color: '#f1ebff'}}><div>(F.col(&quot;status&quot;) != &quot;Completed&quot;) |</div><div>(F.col(&quot;delivery_date&quot;) &gt;= F.col(&quot;order_date&quot;))</div></div>
      </Surface>

      <div style={{position: 'absolute', left: 785, top: 810, width: 620, padding: '17px 24px', borderRadius: 15, background: '#153c2e', border: '2px solid #55bd89', boxSizing: 'border-box', textAlign: 'center', color: '#baffd8', fontSize: 21, fontWeight: 900, letterSpacing: 1.1, opacity: review, translate: `0 ${(1 - review) * 15}px`}}>✓ HUMAN REVIEWED &amp; APPROVED</div>
      <div style={{position: 'absolute', left: 810, top: 892, width: 570, textAlign: 'center', color: '#c5a8ff', fontSize: 18, fontWeight: 850, letterSpacing: 0.8, opacity: engineerReview}}>Complex rules route to Engineering review</div>
    </div>
  </SceneShell>;
};

export const BigPictureScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = NARRATION_CUE_SHEET.bigPicture;
  const localCue = (index: number) => cue.keyPhrases[index].triggerFrame - cue.startFrame;
  const sourceToReadStart = localCue(1) - seconds(1.1);
  const readToTransformStart = localCue(2) - seconds(1.1);
  const transformToWriteStart = localCue(3) - seconds(1.1);
  const writeToOutputStart = localCue(4) - seconds(1.1);
  const source = enterProgress(frame, fps, localCue(0));
  const read = enterProgress(frame, fps, localCue(1));
  const transform = enterProgress(frame, fps, localCue(2));
  const write = enterProgress(frame, fps, localCue(3));
  const output = enterProgress(frame, fps, localCue(4));
  const sourceToRead = interpolate(frame, [sourceToReadStart, localCue(1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const readToTransform = interpolate(frame, [readToTransformStart, localCue(2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const transformToWrite = interpolate(frame, [transformToWriteStart, localCue(3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const writeToOutput = interpolate(frame, [writeToOutputStart, localCue(4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const masking = interpolate(frame, [localCue(7) + seconds(1.8), localCue(7) + seconds(3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const results = enterProgress(frame, fps, localCue(7) + seconds(4.2));
  const violation = enterProgress(frame, fps, localCue(8));
  const connectorOpacity = (start: number) => interpolate(frame, [start - seconds(0.2), start], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rows = [
    {id: '00007', customer: 'C001', order: '09:00', modified: '09:18', result: 'PASS', color: '#72e6ad'},
    {id: '00008', customer: 'C002', order: '09:00', modified: '08:00', result: 'FAIL', color: '#ff756d'},
  ];
  return <SceneShell duration={BIG_PICTURE_DURATION} heading="" accent="#72e6ad">
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
        opacity={connectorOpacity(sourceToReadStart)}
      />
      <AnimatedFlowPath
        id="write-to-output"
        d={`M${VALIDATION_LAYOUT.writeCenter} ${VALIDATION_LAYOUT.pipelineTop + PIPELINE_LAYOUT.cardHeight} V${VALIDATION_LAYOUT.tableTop}`}
        progress={writeToOutput}
        color={FLOW_COLOR}
        opacity={connectorOpacity(writeToOutputStart)}
      />
    </AnimatedDataFlow>

    <Surface accent="#69b7ff" style={{position: 'absolute', left: VALIDATION_LAYOUT.rawLeft, top: VALIDATION_LAYOUT.tableTop, width: VALIDATION_LAYOUT.tableWidth, height: VALIDATION_LAYOUT.tableHeight, padding: '20px 24px', opacity: source, translate: `0 ${(1 - source) * 18}px`}}>
      <div style={{fontSize: 17, fontWeight: 900, color: '#8fc9ff', letterSpacing: 1.5}}>RAW SOURCE</div>
      <div style={{display: 'grid', gridTemplateColumns: '80px 115px 1fr 1fr', gap: 10, marginTop: 17, color: '#8fa7bf', fontSize: 14, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76'}}>customer_id</div><div>order_datetime</div><div>modified_datetime</div></div>
      {rows.map((row) => <div key={row.id} style={{display: 'grid', gridTemplateColumns: '80px 115px 1fr 1fr', gap: 10, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 18}}><div>{row.id}</div><div style={{color: '#ffbd76'}}>{row.customer}</div><div>{row.order}</div><div>{row.modified}</div></div>)}
    </Surface>

    <Surface accent="#72e6ad" style={{position: 'absolute', left: VALIDATION_LAYOUT.outputLeft, top: VALIDATION_LAYOUT.tableTop, width: VALIDATION_LAYOUT.tableWidth, height: VALIDATION_LAYOUT.tableHeight, padding: '20px 24px', opacity: output, translate: `0 ${(1 - output) * 18}px`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><div style={{fontSize: 17, fontWeight: 900, color: '#72e6ad', letterSpacing: 1.5}}>GOVERNED OUTPUT</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 13, color: '#cfc3ef'}}>VALIDATION RESULT · modified_datetime &gt;= order_datetime</div></div>
      <div style={{display: 'grid', gridTemplateColumns: '76px 100px 1fr 1fr 70px', gap: 8, marginTop: 17, color: '#8fa7bf', fontSize: 13, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76'}}>customer_id</div><div>order_datetime</div><div>modified_datetime</div><div>result</div></div>
      {rows.map((row, index) => <div key={`output-${row.id}`} style={{position: 'relative', display: 'grid', gridTemplateColumns: '76px 100px 1fr 1fr 70px', gap: 8, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', borderRadius: 8, background: index === 1 ? `rgba(109, 40, 49, ${violation * 0.48})` : 'transparent', fontFamily: 'ui-monospace, monospace', fontSize: 17}}><div>{row.id}</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - masking}}>{row.customer}</span><span style={{position: 'absolute', left: 0, opacity: masking}}>C•••</span></div><div>{row.order}</div><div style={{color: index === 1 ? '#ff9c8c' : '#dcecff'}}>{row.modified}</div><div style={{opacity: results, color: row.color, fontWeight: 900}}>{row.result}</div></div>)}
    </Surface>
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
  const sentenceEnter = enterProgress(frame, fps, 0);
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

    <div aria-hidden="true" style={{
      position: 'absolute', left: 420 + pulseTravel * 1058, top: 529, zIndex: 1,
      width: 22, height: 22, borderRadius: '50%', background: '#c7fff8',
      boxShadow: `0 0 10px #ffffff, 0 0 28px ${FLOW_COLOR}`, opacity: pulseOpacity,
    }} />

    <Img src={mascotSrc('dev')} style={{
      position: 'absolute', left: 88, top: 350, zIndex: 2, width: 340, height: 430,
      objectFit: 'contain', opacity: devEnter, translate: `${(1 - devEnter) * -32}px 0`,
      filter: 'drop-shadow(0 20px 34px #0009) drop-shadow(0 0 18px #ff8a2844)',
    }} />

    {nodeLabels.map((label, index) => {
      const progress = enterProgress(frame, fps, nodeDelays[index]);
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

    <Img src={mascotSrc('prod')} style={{
      position: 'absolute', left: 1492, top: 350, zIndex: 2, width: 340, height: 430,
      objectFit: 'contain', opacity: productionEnter, translate: `${(1 - productionEnter) * 32}px 0`,
      filter: 'drop-shadow(0 20px 34px #0009) drop-shadow(0 0 18px #38d99144)',
    }} />
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
  const documentationEnter = enterProgress(frame, fps, documentationIn);
  const demoEnter = enterProgress(frame, fps, demoIn);
  return <AbsoluteFill style={{color: theme.text, fontFamily: font}}>
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
      <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: brandEnter}}>
        <div style={{fontSize: VIDEO_CONFIG.text.hero, lineHeight: 1, fontWeight: 840, letterSpacing: -8, whiteSpace: 'nowrap'}}>
          <span style={{color: theme.production}}>Fabric</span>
          <span style={{color: '#fff'}}>Ops</span>
        </div>
      </div>

      <div style={{position: 'absolute', top: 674, left: 0, right: 0, fontSize: 44, lineHeight: 1.1, fontWeight: 720, letterSpacing: -0.8, color: '#dcecff', opacity: interpolate(frame, [plugIn, plugIn + seconds(0.35), governanceIn - seconds(0.25), governanceIn], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}}>
        Plug-and-Play Data Pipelines
      </div>

      <div style={{position: 'absolute', top: 674, left: 0, right: 0, fontSize: 44, lineHeight: 1.1, fontWeight: 720, letterSpacing: -0.8, color: '#c5a8ff', opacity: interpolate(frame, [governanceIn, governanceIn + seconds(0.35), collaborationIn - seconds(0.25), collaborationIn], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}}>
        Governance-as-Code
      </div>

      <div style={{position: 'absolute', top: 674, left: 0, right: 0, fontSize: 44, lineHeight: 1.1, fontWeight: 720, letterSpacing: -0.8, color: '#72e6ad', opacity: interpolate(frame, [collaborationIn, collaborationIn + seconds(0.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)})}}>
        One Consistent Framework
      </div>

      <div style={{position: 'absolute', top: 776, display: 'flex', alignItems: 'center', gap: 24}}>
        <div style={{minWidth: 330, padding: '19px 34px', borderRadius: 14, border: '2px solid #72e6ad', color: '#dfffee', fontSize: 28, fontWeight: 800, boxSizing: 'border-box', opacity: documentationEnter, translate: `0 ${(1 - documentationEnter) * 16}px`}}>Read the documentation</div>
        <div style={{minWidth: 250, padding: '19px 34px', borderRadius: 14, border: '2px solid #c5a8ff', color: '#f0e8ff', fontSize: 28, fontWeight: 800, boxSizing: 'border-box', opacity: demoEnter, translate: `0 ${(1 - demoEnter) * 16}px`}}>Guided Demo</div>
      </div>
    </div>

    <AbsoluteFill style={{background: '#000', opacity: interpolate(frame, [narrationEnd, CLOSING_DURATION - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}} />
  </AbsoluteFill>;
};
