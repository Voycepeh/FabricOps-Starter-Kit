import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {font, theme} from '../theme';
import {GUIDED_SCENE_DURATIONS, seconds, VIDEO_CONFIG} from '../videoConfig';
import {AnimatedDataFlow, AnimatedFlowPath} from '../components/AnimatedDataFlow';

const {
  engineering: ENGINEERING_DURATION,
  governance: GOVERNANCE_DURATION,
  validation: VALIDATION_DURATION,
  activation: ACTIVATION_DURATION,
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
    background: 'radial-gradient(circle at 48% 38%, #17375d 0%, #0b1930 44%, #060d19 86%)',
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

export const EngineeringScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const read = enterProgress(frame, fps, seconds(1.2));
  const transform = enterProgress(frame, fps, seconds(2.2));
  const write = enterProgress(frame, fps, seconds(3.2));
  const firstLink = interpolate(frame, [seconds(2), seconds(3.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secondLink = interpolate(frame, [seconds(3), seconds(4.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ferry = interpolate(frame, [seconds(4.4), seconds(8.1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const ferryOpacity = interpolate(frame, [seconds(4.2), seconds(4.6), seconds(8), seconds(8.4)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <SceneShell duration={ENGINEERING_DURATION} heading="One reusable pipeline pattern" accent={theme.engineering}>
    <PipelinePattern top={300} read={read} transform={transform} write={write} firstLink={firstLink} secondLink={secondLink} />
    <Img src={mascotSrc('carrying')} style={{
      position: 'absolute', left: 260 + ferry * 1265, top: 575, width: 220, height: 220,
      objectFit: 'contain', opacity: ferryOpacity, filter: 'drop-shadow(0 16px 26px #0008)',
    }} />
    <Reveal at={seconds(8.2)} y={16}>
      <div style={{position: 'absolute', left: 210, right: 210, top: 815, display: 'flex', justifyContent: 'center', gap: 28}}>
        {['02A · Full Refresh', '02B · Incremental', '02C · SCD1 / SCD2'].map((label) => <div key={label} style={{padding: '17px 31px', borderRadius: 16, background: '#122d49', border: '1px solid #4d759c', fontSize: 24, fontWeight: 820, color: '#d5e9ff'}}>{label}</div>)}
      </div>
    </Reveal>
  </SceneShell>;
};

export const GovernanceScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sensitiveBubble = enterProgress(frame, fps, seconds(0.5));
  const sensitivePhase = interpolate(frame, [0, seconds(0.35), seconds(7.1), seconds(7.6)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scan = enterProgress(frame, fps, seconds(1.7));
  const treatment = enterProgress(frame, fps, seconds(3.7));
  const redact = interpolate(frame, [seconds(4.4), seconds(5.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const businessBubble = enterProgress(frame, fps, seconds(8.2));
  const businessPhase = interpolate(frame, [seconds(7.8), seconds(8.2), seconds(19.3), seconds(19.8)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const connectorMain = interpolate(frame, [seconds(9.8), seconds(10.25)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const connectorTrunk = interpolate(frame, [seconds(10.25), seconds(10.75)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstBranch = interpolate(frame, [seconds(10.75), seconds(11.1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const secondBranch = interpolate(frame, [seconds(13.15), seconds(13.5)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const firstCheck = enterProgress(frame, fps, seconds(11.1));
  const secondCheck = enterProgress(frame, fps, seconds(13.5));
  const review = enterProgress(frame, fps, seconds(15.7));
  return <SceneShell duration={GOVERNANCE_DURATION} heading="Inject governance as code into your pipelines" accent={theme.governance}>
    <div style={{opacity: sensitivePhase}}>
      <SpeechBubble accent="#ffae66" eyebrow="Sensitive data requirement" style={{left: 555, top: 185, width: 810, height: 160, opacity: sensitiveBubble}}>&ldquo;This column is sensitive.&rdquo;</SpeechBubble>
      <Mascot pose="scanning" x={125} y={485} size={315} delay={seconds(1.7)} />
      <Surface accent="#ffae66" style={{position: 'absolute', left: 480, top: 395, width: 850, height: 390, padding: '28px 34px', opacity: scan}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 28, color: '#ffcf9f', fontWeight: 850}}>customer_id</div><div style={{padding: '9px 18px', borderRadius: 10, background: '#5d351f', color: '#ffd2a4', fontSize: 18, fontWeight: 900, opacity: treatment}}>MASKED</div></div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', marginTop: 30, color: '#8fa7bf', fontSize: 17, fontWeight: 850}}><div>BEFORE</div><div /><div>AFTER</div></div>
        {['C001', 'C002', 'C003'].map((value) => <div key={value} style={{display: 'grid', gridTemplateColumns: '1fr 90px 1fr', alignItems: 'center', height: 72, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 29}}><div>{value}</div><div style={{color: '#66809b', textAlign: 'center'}}>→</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - redact}}>{value}</span><span style={{position: 'absolute', left: 0, opacity: redact}}>C•••</span></div></div>)}
      </Surface>
      <Mascot pose="masking" x={1390} y={485} size={315} delay={seconds(3.7)} />
      <div style={{position: 'absolute', left: 425, top: 605, width: 55, height: 5, borderRadius: 99, background: '#ffae66', scale: `${scan} 1`, transformOrigin: 'left'}} />
      <div style={{position: 'absolute', left: 1330, top: 605, width: 60, height: 5, borderRadius: 99, background: '#ffae66', scale: `${treatment} 1`, transformOrigin: 'left'}} />
    </div>

    <div style={{opacity: businessPhase}}>
      <SpeechBubble accent="#b487ff" eyebrow="Business rule requirement" style={{left: 430, top: 175, width: 1260, height: 195, opacity: businessBubble}}>&ldquo;Every completed order must have a delivery date, and it cannot be earlier than the order date.&rdquo;</SpeechBubble>
      <Mascot pose="coding" x={105} y={505} size={320} delay={seconds(9.8)} />

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
    </div>
  </SceneShell>;
};

export const ValidationScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sourceToReadStart = seconds(2);
  const readToTransformStart = seconds(3.25);
  const transformToWriteStart = seconds(4.5);
  const writeToOutputStart = seconds(5.8);
  const source = enterProgress(frame, fps, seconds(0.5));
  const read = enterProgress(frame, fps, seconds(3));
  const transform = enterProgress(frame, fps, seconds(4.25));
  const write = enterProgress(frame, fps, seconds(5.5));
  const output = enterProgress(frame, fps, seconds(6.8));
  const sourceToRead = interpolate(frame, [sourceToReadStart, seconds(3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const readToTransform = interpolate(frame, [readToTransformStart, seconds(4.25)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const transformToWrite = interpolate(frame, [transformToWriteStart, seconds(5.5)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const writeToOutput = interpolate(frame, [writeToOutputStart, seconds(6.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const masking = interpolate(frame, [seconds(7.15), seconds(7.75)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const results = enterProgress(frame, fps, seconds(7.9));
  const violation = enterProgress(frame, fps, seconds(8.55));
  const connectorOpacity = (start: number) => interpolate(frame, [start - seconds(0.2), start], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rows = [
    {id: '00007', customer: 'C001', order: '09:00', modified: '09:18', result: 'PASS', color: '#72e6ad'},
    {id: '00008', customer: 'C002', order: '09:00', modified: '08:00', result: 'FAIL', color: '#ff756d'},
  ];
  return <SceneShell duration={VALIDATION_DURATION} heading="One reusable pipeline pattern" accent="#72e6ad">
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

export const ActivationScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const frameAt = (value: number) => Math.round(value * fps);
  const developmentEnter = interpolate(frame, [frameAt(0.5), frameAt(1.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const developmentShift = interpolate(frame, [frameAt(4.4), frameAt(5.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const developmentFocus = interpolate(frame, [frameAt(5.8), frameAt(6.4), frameAt(9.6), frameAt(10.2)], [1, 0, 0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const developmentHighlight = interpolate(frame, [frameAt(1.4), frameAt(3.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const validationOpacity = interpolate(frame, [frameAt(3.7), frameAt(4.1), frameAt(5.5), frameAt(5.9)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const promotionProgress = interpolate(frame, [frameAt(4.8), frameAt(6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const promotionPhaseOpacity = interpolate(frame, [frameAt(4.6), frameAt(5), frameAt(6), frameAt(6.2)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const productionEnter = interpolate(frame, [frameAt(6.2), frameAt(7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const productionShift = interpolate(frame, [frameAt(9.4), frameAt(10.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const productionHighlight = interpolate(frame, [frameAt(7), frameAt(9.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const comparisonOpacity = interpolate(frame, [frameAt(9.8), frameAt(10.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <SceneShell
    duration={ACTIVATION_DURATION}
    eyebrow="DEVELOPMENT + PRODUCTION · STEPS 5–6"
    heading="Same pipeline pattern. Different environment."
    subheading="Build and validate in Development. Promote the same engineering stack to Production."
    accent={theme.production}
  >
    <div style={{position: 'absolute', left: 344, top: 236, width: 428, height: 760, opacity: developmentEnter * developmentFocus, translate: `${(1 - developmentShift) * 408}px ${(1 - developmentEnter) * 20}px`}}>
      <Img src={staticFile('mascots/robot-dev-cycle.png')} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
      <div aria-hidden="true" style={{position: 'absolute', left: 0, right: 0, top: -52 + developmentHighlight * 780, height: 52, background: 'linear-gradient(180deg, transparent, #ffad3344, transparent)', opacity: interpolate(frame, [frameAt(1.4), frameAt(1.8), frameAt(3.4), frameAt(3.8)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
    </div>

    <div style={{position: 'absolute', left: 1148, top: 236, width: 428, height: 760, opacity: productionEnter, translate: `${(1 - productionShift) * -408}px ${(1 - productionEnter) * 20}px`}}>
      <Img src={staticFile('mascots/robot-prod-cycle.png')} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
      <div aria-hidden="true" style={{position: 'absolute', left: 0, right: 0, top: -52 + productionHighlight * 780, height: 52, background: 'linear-gradient(180deg, transparent, #72e6ad44, transparent)', opacity: interpolate(frame, [frameAt(7), frameAt(7.4), frameAt(8.9), frameAt(9.3)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
    </div>

    <div style={{position: 'absolute', left: 1188, top: 278, padding: '10px 16px', borderRadius: 8, border: '1px solid #72e6ad', background: '#0d2630', color: '#baffd8', fontSize: 20, fontWeight: 900, opacity: validationOpacity}}>✓ Development validated</div>

    <div style={{position: 'absolute', left: 812, top: 584, width: 296, height: 72, opacity: Math.max(promotionPhaseOpacity, comparisonOpacity)}}>
      <div style={{position: 'absolute', left: 0, top: 38, width: 282, height: 4, borderRadius: 4, background: '#29415d'}}>
        <div style={{width: `${promotionProgress * 100}%`, height: '100%', borderRadius: 4, background: '#5fe1d0'}} />
      </div>
      <div style={{position: 'absolute', right: 0, top: 30, width: 0, height: 0, borderTop: '10px solid transparent', borderBottom: '10px solid transparent', borderLeft: `14px solid ${promotionProgress > 0.94 ? '#5fe1d0' : '#29415d'}`}} />
      <div style={{position: 'absolute', left: 86, top: 0, width: 124, padding: '7px 0', borderRadius: 6, background: '#0b1930', border: '1px solid #5fe1d0', color: '#bffdf5', textAlign: 'center', fontSize: 18, fontWeight: 900, letterSpacing: 0.5}}>Promote 1:1</div>
    </div>
  </SceneShell>;
};

export const ClosingScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <AbsoluteFill style={{color: theme.text, fontFamily: font, background: 'radial-gradient(circle at 50% 43%, #153850 0%, #081524 48%, #03070d 100%)'}}>
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
      <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: interpolate(frame, [0, Math.round(0.65 * fps)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)})}}>
        <div style={{fontSize: VIDEO_CONFIG.text.hero, lineHeight: 1, fontWeight: 840, letterSpacing: -8, whiteSpace: 'nowrap'}}>
          <span style={{color: theme.production}}>Fabric</span>
          <span style={{color: '#fff'}}>Ops</span>
        </div>
      </div>

      <div style={{position: 'absolute', top: 674, left: 0, right: 0, fontSize: 44, lineHeight: 1.1, fontWeight: 720, letterSpacing: -0.8, color: '#dcecff', opacity: interpolate(frame, [Math.round(0.45 * fps), Math.round(0.65 * fps), Math.round(2.15 * fps), Math.round(2.35 * fps)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}}>
        Plug-and-Play Data Pipelines
      </div>

      <div style={{position: 'absolute', top: 674, left: 0, right: 0, fontSize: 44, lineHeight: 1.1, fontWeight: 720, letterSpacing: -0.8, color: '#c5a8ff', opacity: interpolate(frame, [Math.round(2.35 * fps), Math.round(2.55 * fps), Math.round(4.15 * fps), Math.round(4.35 * fps)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}}>
        Governance-as-Code
      </div>

      <div style={{position: 'absolute', top: 776, display: 'flex', alignItems: 'center', gap: 24, opacity: interpolate(frame, [Math.round(4.35 * fps), Math.round(4.75 * fps)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)})}}>
        <div style={{minWidth: 330, padding: '19px 34px', borderRadius: 14, border: '2px solid #72e6ad', color: '#dfffee', fontSize: 28, fontWeight: 800, boxSizing: 'border-box'}}>How FabricOps works</div>
        <div style={{minWidth: 250, padding: '19px 34px', borderRadius: 14, border: '2px solid #c5a8ff', color: '#f0e8ff', fontSize: 28, fontWeight: 800, boxSizing: 'border-box'}}>Guided Demo</div>
      </div>
    </div>

    <AbsoluteFill style={{background: '#000', opacity: interpolate(frame, [Math.round(7 * fps), CLOSING_DURATION - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)})}} />
  </AbsoluteFill>;
};
