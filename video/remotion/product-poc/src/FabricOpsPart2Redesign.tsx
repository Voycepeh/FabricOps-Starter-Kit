import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';
import {mascotSrc, type MascotName} from './mascotAssets';

const seconds = (value: number) => Math.round(value * 30);

export const ENGINEERING_DURATION = seconds(13);
export const GOVERNANCE_DURATION = seconds(16);
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
  padding: '17px 22px', boxSizing: 'border-box', boxShadow: '0 14px 35px #0006', ...style,
}}>
  <div style={{fontSize: 16, fontWeight: 900, letterSpacing: 1.5, color: accent}}>{eyebrow}</div>
  <div style={{fontSize: 23, fontWeight: 760, lineHeight: 1.3, marginTop: 7, color: '#f3f7fc'}}>{children}</div>
  <div style={{position: 'absolute', left: -13, bottom: 22, width: 24, height: 24, background: '#10243c', borderLeft: `1px solid ${accent}99`, borderBottom: `1px solid ${accent}99`, rotate: '45deg'}} />
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
  const human = enterProgress(frame, fps, seconds(0.5));
  const sensitiveBubble = enterProgress(frame, fps, seconds(0.9));
  const ruleBubble = enterProgress(frame, fps, seconds(1.5));
  const sensitivePhase = interpolate(frame, [seconds(2), seconds(2.5), seconds(7.1), seconds(7.8)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scan = enterProgress(frame, fps, seconds(2.4));
  const treatment = enterProgress(frame, fps, seconds(4.5));
  const redact = interpolate(frame, [seconds(5.1), seconds(6.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const businessPhase = interpolate(frame, [seconds(7.2), seconds(7.9), seconds(12.7), seconds(13.4)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const coding = enterProgress(frame, fps, seconds(7.8));
  const structuredRule = enterProgress(frame, fps, seconds(9));
  const structureCheck = enterProgress(frame, fps, seconds(10.8));
  const contract = enterProgress(frame, fps, seconds(13));
  const inputOpacity = interpolate(frame, [seconds(12.8), seconds(13.5)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <SceneShell duration={GOVERNANCE_DURATION} eyebrow="GOVERNANCE · STEP 3" heading="Governance becomes executable" subheading="AI assists. Humans review and approve." accent={theme.governance}>
    <div style={{opacity: inputOpacity}}>
      <div style={{position: 'absolute', left: 104, top: 340, width: 230, height: 126, borderRadius: 20, background: '#132a44', border: '1px solid #527293', padding: '18px 20px', boxSizing: 'border-box', opacity: human}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 14}}><div style={{width: 46, height: 46, borderRadius: 99, background: '#d7e7f7', color: '#17304b', display: 'grid', placeItems: 'center', fontSize: 25, fontWeight: 900}}>H</div><div><div style={{fontSize: 16, letterSpacing: 1.4, color: '#8fc9ff', fontWeight: 900}}>HUMAN INPUT</div><div style={{fontSize: 19, marginTop: 5, color: '#dbe8f5'}}>Requirements entered</div></div></div>
      </div>
      <SpeechBubble accent="#ffae66" eyebrow="SENSITIVE DATA REQUIREMENT" style={{left: 385, top: 330, width: 495, height: 144, opacity: sensitiveBubble}}>&ldquo;This column is sensitive.&rdquo;<div style={{fontFamily: 'ui-monospace, monospace', fontSize: 19, color: '#ffd2a4', marginTop: 5}}>customer_id</div></SpeechBubble>
      <SpeechBubble accent="#b487ff" eyebrow="BUSINESS RULE REQUIREMENT" style={{left: 930, top: 330, width: 875, height: 144, opacity: ruleBubble}}>&ldquo;Modified time must be on or after order time.&rdquo;</SpeechBubble>
    </div>

    <div style={{opacity: sensitivePhase}}>
      <div style={{position: 'absolute', left: 165, top: 540, fontSize: 18, color: '#ffbd76', fontWeight: 900, letterSpacing: 1.4}}>INSPECT SAMPLE VALUES</div>
      <Mascot pose="scanning" x={130} y={585} size={285} delay={seconds(2.4)} />
      <Surface accent="#ffae66" style={{position: 'absolute', left: 475, top: 520, width: 860, height: 335, padding: '24px 30px', opacity: scan}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}><div style={{fontSize: 20, color: '#ffbd76', fontWeight: 900, letterSpacing: 1.4}}>customer_id</div><div style={{padding: '9px 15px', borderRadius: 10, background: '#5d351f', color: '#ffd2a4', fontSize: 18, fontWeight: 850, opacity: treatment}}>FabricOps suggestion · Mask</div></div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 80px 1fr', marginTop: 22, color: '#8fa7bf', fontSize: 17, fontWeight: 850}}><div>BEFORE</div><div /><div>AFTER</div></div>
        {['C001', 'C002', 'C003'].map((value) => <div key={value} style={{display: 'grid', gridTemplateColumns: '1fr 80px 1fr', alignItems: 'center', height: 62, borderTop: '1px solid #3a526d', fontFamily: 'ui-monospace, monospace', fontSize: 26}}><div>{value}</div><div style={{color: '#66809b', textAlign: 'center'}}>→</div><div style={{color: '#ffbd76', position: 'relative'}}><span style={{opacity: 1 - redact}}>{value}</span><span style={{position: 'absolute', left: 0, opacity: redact}}>C•••</span></div></div>)}
      </Surface>
      <div style={{position: 'absolute', left: 1350, top: 540, fontSize: 18, color: '#ffbd76', fontWeight: 900, letterSpacing: 1.4, opacity: treatment}}>PREVIEW MASK TREATMENT</div>
      <Mascot pose="masking" x={1390} y={585} size={285} delay={seconds(4.5)} />
      <div style={{position: 'absolute', left: 405, top: 681, width: 70, height: 5, borderRadius: 99, background: '#ffae66', scale: `${scan} 1`, transformOrigin: 'left'}} />
      <div style={{position: 'absolute', left: 1335, top: 681, width: 65, height: 5, borderRadius: 99, background: '#ffae66', scale: `${treatment} 1`, transformOrigin: 'left'}} />
    </div>

    <div style={{opacity: businessPhase}}>
      <div style={{position: 'absolute', left: 130, top: 535, fontSize: 18, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.4}}>TRANSLATE REQUIREMENT</div>
      <Mascot pose="coding" x={125} y={580} size={300} delay={seconds(7.8)} />
      <Surface accent="#b487ff" style={{position: 'absolute', left: 500, top: 520, width: 855, height: 335, padding: '25px 30px', opacity: coding}}>
        <div style={{fontSize: 18, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.4}}>FABRICOPS SUGGESTION · STRUCTURED DQ RULE</div>
        <div style={{opacity: structuredRule, marginTop: 31}}><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 28, color: '#d8c9ff'}}>column_relationship</div><div style={{marginTop: 24, borderRadius: 14, padding: '20px 22px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 26, color: '#f1ebff', clipPath: `inset(0 ${(1 - structuredRule) * 100}% 0 0)`}}>modified_datetime &gt;= order_datetime</div></div>
        <div style={{opacity: structureCheck, display: 'flex', alignItems: 'center', gap: 12, marginTop: 25, color: '#b9f4d4', fontSize: 20, fontWeight: 850}}><div style={{width: 30, height: 30, borderRadius: 99, background: '#1f6045', display: 'grid', placeItems: 'center'}}>✓</div>Structure ready for human review</div>
      </Surface>
      <div style={{position: 'absolute', left: 1420, top: 535, fontSize: 18, color: '#c5a8ff', fontWeight: 900, letterSpacing: 1.4, opacity: structureCheck}}>CHECK RULE READINESS</div>
      <Mascot pose="validate" x={1415} y={580} size={300} delay={seconds(10.8)} />
      <div style={{position: 'absolute', left: 425, top: 681, width: 75, height: 5, borderRadius: 99, background: '#b487ff', scale: `${coding} 1`, transformOrigin: 'left'}} />
      <div style={{position: 'absolute', left: 1355, top: 681, width: 70, height: 5, borderRadius: 99, background: '#b487ff', scale: `${structureCheck} 1`, transformOrigin: 'left'}} />
    </div>

    <div style={{position: 'absolute', left: 355, top: 565, width: 1210, opacity: contract, translate: `0 ${(1 - contract) * 22}px`}}>
      <div style={{textAlign: 'center', fontSize: 18, color: '#a9bdd2', fontWeight: 900, letterSpacing: 1.6}}>HUMAN REVIEWED &amp; APPROVED</div>
      <div style={{marginTop: 24, display: 'flex', alignItems: 'center', gap: 20, padding: '24px 28px', borderRadius: 20, background: '#132942', border: '2px solid #72e6ad88', boxShadow: '0 18px 45px #0007'}}>
        <div style={{fontSize: 26, fontWeight: 900, color: '#f5f9fd', marginRight: 12}}>Data Contract</div>
        <div style={{flex: 1, padding: '14px 18px', borderRadius: 13, background: '#3f2a1d', color: '#ffd2a4', fontSize: 20, fontWeight: 820}}>✓ Approved sensitive-data treatment</div>
        <div style={{flex: 1, padding: '14px 18px', borderRadius: 13, background: '#292145', color: '#ddd0ff', fontSize: 20, fontWeight: 820}}>✓ Approved Data Quality rule</div>
        <div style={{fontSize: 30, color: '#72e6ad'}}>→</div><div style={{fontSize: 20, fontWeight: 900, color: '#72e6ad'}}>VALIDATION</div>
      </div>
    </div>
  </SceneShell>;
};

export const ValidationScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const read = enterProgress(frame, fps, seconds(0.5));
  const transform = enterProgress(frame, fps, seconds(1));
  const write = enterProgress(frame, fps, seconds(1.5));
  const firstLink = interpolate(frame, [seconds(0.9), seconds(1.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secondLink = interpolate(frame, [seconds(1.4), seconds(2.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const contract = enterProgress(frame, fps, seconds(2.4));
  const records = enterProgress(frame, fps, seconds(3.8));
  const failed = frame < seconds(7.1);
  const correction = enterProgress(frame, fps, seconds(6.1));
  const rerun = enterProgress(frame, fps, seconds(7.1));
  const enforcement = interpolate(frame, [seconds(8), seconds(8.5), seconds(9.8), seconds(10.2)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const success = enterProgress(frame, fps, seconds(9.9));
  return <SceneShell duration={VALIDATION_DURATION} eyebrow="VALIDATION · STEP 4" heading="One reusable pipeline pattern" accent="#72e6ad">
    <PipelinePattern top={230} read={read} transform={transform} write={write} firstLink={firstLink} secondLink={secondLink} />
    <div style={{position: 'absolute', left: 958, top: 510, width: 4, height: 42, background: '#b487ff', opacity: contract, transformOrigin: 'top', scale: `1 ${contract}`}} />
    <div style={{position: 'absolute', left: 590, top: 550, width: 740, padding: '14px 20px', borderRadius: 14, background: '#292145', border: '1px solid #8e6aca', boxSizing: 'border-box', textAlign: 'center', opacity: contract}}><span style={{fontSize: 18, color: '#c5a8ff', fontWeight: 900, marginRight: 16}}>FROZEN DATA CONTRACT</span><span style={{fontFamily: 'ui-monospace, monospace', color: '#eee7ff', fontSize: 19}}>modified_datetime &gt;= order_datetime</span></div>
    <Mascot pose="validate" x={1395} y={555} size={290} delay={seconds(2.8)} />

    <div style={{position: 'absolute', left: 190, top: 665, width: 540, height: 148, borderRadius: 18, background: '#112a25', border: '2px solid #4fbd87', padding: '18px 22px', boxSizing: 'border-box', opacity: records, translate: `${(1 - records) * -28}px 0`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><div style={{fontSize: 18, color: '#8fa7bf', fontWeight: 850}}>RECORD A</div><div style={{padding: '7px 14px', borderRadius: 10, background: '#1f6045', color: '#baffd8', fontSize: 20, fontWeight: 900}}>PASS</div></div>
      <div style={{display: 'flex', gap: 28, marginTop: 18, fontFamily: 'ui-monospace, monospace', fontSize: 20}}><span>order 09:00</span><span style={{color: '#72e6ad'}}>modified 09:18</span></div>
    </div>
    <div style={{position: 'absolute', left: 770, top: 665, width: 560, height: 148, borderRadius: 18, background: failed ? '#351d27' : '#112a25', border: `2px solid ${failed ? '#cc5d64' : '#4fbd87'}`, padding: '18px 22px', boxSizing: 'border-box', opacity: records, translate: `0 ${(1 - records) * 22}px`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><div style={{fontSize: 18, color: '#8fa7bf', fontWeight: 850}}>RECORD B · ENGINEERING CORRECTION</div><div style={{padding: '7px 14px', borderRadius: 10, background: failed ? '#6d2831' : '#1f6045', color: failed ? '#ffb0aa' : '#baffd8', fontSize: 20, fontWeight: 900}}>{failed ? 'FAIL' : 'PASS'}</div></div>
      <div style={{display: 'flex', gap: 28, marginTop: 18, fontFamily: 'ui-monospace, monospace', fontSize: 20}}><span>order 09:00</span><span style={{color: failed ? '#ff9c8c' : '#72e6ad'}}>{failed ? 'modified 08:00' : 'modified 09:18'}</span></div>
      <div style={{position: 'absolute', left: 235, top: 103, opacity: correction, color: '#d5e2ef', fontSize: 17, fontWeight: 820}}>08:00 → 09:18 · rerun check</div>
      {!failed ? <div style={{position: 'absolute', right: -36, top: 56, width: 34, height: 5, borderRadius: 99, background: '#72e6ad', scale: `${rerun} 1`, transformOrigin: 'left'}} /> : null}
    </div>

    <div style={{position: 'absolute', left: 255, right: 255, top: 878, display: 'flex', justifyContent: 'center', gap: 18, opacity: enforcement}}>
      {[
        ['VALIDATE', 'Check only · no publishing', '#8ecbff'],
        ['WARN', 'Record violation · may continue', '#ffbd76'],
        ['BLOCK', 'Stop a failing guarded operation', '#ff9c8c'],
      ].map(([title, copy, color]) => <div key={title} style={{padding: '13px 18px', borderRadius: 13, background: '#10243c', border: `1px solid ${color}77`, fontSize: 17}}><span style={{fontWeight: 900, color, marginRight: 10}}>{title}</span><span style={{color: '#c0cede'}}>{copy}</span></div>)}
    </div>
    <div style={{position: 'absolute', left: 540, right: 540, top: 883, padding: '18px 24px', borderRadius: 16, background: '#153c2e', border: '2px solid #55bd89', textAlign: 'center', opacity: success, translate: `0 ${(1 - success) * 16}px`}}><span style={{fontSize: 27, color: '#baffd8', fontWeight: 900}}>✓ Frozen Data Contract validated</span><span style={{fontSize: 19, color: '#91c9aa', marginLeft: 17}}>Ready for activation review</span></div>
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
