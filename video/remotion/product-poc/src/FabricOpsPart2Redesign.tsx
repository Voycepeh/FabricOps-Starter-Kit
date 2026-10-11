import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';

const seconds = (value: number) => Math.round(value * 30);

export const ENGINEERING_DURATION = seconds(13);
export const GOVERNANCE_DURATION = seconds(16);
export const VALIDATION_DURATION = seconds(12);
export const ACTIVATION_DURATION = seconds(13);
export const CLOSING_DURATION = seconds(9);

type MascotPose = 'writing' | 'scanning' | 'masking' | 'carrying' | 'pointing' | 'dev' | 'prod';

const Mascot = ({pose, x, y, size, delay}: {pose: MascotPose; x: number; y: number; size: number; delay: number}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + seconds(0.6)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <Img src={staticFile(`mascots/robot-${pose}.png`)} style={{
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

const SceneShell = ({duration, eyebrow, heading, subheading, accent, children}: {duration: number; eyebrow: string; heading: string; subheading: string; accent: string; children: ReactNode}) => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{
    opacity: sceneOpacity(frame, duration), color: theme.text, fontFamily: font,
    background: 'radial-gradient(circle at 48% 38%, #17375d 0%, #0b1930 44%, #060d19 86%)',
  }}>
    <AbsoluteFill style={{opacity: 0.14, backgroundImage: 'linear-gradient(#7aa7d51a 1px, transparent 1px), linear-gradient(90deg, #7aa7d51a 1px, transparent 1px)', backgroundSize: '64px 64px'}} />
    <div style={{position: 'absolute', top: 58, left: 104, right: 104}}>
      <div style={{fontSize: 21, fontWeight: 850, letterSpacing: 2.4, color: accent}}>{eyebrow}</div>
      <div style={{fontSize: 66, lineHeight: 1.05, fontWeight: 950, marginTop: 20, letterSpacing: -1.4}}>{heading}</div>
      <div style={{fontSize: 28, color: '#afc0d5', marginTop: 20}}>{subheading}</div>
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
  return <SceneShell duration={ENGINEERING_DURATION} eyebrow="ENGINEERING · STEP 2" heading="One reusable pipeline pattern" subheading="Governed boundaries. Your PySpark." accent={theme.engineering}>
    <div style={{position: 'absolute', left: 145, top: 352, display: 'flex', alignItems: 'center', gap: 115}}>
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
    <StageArrow left={575} top={490} width={112} progress={firstLink} color="#52d6c6" />
    <StageArrow left={1120} top={490} width={112} progress={secondLink} color="#72e6ad" />
    <Img src={staticFile('mascots/robot-carrying.png')} style={{
      position: 'absolute', left: 205 + ferry * 1375, top: 605, width: 220, height: 220,
      objectFit: 'contain', opacity: ferryOpacity, filter: 'drop-shadow(0 16px 26px #0008)',
    }} />
    <Reveal at={seconds(8.2)} y={16}>
      <div style={{position: 'absolute', left: 210, right: 210, top: 810, display: 'flex', justifyContent: 'center', gap: 28}}>
        {['02A · Full Refresh', '02B · Incremental', '02C · SCD'].map((label) => <div key={label} style={{padding: '17px 31px', borderRadius: 16, background: '#122d49', border: '1px solid #4d759c', fontSize: 24, fontWeight: 820, color: '#d5e9ff'}}>{label}</div>)}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 897, textAlign: 'center', fontSize: 22, color: '#91a8c0'}}>Choose one pattern per workload.</div>
    </Reveal>
  </SceneShell>;
};

export const GovernanceScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scan = enterProgress(frame, fps, seconds(1.1));
  const treatment = enterProgress(frame, fps, seconds(3.1));
  const rule = enterProgress(frame, fps, seconds(5.2));
  const runtime = enterProgress(frame, fps, seconds(7.2));
  return <SceneShell duration={GOVERNANCE_DURATION} eyebrow="GOVERNANCE · STEP 3" heading="Governance becomes executable" subheading="AI suggests. Humans decide. Pipelines enforce." accent={theme.governance}>
    <Surface accent="#ffae66" style={{position: 'absolute', left: 104, top: 340, width: 790, height: 526, padding: '30px 34px'}}>
      <div style={{fontSize: 21, fontWeight: 850, color: '#ffbd76', letterSpacing: 1.6}}>SENSITIVE DATA</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 70px 1fr', alignItems: 'center', gap: 16, marginTop: 34}}>
        <div style={{opacity: scan}}><div style={{fontSize: 22, color: '#9fb1c6'}}>DISCOVER</div><div style={{fontSize: 35, fontWeight: 880, marginTop: 12}}>customer_id</div><div style={{fontSize: 22, color: '#ffbd76', marginTop: 20}}>Direct PII</div></div>
        <div style={{fontSize: 46, color: '#607d9b', textAlign: 'center'}}>→</div>
        <div style={{opacity: treatment}}><div style={{fontSize: 22, color: '#9fb1c6'}}>TREAT</div><div style={{fontSize: 35, fontWeight: 880, marginTop: 12, color: '#ffbd76'}}>Mask</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 24, color: '#f5d8bd', marginTop: 20}}>C001 → C•••</div></div>
      </div>
      <div style={{height: 1, background: '#39506a', marginTop: 38}} />
      <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 28, opacity: treatment}}><div style={{padding: '12px 18px', borderRadius: 12, background: '#5d351f', color: '#ffd5ad', fontWeight: 850, fontSize: 20}}>Data Contract</div><div style={{color: '#9eb0c5', fontSize: 22}}>reviewed treatment</div></div>
    </Surface>
    <Surface accent="#b487ff" style={{position: 'absolute', left: 956, top: 340, width: 860, height: 526, padding: '30px 34px'}}>
      <div style={{fontSize: 21, fontWeight: 850, color: '#c5a8ff', letterSpacing: 1.6}}>BUSINESS RULE → DATA QUALITY</div>
      <div style={{opacity: rule, marginTop: 28}}>
        <div style={{fontSize: 25, color: '#c8d3e0', lineHeight: 1.42}}>&ldquo;Modified time must be on or after order time.&rdquo;</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 30}}><div style={{fontSize: 34, color: '#7790aa'}}>↓</div><div style={{fontFamily: 'ui-monospace, monospace', fontSize: 25, color: '#d6c4ff'}}>column_relationship</div></div>
        <div style={{marginTop: 22, borderRadius: 15, padding: '17px 21px', background: '#211c3e', border: '1px solid #7253ab', fontFamily: 'ui-monospace, monospace', fontSize: 23, color: '#ebe4ff'}}>modified_datetime ≥ order_datetime</div>
      </div>
      <div style={{opacity: runtime, marginTop: 28, fontSize: 23, fontWeight: 850, color: '#c5a8ff'}}>Structured rule → executable check</div>
    </Surface>
    <Mascot pose="scanning" x={115} y={765} size={210} delay={seconds(1.1)} />
    <Mascot pose="masking" x={680} y={740} size={220} delay={seconds(3.1)} />
    <Mascot pose="writing" x={1590} y={735} size={220} delay={seconds(5.2)} />
  </SceneShell>;
};

export const ValidationScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const failed = frame < seconds(5.8);
  const row = enterProgress(frame, fps, seconds(1.3));
  const correction = enterProgress(frame, fps, seconds(5.8));
  const policy = enterProgress(frame, fps, seconds(7.2));
  return <SceneShell duration={VALIDATION_DURATION} eyebrow="VALIDATION · STEP 4" heading="Fail. Correct. Pass." subheading="The frozen rule runs in Development." accent="#ff9c8c">
    <Surface accent={failed ? '#ff756d' : '#72e6ad'} style={{position: 'absolute', left: 120, top: 352, width: 1180, height: 440, padding: '30px 34px'}}>
      <div style={{display: 'grid', gridTemplateColumns: '185px 1fr 1fr 170px', gap: 2, borderRadius: 14, overflow: 'hidden', border: '1px solid #3b526d'}}>
        {['order_id', 'order_datetime', 'modified_datetime', 'result'].map((header) => <div key={header} style={{padding: '17px 18px', background: '#17314f', fontSize: 20, color: '#9db7d3', fontWeight: 800}}>{header}</div>)}
        <div style={{padding: '25px 18px', background: '#0d1d31', fontFamily: 'ui-monospace, monospace', fontSize: 24, opacity: row}}>O0007</div>
        <div style={{padding: '25px 18px', background: '#0d1d31', fontFamily: 'ui-monospace, monospace', fontSize: 24, opacity: row}}>2026-07-03 09:00</div>
        <div style={{padding: '25px 18px', background: failed ? '#3b1d26' : '#123528', fontFamily: 'ui-monospace, monospace', fontSize: 24, color: failed ? '#ff9c8c' : '#72e6ad'}}>{failed ? '2026-07-03 08:00' : '2026-07-03 09:18'}</div>
        <div style={{padding: '25px 18px', background: failed ? '#3b1d26' : '#123528', fontSize: 25, color: failed ? '#ff9c8c' : '#72e6ad', fontWeight: 900}}>{failed ? 'FAIL' : 'PASS'}</div>
      </div>
      <div style={{display: 'flex', alignItems: 'center', marginTop: 34, gap: 24}}>
        <div style={{width: 54, height: 54, borderRadius: 99, display: 'grid', placeItems: 'center', background: failed ? '#6d2831' : '#1f6045', color: failed ? '#ffb0aa' : '#baffd8', fontSize: 30, fontWeight: 900}}>{failed ? '!' : '✓'}</div>
        <div><div style={{fontSize: 29, fontWeight: 870, color: failed ? '#ff9c8c' : '#72e6ad'}}>{failed ? 'Rule violation identified' : 'Frozen Data Contract validated'}</div><div style={{fontSize: 22, color: '#9fb1c6', marginTop: 8}}>{failed ? 'modified_datetime is earlier than order_datetime' : 'validation_passed=True · published=False'}</div></div>
        {!failed ? <div style={{marginLeft: 'auto', opacity: correction, padding: '13px 19px', borderRadius: 12, background: '#153c2e', border: '1px solid #3d9b70', color: '#9ff0c4', fontSize: 20, fontWeight: 820}}>corrected row</div> : null}
      </div>
      <div style={{height: 6, borderRadius: 99, background: '#243b55', marginTop: 35, overflow: 'hidden'}}><div style={{width: failed ? '42%' : '100%', height: '100%', background: failed ? '#ff756d' : '#72e6ad'}} /></div>
    </Surface>
    <Mascot pose="scanning" x={1390} y={335} size={360} delay={seconds(1)} />
    <div style={{position: 'absolute', left: 170, right: 170, top: 844, display: 'flex', gap: 22, opacity: policy}}>
      {[
        ['VALIDATE', 'Check only · no publish', '#8ecbff'],
        ['WARN', 'Record · may continue', '#ffbd76'],
        ['BLOCK', 'Stop at Guardrail', '#ff9c8c'],
      ].map(([title, copy, color]) => <div key={title} style={{flex: 1, borderRadius: 16, padding: '17px 21px', background: '#10243c', border: `1px solid ${color}77`}}><span style={{fontSize: 18, fontWeight: 900, color, marginRight: 12}}>{title}</span><span style={{fontSize: 18, color: '#c0cede'}}>{copy}</span></div>)}
    </div>
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
