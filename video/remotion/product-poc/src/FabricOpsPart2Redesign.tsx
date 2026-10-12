import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';
import {mascotSrc, type MascotName} from './mascotAssets';

const seconds = (value: number) => Math.round(value * 30);

export const ENGINEERING_DURATION = seconds(13);
export const GOVERNANCE_DURATION = seconds(20);
export const VALIDATION_DURATION = seconds(12);
export const ACTIVATION_DURATION = seconds(13);
export const CLOSING_DURATION = seconds(9);

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

const StageArrow = ({left, top, width, progress, color}: {left: number; top: number; width: number; progress: number; color: string}) => <div style={{position: 'absolute', left, top, width, height: 6, borderRadius: 99, background: '#29415d'}}>
  <div style={{width: `${progress * 100}%`, height: '100%', borderRadius: 99, background: color, boxShadow: `0 0 18px ${color}88`}} />
  <div style={{position: 'absolute', right: -2, top: -7, width: 0, height: 0, borderTop: '10px solid transparent', borderBottom: '10px solid transparent', borderLeft: `14px solid ${progress > 0.95 ? color : '#29415d'}`}} />
</div>;

const PipelinePattern = ({top, read, transform, write, firstLink, secondLink}: {top: number; read: number; transform: number; write: number; firstLink: number; secondLink: number}) => <>
  <div style={{position: 'absolute', left: 200, top, display: 'flex', alignItems: 'center', gap: 115}}>
    <Surface accent="#69b7ff" style={{width: 430, height: 280, padding: '34px 36px', opacity: read, translate: `0 ${(1 - read) * 24}px`}}>
      <div style={{fontSize: 20, color: '#8fc9ff', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED READ</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 34, color: '#d8ecff', fontWeight: 800, marginTop: 46}}>orchestrate_read()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 38}}>Governed source</div>
    </Surface>
    <Surface accent="#52d6c6" style={{width: 430, height: 280, padding: '34px 36px', opacity: transform, translate: `0 ${(1 - transform) * 24}px`}}>
      <div style={{fontSize: 20, color: '#7ae4d8', letterSpacing: 1.8, fontWeight: 850}}>YOUR LOGIC</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 39, color: '#f6fbff', fontWeight: 850, marginTop: 43}}>PySpark</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 34}}>Your transformation</div>
    </Surface>
    <Surface accent="#72e6ad" style={{width: 430, height: 280, padding: '34px 36px', opacity: write, translate: `0 ${(1 - write) * 24}px`}}>
      <div style={{fontSize: 20, color: '#72e6ad', letterSpacing: 1.8, fontWeight: 850}}>GOVERNED WRITE</div>
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 32, color: '#dcffec', fontWeight: 800, marginTop: 46}}>orchestrate_write()</div>
      <div style={{fontSize: 24, color: '#aebed3', marginTop: 38}}>Governed target</div>
    </Surface>
  </div>
  <StageArrow left={630} top={top + 138} width={112} progress={firstLink} color="#52d6c6" />
  <StageArrow left={1175} top={top + 138} width={112} progress={secondLink} color="#72e6ad" />
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
  const coding = enterProgress(frame, fps, seconds(9.8));
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
      <div style={{position: 'absolute', left: 420, top: 617, width: 55, height: 5, borderRadius: 99, background: '#b487ff', scale: `${coding} 1`, transformOrigin: 'left'}} />

      <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 415, width: 1235, height: 155, padding: '22px 28px', opacity: firstCheck, translate: `${(1 - firstCheck) * 24}px 0`}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{fontSize: 17, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.3}}>CHECK 1</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 20, color: '#d8c9ff'}}>conditional_completeness</div></div>
        <div style={{marginTop: 20, borderRadius: 12, padding: '15px 20px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 24, color: '#f1ebff'}}>status = &apos;Completed&apos; → delivery_date IS NOT NULL</div>
      </Surface>

      <Surface accent="#b487ff" style={{position: 'absolute', left: 475, top: 590, width: 1235, height: 190, padding: '22px 28px', opacity: secondCheck, translate: `${(1 - secondCheck) * 24}px 0`}}>
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
  const read = enterProgress(frame, fps, seconds(0.4));
  const transform = enterProgress(frame, fps, seconds(0.9));
  const write = enterProgress(frame, fps, seconds(1.4));
  const firstLink = interpolate(frame, [seconds(0.8), seconds(1.7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secondLink = interpolate(frame, [seconds(1.3), seconds(2.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const source = enterProgress(frame, fps, seconds(2.3));
  const travel = interpolate(frame, [seconds(3.8), seconds(6.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const travelOpacity = interpolate(frame, [seconds(3.5), seconds(3.9), seconds(6.1), seconds(6.5)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const contract = enterProgress(frame, fps, seconds(5.6));
  const output = enterProgress(frame, fps, seconds(6.3));
  const masking = interpolate(frame, [seconds(7), seconds(7.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const results = enterProgress(frame, fps, seconds(8.1));
  const violation = enterProgress(frame, fps, seconds(9.2));
  const rows = [
    {id: '00007', customer: 'C001', order: '09:00', modified: '09:18', result: 'PASS', color: '#72e6ad'},
    {id: '00008', customer: 'C002', order: '09:00', modified: '08:00', result: 'FAIL', color: '#ff756d'},
  ];
  return <SceneShell duration={VALIDATION_DURATION} heading="One reusable pipeline pattern" accent="#72e6ad">
    <PipelinePattern top={200} read={read} transform={transform} write={write} firstLink={firstLink} secondLink={secondLink} />

    <div style={{position: 'absolute', left: 1360, top: 174, width: 360, padding: '10px 16px', borderRadius: 12, background: '#292145', border: '1px solid #8e6aca', boxSizing: 'border-box', textAlign: 'center', opacity: contract, zIndex: 3}}><span style={{fontSize: 16, color: '#c5a8ff', fontWeight: 900}}>DATA CONTRACT</span><span style={{fontSize: 15, color: '#eee7ff', marginLeft: 12}}>MASK + VALIDATE</span></div>
    <div style={{position: 'absolute', left: 1538, top: 220, width: 4, height: 18, borderRadius: 4, background: '#b487ff', opacity: contract}} />

    <div style={{position: 'absolute', left: 414, top: 480, width: 4, height: 180, borderRadius: 4, background: '#69b7ff66', opacity: source}} />
    <Surface accent="#69b7ff" style={{position: 'absolute', left: 90, top: 660, width: 740, height: 226, padding: '20px 24px', opacity: source, translate: `0 ${(1 - source) * 18}px`}}>
      <div style={{fontSize: 17, fontWeight: 900, color: '#8fc9ff', letterSpacing: 1.5}}>RAW SOURCE</div>
      <div style={{display: 'grid', gridTemplateColumns: '90px 125px 1fr 1fr', gap: 12, marginTop: 17, color: '#8fa7bf', fontSize: 14, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76'}}>customer_id</div><div>order_datetime</div><div>modified_datetime</div></div>
      {rows.map((row) => <div key={row.id} style={{display: 'grid', gridTemplateColumns: '90px 125px 1fr 1fr', gap: 12, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 18}}><div>{row.id}</div><div style={{color: '#ffbd76'}}>{row.customer}</div><div>{row.order}</div><div>{row.modified}</div></div>)}
    </Surface>

    {rows.map((row, index) => <div key={`travel-${row.id}`} style={{position: 'absolute', left: 180, top: 535 + index * 52, width: 560, height: 40, borderRadius: 10, padding: '9px 16px', boxSizing: 'border-box', background: '#132d48', border: '1px solid #58799c', boxShadow: '0 10px 24px #0007', fontFamily: 'ui-monospace, monospace', fontSize: 17, color: '#dcecff', opacity: travelOpacity, translate: `${travel * 1000}px 0`, zIndex: 4}}>{row.id}&nbsp;&nbsp;|&nbsp;&nbsp;{row.customer}&nbsp;&nbsp;|&nbsp;&nbsp;{row.order}&nbsp;&nbsp;|&nbsp;&nbsp;{row.modified}</div>)}

    <div style={{position: 'absolute', left: 1503, top: 480, width: 4, height: 180, borderRadius: 4, background: '#72e6ad88', opacity: output}} />
    <Surface accent="#72e6ad" style={{position: 'absolute', left: 995, top: 660, width: 835, height: 226, padding: '20px 24px', opacity: output, translate: `0 ${(1 - output) * 18}px`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><div style={{fontSize: 17, fontWeight: 900, color: '#72e6ad', letterSpacing: 1.5}}>GOVERNED OUTPUT</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 15, color: '#cfc3ef'}}>modified_datetime &gt;= order_datetime</div></div>
      <div style={{display: 'grid', gridTemplateColumns: '82px 112px 1fr 1fr 80px', gap: 10, marginTop: 17, color: '#8fa7bf', fontSize: 13, fontWeight: 850}}><div>order_id</div><div style={{color: '#ffbd76'}}>customer_id</div><div>order_datetime</div><div>modified_datetime</div><div>result</div></div>
      {rows.map((row, index) => <div key={`output-${row.id}`} style={{position: 'relative', display: 'grid', gridTemplateColumns: '82px 112px 1fr 1fr 80px', gap: 10, alignItems: 'center', height: 58, borderTop: '1px solid #3a526d', borderRadius: 8, background: index === 1 ? `rgba(109, 40, 49, ${violation * 0.48})` : 'transparent', fontFamily: 'ui-monospace, monospace', fontSize: 18}}><div>{row.id}</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - masking}}>{row.customer}</span><span style={{position: 'absolute', left: 0, opacity: masking}}>C•••</span></div><div>{row.order}</div><div style={{color: index === 1 ? '#ff9c8c' : '#dcecff'}}>{row.modified}</div><div style={{opacity: results, color: row.color, fontWeight: 900}}>{row.result}</div>{index === 1 ? <div style={{position: 'absolute', right: 4, bottom: -21, color: '#ff9c8c', fontFamily: font, fontSize: 14, fontWeight: 850, opacity: violation}}>Rule violation</div> : null}</div>)}
    </Surface>
  </SceneShell>;
};

export const ActivationScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const lifecycle = enterProgress(frame, fps, seconds(1.1));
  const activation = enterProgress(frame, fps, seconds(3.7));
  const promotion = enterProgress(frame, fps, seconds(6.2));
  const production = enterProgress(frame, fps, seconds(8.1));
  const deployLine = interpolate(frame, [seconds(6.5), seconds(8.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <SceneShell duration={ACTIVATION_DURATION} eyebrow="ACTIVATION + PRODUCTION · STEPS 5–6" heading="Activate. Then promote." subheading="Contract approval and deployment stay distinct." accent={theme.production}>
    <Surface accent="#b487ff" style={{position: 'absolute', left: 115, top: 345, width: 780, height: 470, padding: '30px 34px', opacity: lifecycle}}>
      <div style={{fontSize: 21, letterSpacing: 1.5, fontWeight: 850, color: '#c5a8ff'}}>DATA CONTRACT LIFECYCLE</div>
      <div style={{display: 'flex', alignItems: 'center', marginTop: 60}}>
        {['Draft', 'Frozen', 'Validated', 'Activated'].map((label, index) => <div key={label} style={{display: 'flex', alignItems: 'center'}}>
          <div style={{width: 145, padding: '18px 10px', borderRadius: 15, textAlign: 'center', fontSize: 22, fontWeight: 850, color: index === 3 ? '#e8ddff' : '#c2cfdd', background: index === 3 ? '#49357c' : '#172d47', border: `1px solid ${index === 3 ? '#b487ff' : '#486079'}`}}>{label}</div>
          {index < 3 ? <div style={{fontSize: 31, color: '#69829e', margin: '0 10px'}}>→</div> : null}
        </div>)}
      </div>
      <div style={{opacity: activation, marginTop: 53, padding: '18px 20px', borderRadius: 14, background: '#241d3c', borderLeft: '5px solid #b487ff', fontSize: 23, fontWeight: 850}}>Activate the validated contract</div>
    </Surface>
    <Surface accent="#72e6ad" style={{position: 'absolute', left: 955, top: 345, width: 850, height: 470, padding: '30px 34px', opacity: promotion}}>
      <div style={{fontSize: 21, letterSpacing: 1.5, fontWeight: 850, color: '#72e6ad'}}>ENGINEERING PROMOTION</div>
      <div style={{position: 'relative', height: 210, marginTop: 20}}>
        <div style={{position: 'absolute', left: 55, top: 35, width: 225, textAlign: 'center'}}><div style={{fontSize: 22, color: '#8ecbff', fontWeight: 850}}>DEVELOPMENT</div></div>
        <div style={{position: 'absolute', left: 280, top: 85, width: 230, height: 6, borderRadius: 99, background: '#29415d'}}><div style={{height: '100%', width: `${deployLine * 100}%`, borderRadius: 99, background: '#72e6ad', boxShadow: '0 0 18px #72e6ad88'}} /></div>
        <div style={{position: 'absolute', right: 45, top: 35, width: 225, textAlign: 'center', opacity: production}}><div style={{fontSize: 22, color: '#72e6ad', fontWeight: 850}}>PRODUCTION</div></div>
        <Mascot pose="dev" x={75} y={112} size={150} delay={seconds(6.2)} />
        <Mascot pose="prod" x={590} y={112} size={150} delay={seconds(8.1)} />
      </div>
      <div style={{opacity: production, marginTop: 25, padding: '18px 20px', borderRadius: 14, background: '#12362a', borderLeft: '5px solid #72e6ad', fontSize: 23, fontWeight: 850}}>Promote the validated pipeline</div>
    </Surface>
    <Reveal at={seconds(10)} y={14}><div style={{position: 'absolute', left: 300, right: 300, top: 885, textAlign: 'center', fontSize: 26, color: '#d9e6f4', fontWeight: 820}}>Same governed pipeline. Production configuration.</div></Reveal>
  </SceneShell>;
};

export const ClosingScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const title = enterProgress(frame, fps, seconds(0.5));
  const support = enterProgress(frame, fps, seconds(1.8));
  const cta = enterProgress(frame, fps, seconds(3));
  return <AbsoluteFill style={{opacity: sceneOpacity(frame, CLOSING_DURATION), color: theme.text, fontFamily: font, background: 'radial-gradient(circle at 47% 44%, #17415b, #07101f 72%)'}}>
    <AbsoluteFill style={{opacity: 0.16, backgroundImage: 'linear-gradient(#7ae4d81c 1px, transparent 1px), linear-gradient(90deg, #7ae4d81c 1px, transparent 1px)', backgroundSize: '72px 72px'}} />
    <div style={{position: 'absolute', left: 150, top: 178, width: 1320, opacity: title, translate: `${(1 - title) * -30}px 0`}}>
      <div style={{fontSize: 24, letterSpacing: 2.5, fontWeight: 900, color: '#72e6ad'}}>FABRICOPS STARTER KIT</div>
      <div style={{fontSize: 82, lineHeight: 1.08, fontWeight: 950, marginTop: 34, letterSpacing: -2}}>Plug-and-Play Data Pipelines.</div>
      <div style={{fontSize: 82, lineHeight: 1.08, fontWeight: 950, color: '#c5a8ff', marginTop: 10, letterSpacing: -2}}>Governance-as-Code.</div>
      <div style={{fontSize: 31, color: '#b9c8d9', marginTop: 45, opacity: support}}>A faster, more consistent data foundation for the age of AI.</div>
    </div>
    <div style={{position: 'absolute', left: 150, top: 730, display: 'flex', alignItems: 'center', gap: 26, opacity: cta}}><div style={{padding: '21px 31px', borderRadius: 17, background: '#72e6ad', color: '#071a24', fontSize: 29, fontWeight: 920, boxShadow: '0 16px 45px #0007'}}>Explore How FabricOps Works</div><div style={{fontSize: 33, color: '#8fa6bd'}}>→</div><div style={{fontSize: 33, color: '#f4f8fc', fontWeight: 870}}>Guided Demo</div></div>
    <div style={{position: 'absolute', left: 154, top: 835, fontSize: 23, color: '#8fa6bd', opacity: cta}}>voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/</div>
    <Mascot pose="pointing" x={1450} y={560} size={360} delay={seconds(2.4)} />
  </AbsoluteFill>;
};
