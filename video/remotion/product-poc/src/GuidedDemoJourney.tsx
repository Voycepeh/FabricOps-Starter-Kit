import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from './theme';

const FPS = 30;
const s = (value: number) => Math.round(value * FPS);

const stepDurations = {
  intro: s(3),
  step2: s(12),
  step3: s(14),
  step4: s(20),
  step5: s(10),
  step6: s(8),
} as const;

const starts = {
  intro: 0,
  step2: stepDurations.intro,
  step3: stepDurations.intro + stepDurations.step2,
  step4: stepDurations.intro + stepDurations.step2 + stepDurations.step3,
  step5: stepDurations.intro + stepDurations.step2 + stepDurations.step3 + stepDurations.step4,
  step6: stepDurations.intro + stepDurations.step2 + stepDurations.step3 + stepDurations.step4 + stepDurations.step5,
} as const;

export const GUIDED_DEMO_DURATION =
  stepDurations.intro +
  stepDurations.step2 +
  stepDurations.step3 +
  stepDurations.step4 +
  stepDurations.step5 +
  stepDurations.step6;

const fade = (frame: number, duration: number) =>
  interpolate(frame, [0, 12, duration - 12, duration], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const enter = (frame: number, fps: number, delay = 0) =>
  spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 88}});

const Shell = ({
  step,
  title,
  subtitle,
  color,
  children,
  duration,
}: {
  step: number;
  title: string;
  subtitle: string;
  color: string;
  children: React.ReactNode;
  duration: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: fade(frame, duration)}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 42%, #17345a 0%, #0b1830 38%, #060d19 78%)'}} />
      <div style={{position: 'absolute', left: 86, top: 66, display: 'flex', alignItems: 'center', gap: 20}}>
        <div style={{width: 68, height: 68, borderRadius: 99, display: 'grid', placeItems: 'center', background: color, color: '#07101f', fontSize: 36, fontWeight: 950}}>{step}</div>
        <div>
          <div style={{fontSize: 52, fontWeight: 920, color: '#f7f9fd'}}>{title}</div>
          <div style={{fontSize: 25, marginTop: 6, color: '#9fb0c5'}}>{subtitle}</div>
        </div>
      </div>
      {children}
    </AbsoluteFill>
  );
};

const Panel = ({
  children,
  x,
  y,
  width,
  height,
  color,
  progress = 1,
}: {
  children: React.ReactNode;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  progress?: number;
}) => (
  <div style={{
    position: 'absolute',
    left: x,
    top: y,
    width,
    height,
    borderRadius: 28,
    border: `2px solid ${color}88`,
    background: `linear-gradient(145deg, ${color}16, #0d192b 74%)`,
    boxShadow: `0 18px 44px #0007, 0 0 28px ${color}18`,
    opacity: progress,
    transform: `translateY(${(1 - progress) * 24}px) scale(${0.96 + progress * 0.04})`,
    boxSizing: 'border-box',
    padding: 28,
  }}>{children}</div>
);

const Field = ({label, value, accent}: {label: string; value: string; accent?: string}) => (
  <div style={{display: 'grid', gridTemplateColumns: '170px 1fr', gap: 18, alignItems: 'center', marginTop: 15}}>
    <div style={{fontSize: 20, color: '#879ab1', fontWeight: 700}}>{label}</div>
    <div style={{fontSize: 23, color: accent ?? '#f7f9fd', background: '#0a1424', border: '1px solid #31465f', borderRadius: 12, padding: '10px 14px', fontWeight: 700}}>{value}</div>
  </div>
);

const Chip = ({text, color}: {text: string; color: string}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', padding: '8px 13px', borderRadius: 999, background: `${color}1f`, border: `1px solid ${color}88`, color, fontSize: 19, fontWeight: 800}}>{text}</div>
);

const Arrow = ({x1, y1, x2, y2, color = '#91a6bf', opacity = 1}: {x1: number; y1: number; x2: number; y2: number; color?: string; opacity?: number}) => (
  <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity}}>
    <defs>
      <marker id="demo-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10z" fill={color} /></marker>
    </defs>
    <path d={`M${x1} ${y1} C${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}`} fill="none" stroke={color} strokeWidth="5" markerEnd="url(#demo-arrow)" />
  </svg>
);

const MiniTable = ({rows, highlight}: {rows: string[][]; highlight?: number}) => (
  <div style={{border: '1px solid #344a64', borderRadius: 14, overflow: 'hidden'}}>
    {rows.map((row, ri) => <div key={ri} style={{display: 'grid', gridTemplateColumns: `repeat(${row.length}, 1fr)`, background: highlight === ri ? '#ffad5524' : ri === 0 ? '#1b2d46' : '#0d192b'}}>
      {row.map((cell, ci) => <div key={ci} style={{padding: '10px 12px', borderRight: ci < row.length - 1 ? '1px solid #2b4059' : undefined, borderTop: ri > 0 ? '1px solid #26384f' : undefined, color: ri === 0 ? '#d7e4f3' : '#eef4fb', fontSize: 18, fontWeight: ri === 0 ? 800 : 600}}>{cell}</div>)}
    </div>)}
  </div>
);

const IntroScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = enter(frame, fps);
  return <AbsoluteFill style={{display: 'grid', placeItems: 'center', opacity: fade(frame, stepDurations.intro), background: 'radial-gradient(circle at 50% 45%, #173f55 0%, #0b1830 42%, #060d19 82%)'}}>
    <div style={{textAlign: 'center', transform: `scale(${0.92 + p * 0.08})`, opacity: p}}>
      <div style={{fontSize: 86, fontWeight: 950, color: '#f7f9fd'}}>See FabricOps in action</div>
      <div style={{fontSize: 38, marginTop: 28, color: '#aebed3', fontWeight: 750}}>
        <span style={{color: '#ffad55', fontWeight: 900}}>CustomerOrders</span>
        <span style={{margin: '0 18px', color: '#5f748e'}}>·</span>
        From source data to production
      </div>
    </div>
  </AbsoluteFill>;
};

const Step2 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sources = enter(frame, fps, 6);
  const read = enter(frame, fps, 28);
  const transform = enter(frame, fps, 48);
  const write = enter(frame, fps, 68);
  const targets = enter(frame, fps, 88);
  const metadata = enter(frame, fps, 112);

  const box = (label: string, sublabel: string, color: string) => (
    <div style={{width: 255, minHeight: 112, border: `2px solid ${color}88`, borderRadius: 18, background: `${color}12`, padding: '20px 22px', boxSizing: 'border-box'}}>
      <div style={{fontSize: 23, fontWeight: 900, color: '#f7f9fd'}}>{label}</div>
      <div style={{fontSize: 17, color: '#9fb0c5', marginTop: 8}}>{sublabel}</div>
    </div>
  );

  return <Shell step={2} title="Engineer & catalogue" subtitle="Read three sources, transform with PySpark, then write two governed targets" color={theme.engineering} duration={stepDurations.step2}>
    <div style={{position: 'absolute', left: 80, right: 80, top: 285, height: 520, display: 'grid', gridTemplateColumns: '255px 300px 310px 300px 255px', columnGap: 70, alignItems: 'center'}}>
      <div style={{display: 'flex', flexDirection: 'column', gap: 28, opacity: sources}}>
        {box('Orders', 'Sales Lakehouse', theme.engineering)}
        {box('Products', 'Product Lakehouse', theme.engineering)}
        {box('Order History', 'Sales Lakehouse', theme.engineering)}
      </div>

      <div style={{opacity: read, display: 'grid', placeItems: 'center'}}>
        <div style={{width: 300, border: `2px solid ${theme.engineering}99`, borderRadius: 20, padding: '26px 20px', boxSizing: 'border-box', textAlign: 'center', background: '#0d192b'}}>
          <div style={{fontSize: 18, fontWeight: 850, color: '#93c7ff'}}>READ</div>
          <div style={{fontSize: 25, marginTop: 10, fontFamily: 'ui-monospace, SFMono-Regular, monospace', fontWeight: 850}}>orchestrate_read()</div>
        </div>
      </div>

      <div style={{opacity: transform, display: 'grid', placeItems: 'center'}}>
        <div style={{width: 310, border: '2px solid #52d6c699', borderRadius: 20, padding: '30px 22px', textAlign: 'center', boxSizing: 'border-box', background: '#0d192b'}}>
          <div style={{fontSize: 19, fontWeight: 850, color: '#52d6c6'}}>YOUR PYSPARK</div>
          <div style={{fontSize: 26, marginTop: 12, fontWeight: 900}}>Transform</div>
          <div style={{fontSize: 18, color: '#9fb0c5', marginTop: 8}}>Join · Clean · Shape</div>
        </div>
      </div>

      <div style={{opacity: write, display: 'grid', placeItems: 'center'}}>
        <div style={{width: 300, border: `2px solid ${theme.production}99`, borderRadius: 20, padding: '26px 20px', boxSizing: 'border-box', textAlign: 'center', background: '#0d192b'}}>
          <div style={{fontSize: 18, fontWeight: 850, color: '#72e6ad'}}>WRITE</div>
          <div style={{fontSize: 25, marginTop: 10, fontFamily: 'ui-monospace, SFMono-Regular, monospace', fontWeight: 850}}>orchestrate_write()</div>
        </div>
      </div>

      <div style={{display: 'flex', flexDirection: 'column', gap: 34, opacity: targets}}>
        {box('Curated Orders', 'Warehouse target', theme.production)}
        {box('Customer Summary', 'Warehouse target', theme.production)}
      </div>
    </div>

    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      <defs>
        <marker id="step2-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill={theme.engineering} /></marker>
        <marker id="step2-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill={theme.production} /></marker>
      </defs>
      <g fill="none" strokeWidth="4" opacity={read}>
        <path d="M335 367 H405 Q430 367 430 392 V545 H475" stroke={theme.engineering} markerEnd="url(#step2-blue)" />
        <path d="M335 507 H475" stroke={theme.engineering} markerEnd="url(#step2-blue)" />
        <path d="M335 647 H405 Q430 647 430 622 V545 H475" stroke={theme.engineering} markerEnd="url(#step2-blue)" />
      </g>
      <path d="M775 545 H845" fill="none" stroke="#52d6c6" strokeWidth="4" opacity={transform} />
      <path d="M1155 545 H1225" fill="none" stroke={theme.production} strokeWidth="4" opacity={write} markerEnd="url(#step2-green)" />
      <g fill="none" stroke={theme.production} strokeWidth="4" opacity={targets}>
        <path d="M1525 545 H1570 Q1595 545 1595 510 V425 H1665" markerEnd="url(#step2-green)" />
        <path d="M1525 545 H1570 Q1595 545 1595 580 V665 H1665" markerEnd="url(#step2-green)" />
      </g>
    </svg>

    <div style={{position: 'absolute', left: 655, right: 655, top: 820, display: 'flex', justifyContent: 'center', gap: 14, opacity: metadata}}>
      <Chip text="Profile" color="#52d6c6" />
      <Chip text="Lineage" color={theme.governance} />
      <Chip text="Catalogue" color={theme.consumer} />
    </div>
  </Shell>;
};

const BigStage = ({label, color, progress, children}: {label: string; color: string; progress: number; children?: React.ReactNode}) => (
  <div style={{width: 390, minHeight: 250, borderRadius: 32, border: `3px solid ${color}88`, background: `linear-gradient(145deg, ${color}18, #0d192b 76%)`, boxShadow: `0 24px 60px #0008, 0 0 34px ${color}20`, display: 'grid', placeItems: 'center', padding: 34, boxSizing: 'border-box', opacity: progress, transform: `translateY(${(1-progress)*28}px) scale(${0.94+progress*0.06})`}}>
    <div style={{textAlign: 'center'}}>
      <div style={{fontSize: 34, fontWeight: 930, color: '#f7f9fd'}}>{label}</div>
      {children}
    </div>
  </div>
);

const Step3 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const table = enter(frame, fps, 4);
  const contract = enter(frame, fps, 38);
  const sensitivity = enter(frame, fps, 88);
  const quality = enter(frame, fps, 138);
  return <Shell step={3} title="Author & freeze the contract" subtitle="" color={theme.governance} duration={stepDurations.step3}>
    <div style={{position: 'absolute', left: 150, right: 150, top: 315, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <BigStage label="CustomerOrders" color={theme.consumer} progress={table}>
        <div style={{marginTop: 24}}><MiniTable rows={[['Order', 'NRIC', 'Qty'], ['1001', 'S1234567A', '2'], ['1002', 'S7654321B', '1']]} /></div>
      </BigStage>
      <div style={{fontSize: 70, color: theme.governance, opacity: contract}}>→</div>
      <BigStage label="Data Contract" color={theme.governance} progress={contract}>
        <div style={{fontSize: 22, color: '#b9c7d8', marginTop: 22}}>Grain · descriptions · ownership</div>
      </BigStage>
      <div style={{fontSize: 70, color: theme.production, opacity: Math.min(sensitivity, quality)}}>+</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 24}}>
        <BigStage label="Sensitive Data" color={theme.consumer} progress={sensitivity}>
          <div style={{fontSize: 24, color: '#ffbd76', marginTop: 18}}>NRIC → Mask</div>
        </BigStage>
        <BigStage label="Data Quality" color={theme.production} progress={quality}>
          <div style={{fontSize: 24, color: '#72e6ad', marginTop: 18}}>Category · Quantity</div>
        </BigStage>
      </div>
    </div>
    <div style={{position: 'absolute', left: 760, top: 825, width: 400, textAlign: 'center', fontSize: 30, fontWeight: 900, color: theme.consumer, opacity: enter(frame, fps, 190)}}>Frozen contract</div>
  </Shell>;
};

const Step4 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const incoming = enter(frame, fps, 4);
  const guardrails = enter(frame, fps, 42);
  const failed = enter(frame, fps, 92);
  const corrected = enter(frame, fps, 250);
  const passed = enter(frame, fps, 335);
  const secondHalf = frame >= 250;
  return <Shell step={4} title="Validate the contract" subtitle="" color={theme.engineering} duration={stepDurations.step4}>
    <div style={{position: 'absolute', left: 130, right: 130, top: 320, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <BigStage label={secondHalf ? "Corrected rows" : "Incoming rows"} color={theme.engineering} progress={secondHalf ? corrected : incoming}>
        <div style={{marginTop: 24}}><MiniTable highlight={secondHalf ? undefined : 1} rows={secondHalf ? [['NRIC', 'Category', 'Qty'], ['S1234567A', 'Home', '2']] : [['NRIC', 'Category', 'Qty'], ['S1234567A', 'Toys', '0']]} /></div>
      </BigStage>
      <div style={{fontSize: 72, color: '#91a6bf', opacity: guardrails}}>→</div>
      <BigStage label="Contract guardrails" color={theme.governance} progress={guardrails}>
        <div style={{fontSize: 23, color: '#c5a8ff', marginTop: 22}}>Mask · Allowed values · Range</div>
      </BigStage>
      <div style={{fontSize: 72, color: secondHalf ? theme.production : '#ff6b6b', opacity: secondHalf ? passed : failed}}>→</div>
      <BigStage label={secondHalf ? "PASS" : "FAIL"} color={secondHalf ? theme.production : '#ff6b6b'} progress={secondHalf ? passed : failed}>
        <div style={{fontSize: 27, fontWeight: 900, marginTop: 20, color: secondHalf ? '#72e6ad' : '#ff8b8b'}}>{secondHalf ? "✓ Governed data" : "Toys ✕   Qty 0 ✕"}</div>
      </BigStage>
    </div>
    {!secondHalf && <div style={{position: 'absolute', left: 0, right: 0, top: 790, textAlign: 'center', opacity: enter(frame, fps, 150)}}>
      <span style={{fontSize: 36, fontWeight: 930, color: theme.consumer}}>Fix</span>
      <span style={{fontSize: 42, margin: '0 24px', color: '#637991'}}>→</span>
      <span style={{fontSize: 36, fontWeight: 930, color: theme.engineering}}>Re-run</span>
    </div>}
  </Shell>;
};

const Step5 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const contract = enter(frame, fps, 5);
  const activate = enter(frame, fps, 45);
  const engineering = enter(frame, fps, 105);
  const promote = enter(frame, fps, 145);
  return <Shell step={5} title="Activate & promote" subtitle="" color={theme.governance} duration={stepDurations.step5}>
    <div style={{position: 'absolute', left: 170, right: 170, top: 330, display: 'grid', gridTemplateColumns: '1fr 180px 1fr', alignItems: 'center', columnGap: 80}}>
      <BigStage label="Frozen Contract" color={theme.governance} progress={contract}>
        <div style={{fontSize: 26, color: '#c5a8ff', marginTop: 22}}>CustomerOrders</div>
      </BigStage>
      <div style={{textAlign: 'center', opacity: activate}}>
        <div style={{fontSize: 64, color: theme.production}}>→</div>
        <div style={{fontSize: 24, fontWeight: 900, color: theme.production, marginTop: 12}}>ACTIVATE</div>
      </div>
      <BigStage label="Active Governance" color={theme.production} progress={activate}>
        <div style={{fontSize: 26, color: '#72e6ad', marginTop: 22}}>Contract v3</div>
      </BigStage>

      <div style={{gridColumn: '1 / 2', marginTop: 70}}><BigStage label="Development" color={theme.engineering} progress={engineering}><div style={{fontSize: 24, color: '#93c7ff', marginTop: 20}}>00 Config · 02 Pipeline</div></BigStage></div>
      <div style={{gridColumn: '2 / 3', gridRow: 2, textAlign: 'center', opacity: promote, marginTop: 70}}>
        <div style={{fontSize: 64, color: theme.production}}>→</div>
        <div style={{fontSize: 24, fontWeight: 900, color: theme.production, marginTop: 12}}>PROMOTE</div>
      </div>
      <div style={{gridColumn: '3 / 4', gridRow: 2, marginTop: 70}}><BigStage label="Production" color={theme.production} progress={promote}><div style={{fontSize: 24, color: '#72e6ad', marginTop: 20}}>00 Config · 02 Pipeline</div></BigStage></div>
    </div>
  </Shell>;
};

const Step6 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pipeline = enter(frame, fps, 5);
  const checks = [35, 52, 69, 86].map((delay) => enter(frame, fps, delay));
  const output = enter(frame, fps, 120);
  return <Shell step={6} title="Run in Production" subtitle="" color={theme.production} duration={stepDurations.step6}>
    <div style={{position: 'absolute', left: 180, right: 180, top: 350, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <BigStage label="Production Pipeline" color={theme.engineering} progress={pipeline}>
        <div style={{fontSize: 24, color: '#93c7ff', marginTop: 20}}>Read → PySpark → Write</div>
      </BigStage>
      <div style={{width: 520, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20}}>
        {['Freshness', 'Schema', 'Sensitive Data', 'Data Quality'].map((label, i) => <div key={label} style={{height: 115, borderRadius: 22, border: `2px solid ${theme.production}88`, background: `${theme.production}14`, display: 'grid', placeItems: 'center', fontSize: 24, fontWeight: 900, color: '#72e6ad', opacity: checks[i], transform: `scale(${0.9 + checks[i]*0.1})`}}>✓ {label}</div>)}
      </div>
      <BigStage label="Production Tables" color={theme.production} progress={output}>
        <div style={{fontSize: 26, color: '#72e6ad', marginTop: 20}}>Ready to consume</div>
      </BigStage>
    </div>
  </Shell>;
};


export const GuidedDemoJourney = () => (
  <AbsoluteFill>
    <Sequence from={starts.intro} durationInFrames={stepDurations.intro}><IntroScene /></Sequence>
    <Sequence from={starts.step2} durationInFrames={stepDurations.step2}><Step2 /></Sequence>
    <Sequence from={starts.step3} durationInFrames={stepDurations.step3}><Step3 /></Sequence>
    <Sequence from={starts.step4} durationInFrames={stepDurations.step4}><Step4 /></Sequence>
    <Sequence from={starts.step5} durationInFrames={stepDurations.step5}><Step5 /></Sequence>
    <Sequence from={starts.step6} durationInFrames={stepDurations.step6}><Step6 /></Sequence>
  </AbsoluteFill>
);
