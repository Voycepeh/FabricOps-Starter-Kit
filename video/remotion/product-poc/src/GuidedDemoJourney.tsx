import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from './theme';

const FPS = 30;
const s = (value: number) => Math.round(value * FPS);

const stepDurations = {
  intro: s(3),
  step1: s(9),
  step2: s(12),
  step3: s(14),
  step4: s(20),
  step5: s(10),
  step6: s(8),
  step7: s(7),
} as const;

const starts = {
  intro: 0,
  step1: stepDurations.intro,
  step2: stepDurations.intro + stepDurations.step1,
  step3: stepDurations.intro + stepDurations.step1 + stepDurations.step2,
  step4: stepDurations.intro + stepDurations.step1 + stepDurations.step2 + stepDurations.step3,
  step5: stepDurations.intro + stepDurations.step1 + stepDurations.step2 + stepDurations.step3 + stepDurations.step4,
  step6: stepDurations.intro + stepDurations.step1 + stepDurations.step2 + stepDurations.step3 + stepDurations.step4 + stepDurations.step5,
  step7: stepDurations.intro + stepDurations.step1 + stepDurations.step2 + stepDurations.step3 + stepDurations.step4 + stepDurations.step5 + stepDurations.step6,
} as const;

export const GUIDED_DEMO_DURATION =
  stepDurations.intro +
  stepDurations.step1 +
  stepDurations.step2 +
  stepDurations.step3 +
  stepDurations.step4 +
  stepDurations.step5 +
  stepDurations.step6 +
  stepDurations.step7;

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
      <div style={{position: 'absolute', left: 86, right: 86, bottom: 32, height: 4, borderRadius: 99, background: '#26384f'}}>
        <div style={{height: 4, borderRadius: 99, background: color, width: `${interpolate(frame, [0, duration], [0, 100], {extrapolateRight: 'clamp'})}%`}} />
      </div>
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
      <div style={{fontSize: 82, fontWeight: 950, color: '#f7f9fd'}}>Let’s trace one data product</div>
      <div style={{fontSize: 42, marginTop: 18, color: '#62e4ad', fontWeight: 850}}>through the full 7-step FabricOps flow</div>
      <div style={{marginTop: 42, display: 'inline-flex', alignItems: 'center', gap: 18, padding: '18px 28px', border: '2px solid #ffad5588', borderRadius: 20, background: '#ffad5512'}}>
        <div style={{fontSize: 26, color: '#ffad55', fontWeight: 850}}>Example</div>
        <div style={{fontSize: 34, color: '#f7f9fd', fontWeight: 900}}>CustomerOrders</div>
      </div>
    </div>
  </AbsoluteFill>;
};

const Step1 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = enter(frame, fps, 6);
  const b = enter(frame, fps, 20);
  const agreement = enter(frame, fps, 46);
  return <Shell step={1} title="Establish stewardship & agreement" subtitle="Define responsibility before engineering starts" color={theme.governance} duration={stepDurations.step1}>
    <Panel x={110} y={245} width={510} height={340} color={theme.governance} progress={a}>
      <div style={{fontSize: 29, fontWeight: 900}}>Create Data Steward</div>
      <Field label="Data domain" value="Sales Data" />
      <Field label="Steward" value="Alice Tan" />
      <Field label="Purpose" value="Order transactions" />
      <div style={{marginTop: 22}}><Chip text="Saved" color={theme.production} /></div>
    </Panel>
    <Panel x={1300} y={245} width={510} height={340} color={theme.governance} progress={b}>
      <div style={{fontSize: 29, fontWeight: 900}}>Create Data Steward</div>
      <Field label="Data domain" value="Customer Data" />
      <Field label="Steward" value="Bob Lim" />
      <Field label="Purpose" value="Customer master" />
      <div style={{marginTop: 22}}><Chip text="Saved" color={theme.production} /></div>
    </Panel>
    <Arrow x1={620} y1={420} x2={780} y2={520} color={theme.governance} opacity={agreement} />
    <Arrow x1={1300} y1={420} x2={1140} y2={520} color={theme.governance} opacity={agreement} />
    <Panel x={735} y={610} width={450} height={250} color={theme.consumer} progress={agreement}>
      <div style={{fontSize: 28, fontWeight: 900}}>Data Agreement</div>
      <Field label="Parties" value="Sales ↔ Customer" />
      <Field label="Purpose" value="Customer Orders analytics" />
    </Panel>
  </Shell>;
};

const SourceBox = ({title, lines, x, y, color, p}: {title: string; lines: string[]; x: number; y: number; color: string; p: number}) => (
  <Panel x={x} y={y} width={330} height={190} color={color} progress={p}>
    <div style={{fontSize: 26, fontWeight: 900}}>{title}</div>
    <div style={{marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8}}>{lines.map((line) => <div key={line} style={{fontSize: 20, color: '#b8c6d6'}}>{line}</div>)}</div>
  </Panel>
);

const Step2 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sources = enter(frame, fps, 6);
  const read = enter(frame, fps, 28);
  const write = enter(frame, fps, 62);
  const meta = enter(frame, fps, 96);
  const flow = interpolate(frame, [34, 90], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <Shell step={2} title="Engineer & catalogue" subtitle="Move data with the two orchestrators while FabricOps captures metadata" color={theme.engineering} duration={stepDurations.step2}>
    <SourceBox x={90} y={230} title="Sales Lakehouse" lines={['Orders', 'Order Lines']} color={theme.engineering} p={sources} />
    <SourceBox x={90} y={500} title="Customer Lakehouse" lines={['Customers']} color={theme.engineering} p={sources} />
    <SourceBox x={90} y={770} title="Product Lakehouse" lines={['Products']} color={theme.engineering} p={sources} />

    <Panel x={535} y={350} width={330} height={180} color={theme.engineering} progress={read}>
      <div style={{fontSize: 26, color: '#93c7ff', fontWeight: 800}}>02 Pipeline</div>
      <div style={{fontSize: 31, marginTop: 18, fontFamily: 'ui-monospace, SFMono-Regular, monospace', fontWeight: 850}}>orchestrate_read()</div>
    </Panel>
    <Panel x={535} y={630} width={330} height={180} color="#52d6c6" progress={read}>
      <div style={{fontSize: 25, color: '#52d6c6', fontWeight: 850}}>Your PySpark</div>
      <div style={{fontSize: 27, marginTop: 15, fontWeight: 800}}>Join • Clean • Transform</div>
    </Panel>
    <Panel x={1010} y={490} width={360} height={190} color={theme.production} progress={write}>
      <div style={{fontSize: 26, color: '#72e6ad', fontWeight: 800}}>02 Pipeline</div>
      <div style={{fontSize: 31, marginTop: 18, fontFamily: 'ui-monospace, SFMono-Regular, monospace', fontWeight: 850}}>orchestrate_write()</div>
    </Panel>
    <SourceBox x={1490} y={490} title="Warehouse" lines={['CustomerOrders', 'Production-ready target']} color={theme.production} p={write} />

    <Arrow x1={420} y1={320} x2={535} y2={420} color={theme.engineering} opacity={flow} />
    <Arrow x1={420} y1={590} x2={535} y2={440} color={theme.engineering} opacity={flow} />
    <Arrow x1={420} y1={860} x2={535} y2={460} color={theme.engineering} opacity={flow} />
    <Arrow x1={865} y1={440} x2={700} y2={630} color="#52d6c6" opacity={flow} />
    <Arrow x1={865} y1={720} x2={1010} y2={585} color={theme.production} opacity={flow} />
    <Arrow x1={1370} y1={585} x2={1490} y2={585} color={theme.production} opacity={flow} />

    <Panel x={860} y={210} width={520} height={190} color={theme.consumer} progress={meta}>
      <div style={{fontSize: 25, color: '#ffbd76', fontWeight: 900}}>Built as the data moves</div>
      <div style={{display: 'flex', gap: 12, marginTop: 22}}>
        <Chip text="Profile" color="#52d6c6" />
        <Chip text="Lineage" color={theme.governance} />
        <Chip text="Catalogue" color={theme.consumer} />
      </div>
      <div style={{fontSize: 20, color: '#aebed3', marginTop: 22}}>CustomerOrders is now discoverable for governance.</div>
    </Panel>
  </Shell>;
};

const Step3 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const catalogue = enter(frame, fps, 4);
  const form = enter(frame, fps, 28);
  const pii = enter(frame, fps, 72);
  const dq1 = enter(frame, fps, 118);
  const dq2 = enter(frame, fps, 154);
  return <Shell step={3} title="Author the Data Contract" subtitle="Use the catalogue plus AI-assisted authoring to define expectations" color={theme.governance} duration={stepDurations.step3}>
    <Panel x={95} y={230} width={470} height={650} color={theme.consumer} progress={catalogue}>
      <div style={{fontSize: 25, color: '#ffbd76', fontWeight: 850}}>DATA CATALOGUE</div>
      <div style={{fontSize: 39, fontWeight: 930, marginTop: 12}}>CustomerOrders</div>
      <div style={{fontSize: 20, color: '#9fb0c5', marginTop: 12}}>Warehouse • dbo • Production target</div>
      <div style={{marginTop: 28}}><MiniTable rows={[
        ['Column', 'Type'],
        ['order_id', 'string'],
        ['customer_nric', 'string'],
        ['product_category', 'string'],
        ['quantity', 'int'],
      ]} /></div>
      <div style={{marginTop: 24, display: 'flex', flexWrap: 'wrap', gap: 10}}>
        <Chip text="Profile available" color="#52d6c6" />
        <Chip text="Lineage available" color={theme.governance} />
      </div>
    </Panel>

    <Panel x={635} y={210} width={570} height={690} color={theme.governance} progress={form}>
      <div style={{fontSize: 25, color: '#c5a8ff', fontWeight: 850}}>CONTRACT AUTHORING</div>
      <div style={{fontSize: 30, fontWeight: 900, marginTop: 10}}>Describe the governed table</div>
      <Field label="Description" value="One row per order line" />
      <Field label="Grain" value="order_id + product_id" />
      <Field label="Owner" value="Sales Data" />
      <div style={{marginTop: 26, fontSize: 23, fontWeight: 850}}>Column descriptions</div>
      <div style={{marginTop: 12, padding: 16, borderRadius: 14, background: '#0a1424', border: '1px solid #31465f', fontSize: 20, color: '#d6e2ef'}}>customer_nric — National identity number used for customer matching</div>
      <div style={{marginTop: 12, padding: 16, borderRadius: 14, background: '#0a1424', border: '1px solid #31465f', fontSize: 20, color: '#d6e2ef'}}>quantity — Number of units ordered</div>
    </Panel>

    <Panel x={1275} y={190} width={550} height={235} color={theme.consumer} progress={pii}>
      <div style={{fontSize: 23, color: '#ffbd76', fontWeight: 850}}>AI SENSITIVITY SUGGESTION</div>
      <div style={{fontSize: 28, fontWeight: 900, marginTop: 13}}>customer_nric</div>
      <div style={{display: 'flex', gap: 10, marginTop: 15}}>
        <Chip text="PII suggested" color={theme.consumer} />
        <Chip text="Mask" color={theme.production} />
        <Chip text="Restricted" color={theme.governance} />
      </div>
    </Panel>

    <Panel x={1275} y={460} width={550} height={205} color={theme.production} progress={dq1}>
      <div style={{fontSize: 21, color: '#72e6ad', fontWeight: 850}}>NATURAL LANGUAGE → DQ</div>
      <div style={{fontSize: 22, marginTop: 12, color: '#dce7f5'}}>“Product category must be Electronics, Home, or Sports.”</div>
      <div style={{marginTop: 15}}><Chip text="Allowed values: 3" color={theme.production} /></div>
    </Panel>

    <Panel x={1275} y={700} width={550} height={180} color={theme.production} progress={dq2}>
      <div style={{fontSize: 21, color: '#72e6ad', fontWeight: 850}}>NATURAL LANGUAGE → DQ</div>
      <div style={{fontSize: 22, marginTop: 12, color: '#dce7f5'}}>“Order quantity must be greater than zero.”</div>
      <div style={{marginTop: 15}}><Chip text="Range: min 1" color={theme.production} /></div>
    </Panel>
  </Shell>;
};

const Step4 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pipeline = enter(frame, fps, 4);
  const badRows = enter(frame, fps, 30);
  const treatment = enter(frame, fps, 74);
  const fail = enter(frame, fps, 118);
  const loopBack = enter(frame, fps, 230);
  const pass = enter(frame, fps, 330);
  const phase = frame < 235 ? 'validate' : frame < 325 ? 'fix' : 'pass';
  const statusColor = phase === 'pass' ? theme.production : phase === 'fix' ? theme.consumer : '#ff6b6b';
  return <Shell step={4} title="Validate with contract guardrails" subtitle="This is where Steps 3 and 4 become an iterative development loop" color={theme.engineering} duration={stepDurations.step4}>
    <Panel x={90} y={220} width={460} height={650} color={theme.engineering} progress={pipeline}>
      <div style={{fontSize: 24, color: '#93c7ff', fontWeight: 850}}>02 PIPELINE • VALIDATE</div>
      <div style={{fontSize: 31, marginTop: 14, fontWeight: 900}}>CustomerOrders</div>
      <div style={{marginTop: 26, display: 'flex', flexDirection: 'column', gap: 15}}>
        <Chip text="✓ Freshness" color={theme.production} />
        <Chip text="✓ Schema" color={theme.production} />
        <Chip text="Sensitive Data treatment" color={theme.consumer} />
        <Chip text="Data Quality" color={theme.governance} />
      </div>
      <div style={{marginTop: 34, padding: 18, border: `2px solid ${statusColor}99`, borderRadius: 16, background: `${statusColor}16`, color: statusColor, fontSize: 26, fontWeight: 900}}>
        {phase === 'validate' ? 'VALIDATION FAILED' : phase === 'fix' ? 'BACK TO STEP 3 / TRANSFORM' : 'VALIDATION PASSED'}
      </div>
    </Panel>

    <Panel x={610} y={220} width={560} height={360} color={theme.consumer} progress={badRows}>
      <div style={{fontSize: 25, fontWeight: 900}}>Incoming sample</div>
      <div style={{marginTop: 20}}><MiniTable highlight={1} rows={[
        ['NRIC', 'Category', 'Qty'],
        ['S1234567A', 'Toys', '0'],
        ['S7654321B', 'Home', '2'],
      ]} /></div>
      <div style={{display: 'flex', gap: 10, marginTop: 20}}>
        <Chip text="NRIC → mask" color={theme.consumer} />
        <Chip text="Toys ✕" color="#ff6b6b" />
        <Chip text="Qty 0 ✕" color="#ff6b6b" />
      </div>
    </Panel>

    <Panel x={610} y={630} width={560} height={240} color={theme.production} progress={treatment}>
      <div style={{fontSize: 23, color: '#72e6ad', fontWeight: 850}}>CONTRACT APPLIED</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: 16, marginTop: 24}}>
        <div style={{padding: 14, borderRadius: 12, background: '#0a1424', fontSize: 27, fontFamily: 'ui-monospace, monospace'}}>S1234567A</div>
        <div style={{fontSize: 34, color: theme.production}}>→</div>
        <div style={{padding: 14, borderRadius: 12, background: '#0a1424', fontSize: 27, fontFamily: 'ui-monospace, monospace'}}>S******7A</div>
      </div>
      <div style={{marginTop: 18, fontSize: 20, color: '#aebed3'}}>Because customer_nric was classified as PII with Mask treatment.</div>
    </Panel>

    <Panel x={1230} y={220} width={600} height={650} color={statusColor} progress={fail}>
      <div style={{fontSize: 25, color: statusColor, fontWeight: 900}}>{phase === 'pass' ? 'SECOND VALIDATION' : phase === 'fix' ? 'ITERATE' : 'GUARDRAIL RESULTS'}</div>

      {phase === 'validate' && <>
        <div style={{marginTop: 26, fontSize: 25, fontWeight: 850}}>Schema</div>
        <div style={{marginTop: 8}}><Chip text="✓ Pass" color={theme.production} /></div>
        <div style={{marginTop: 25, fontSize: 25, fontWeight: 850}}>Allowed values</div>
        <div style={{marginTop: 8}}><Chip text="✕ Toys is not allowed" color="#ff6b6b" /></div>
        <div style={{marginTop: 25, fontSize: 25, fontWeight: 850}}>Quantity range</div>
        <div style={{marginTop: 8}}><Chip text="✕ 0 is below minimum 1" color="#ff6b6b" /></div>
        <div style={{marginTop: 36, fontSize: 22, color: '#aebed3'}}>The contract is executable, not just documentation.</div>
      </>}

      {phase === 'fix' && <div style={{opacity: loopBack}}>
        <div style={{fontSize: 31, fontWeight: 900, marginTop: 34}}>Fix the transformation or adjust the contract</div>
        <div style={{marginTop: 34, display: 'flex', flexDirection: 'column', gap: 14}}>
          <Chip text="Map Toys → Home" color={theme.consumer} />
          <Chip text="Reject invalid quantity rows" color={theme.consumer} />
          <Chip text="Re-run validation" color={theme.engineering} />
        </div>
        <div style={{marginTop: 46, fontSize: 30, fontWeight: 900, color: '#f7f9fd'}}>Step 3 ↔ Step 4</div>
        <div style={{fontSize: 21, color: '#aebed3', marginTop: 10}}>Iterate until the governed data behaves as intended.</div>
      </div>}

      {phase === 'pass' && <div style={{opacity: pass}}>
        <div style={{marginTop: 30}}><MiniTable rows={[
          ['NRIC', 'Category', 'Qty'],
          ['S******7A', 'Home', '2'],
          ['S******1B', 'Home', '2'],
        ]} /></div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 14, marginTop: 30}}>
          <Chip text="✓ Schema" color={theme.production} />
          <Chip text="✓ Allowed values" color={theme.production} />
          <Chip text="✓ Quantity range" color={theme.production} />
          <Chip text="✓ Sensitive Data treatment" color={theme.production} />
        </div>
      </div>}
    </Panel>
  </Shell>;
};

const Step5 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const freeze = enter(frame, fps, 8);
  const activate = enter(frame, fps, 54);
  const deploy = enter(frame, fps, 100);
  const metadata = enter(frame, fps, 154);
  return <Shell step={5} title="Freeze, activate & promote" subtitle="Lock the approved contract, link it to the agreement, then promote the engineering assets" color={theme.governance} duration={stepDurations.step5}>
    <Panel x={110} y={260} width={460} height={520} color={theme.governance} progress={freeze}>
      <div style={{fontSize: 24, color: '#c5a8ff', fontWeight: 850}}>DATA CONTRACT v3</div>
      <div style={{fontSize: 36, fontWeight: 930, marginTop: 14}}>CustomerOrders</div>
      <div style={{marginTop: 32, display: 'flex', flexDirection: 'column', gap: 14}}>
        <Chip text="Draft" color="#8292a8" />
        <div style={{fontSize: 32, color: '#92a4b9', textAlign: 'center'}}>↓</div>
        <Chip text="Frozen" color={theme.consumer} />
        <div style={{fontSize: 32, color: '#92a4b9', textAlign: 'center'}}>↓</div>
        <Chip text="Activated" color={theme.production} />
      </div>
    </Panel>

    <Panel x={680} y={260} width={500} height={300} color={theme.consumer} progress={activate}>
      <div style={{fontSize: 24, color: '#ffbd76', fontWeight: 850}}>ACTIVATION</div>
      <div style={{fontSize: 28, fontWeight: 900, marginTop: 18}}>Link approved contract to its Data Agreement</div>
      <div style={{display: 'flex', justifyContent: 'center', gap: 12, marginTop: 30, alignItems: 'center'}}>
        <Chip text="Data Agreement v1" color={theme.consumer} />
        <div style={{fontSize: 30}}>↔</div>
        <Chip text="Contract v3" color={theme.governance} />
      </div>
    </Panel>

    <Panel x={680} y={610} width={500} height={220} color={theme.consumer} progress={metadata}>
      <div style={{fontSize: 23, fontWeight: 850, color: '#ffbd76'}}>GOVERNANCE METADATA</div>
      <div style={{fontSize: 25, marginTop: 15, fontWeight: 850}}>Activated contract remains in FabricOps metadata</div>
      <div style={{fontSize: 20, marginTop: 14, color: '#aebed3'}}>It is not “deployed” like notebook code.</div>
    </Panel>

    <Panel x={1300} y={260} width={510} height={570} color={theme.production} progress={deploy}>
      <div style={{fontSize: 24, color: '#72e6ad', fontWeight: 850}}>FABRIC DEPLOYMENT PIPELINE</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 18, alignItems: 'center', marginTop: 42}}>
        <div style={{padding: 20, border: '2px solid #4ea1ff88', borderRadius: 20, textAlign: 'center'}}>
          <div style={{fontSize: 24, fontWeight: 900, color: theme.engineering}}>Development</div>
          <div style={{fontSize: 20, marginTop: 18}}>00 Config</div>
          <div style={{fontSize: 20, marginTop: 9}}>02 Pipeline</div>
        </div>
        <div style={{fontSize: 44, color: theme.production}}>→</div>
        <div style={{padding: 20, border: '2px solid #38d99188', borderRadius: 20, textAlign: 'center'}}>
          <div style={{fontSize: 24, fontWeight: 900, color: theme.production}}>Production</div>
          <div style={{fontSize: 20, marginTop: 18}}>00 Config</div>
          <div style={{fontSize: 20, marginTop: 9}}>02 Pipeline</div>
        </div>
      </div>
      <div style={{marginTop: 40, fontSize: 21, color: '#aebed3', lineHeight: 1.4}}>Engineering assets move through Fabric deployment. The activated contract is resolved from governed metadata at runtime.</div>
    </Panel>
  </Shell>;
};

const Step6 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const run = enter(frame, fps, 6);
  const checks = enter(frame, fps, 45);
  const output = enter(frame, fps, 105);
  return <Shell step={6} title="Run in Production" subtitle="The same governed 02 Pipeline runs against the Production environment" color={theme.production} duration={stepDurations.step6}>
    <Panel x={130} y={300} width={480} height={430} color={theme.production} progress={run}>
      <div style={{fontSize: 24, color: '#72e6ad', fontWeight: 850}}>PRODUCTION</div>
      <div style={{fontSize: 34, fontWeight: 920, marginTop: 12}}>02 Pipeline</div>
      <div style={{marginTop: 28, padding: 16, borderRadius: 15, background: '#0a1424', fontFamily: 'ui-monospace, monospace', fontSize: 23}}>orchestrate_read()</div>
      <div style={{marginTop: 13, textAlign: 'center', color: '#92a4b9', fontSize: 28}}>↓ PySpark ↓</div>
      <div style={{marginTop: 13, padding: 16, borderRadius: 15, background: '#0a1424', fontFamily: 'ui-monospace, monospace', fontSize: 23}}>orchestrate_write()</div>
    </Panel>

    <Panel x={720} y={260} width={470} height={510} color={theme.governance} progress={checks}>
      <div style={{fontSize: 24, color: '#c5a8ff', fontWeight: 850}}>ACTIVE GOVERNANCE</div>
      <div style={{fontSize: 31, fontWeight: 900, marginTop: 14}}>CustomerOrders Contract v3</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 14, marginTop: 28}}>
        <Chip text="✓ Freshness" color={theme.production} />
        <Chip text="✓ Schema" color={theme.production} />
        <Chip text="✓ Sensitive Data" color={theme.production} />
        <Chip text="✓ Data Quality" color={theme.production} />
        <Chip text="✓ Guardrail coverage" color={theme.production} />
      </div>
    </Panel>

    <Arrow x1={610} y1={515} x2={720} y2={515} color={theme.production} opacity={checks} />
    <Arrow x1={1190} y1={515} x2={1330} y2={515} color={theme.production} opacity={output} />

    <Panel x={1330} y={330} width={450} height={360} color={theme.production} progress={output}>
      <div style={{fontSize: 24, color: '#72e6ad', fontWeight: 850}}>PRODUCTION OUTPUT</div>
      <div style={{fontSize: 34, fontWeight: 930, marginTop: 15}}>CustomerOrders</div>
      <div style={{fontSize: 21, color: '#aebed3', marginTop: 8}}>Warehouse • governed • ready to consume</div>
      <div style={{marginTop: 28}}><MiniTable rows={[
        ['Category', 'Qty', 'NRIC'],
        ['Home', '2', 'S******7A'],
        ['Sports', '1', 'S******1B'],
      ]} /></div>
    </Panel>
  </Shell>;
};

const Step7 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const table = enter(frame, fps, 4);
  const consumers = enter(frame, fps, 42);
  const items = [
    ['Power BI', '#f2c811'],
    ['Data Agent', theme.production],
    ['ML / Notebooks', theme.governance],
    ['Fabric / External Apps', theme.engineering],
  ] as const;
  return <Shell step={7} title="Consume the Production data" subtitle="The governed table becomes a reusable foundation for the Fabric ecosystem" color={theme.consumer} duration={stepDurations.step7}>
    <Panel x={685} y={260} width={550} height={330} color={theme.consumer} progress={table}>
      <div style={{fontSize: 25, color: '#ffbd76', fontWeight: 850}}>GOVERNED PRODUCTION TABLE</div>
      <div style={{fontSize: 43, fontWeight: 950, marginTop: 13}}>CustomerOrders</div>
      <div style={{marginTop: 25}}><MiniTable rows={[
        ['Category', 'Qty', 'NRIC'],
        ['Home', '2', 'S******7A'],
        ['Sports', '1', 'S******1B'],
      ]} /></div>
    </Panel>
    <div style={{position: 'absolute', left: 240, right: 240, top: 690, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24, opacity: consumers}}>
      {items.map(([label, color]) => <div key={label} style={{height: 150, border: `2px solid ${color}88`, borderRadius: 24, background: `${color}12`, display: 'grid', placeItems: 'center', color: '#f7f9fd', fontSize: 25, fontWeight: 850, boxShadow: `0 0 28px ${color}18`}}>{label}</div>)}
    </div>
    <Arrow x1={960} y1={590} x2={960} y2={690} color={theme.consumer} opacity={consumers} />
  </Shell>;
};

export const GuidedDemoJourney = () => (
  <AbsoluteFill>
    <Sequence from={starts.intro} durationInFrames={stepDurations.intro}><IntroScene /></Sequence>
    <Sequence from={starts.step1} durationInFrames={stepDurations.step1}><Step1 /></Sequence>
    <Sequence from={starts.step2} durationInFrames={stepDurations.step2}><Step2 /></Sequence>
    <Sequence from={starts.step3} durationInFrames={stepDurations.step3}><Step3 /></Sequence>
    <Sequence from={starts.step4} durationInFrames={stepDurations.step4}><Step4 /></Sequence>
    <Sequence from={starts.step5} durationInFrames={stepDurations.step5}><Step5 /></Sequence>
    <Sequence from={starts.step6} durationInFrames={stepDurations.step6}><Step6 /></Sequence>
    <Sequence from={starts.step7} durationInFrames={stepDurations.step7}><Step7 /></Sequence>
  </AbsoluteFill>
);
