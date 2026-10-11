import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';
import {LifecycleScene} from './scenes/LifecycleScene';
import {SCENE_STARTS} from './videoConfig';

const seconds = (value: number) => Math.round(value * 30);

const destinations = [
  {title: 'Power BI Dashboard', color: '#f2c811', x: 135, y: 185, icon: 'bars'},
  {title: 'Fabric Data Agents', color: '#38d991', x: 1325, y: 185, icon: 'hex'},
  {title: 'Machine Learning Models', color: '#a879ff', x: 135, y: 665, icon: 'nodes'},
  {title: 'Fabric Apps', color: '#52d6c6', x: 730, y: 785, icon: 'ribbon'},
  {title: 'External Apps', color: '#4ea1ff', x: 1325, y: 665, icon: 'grid'},
] as const;

const CardIcon = ({kind, color}: {kind: string; color: string}) => {
  if (kind === 'bars') {
    return <div style={{display: 'flex', alignItems: 'end', gap: 8, height: 64}}>
      {[34, 50, 64].map((height) => <div key={height} style={{width: 22, height, borderRadius: 7, background: color}} />)}
    </div>;
  }
  if (kind === 'grid') {
    return <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 26px)', gap: 8}}>
      {[0, 1, 2, 3].map((i) => <div key={i} style={{width: 26, height: 26, borderRadius: 6, border: `3px solid ${color}`, background: i === 0 || i === 3 ? color : 'transparent'}} />)}
    </div>;
  }
  if (kind === 'hex') {
    return <div style={{position: 'relative', width: 72, height: 62}}>
      <div style={{position: 'absolute', left: 24, top: 0, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, background: color}} />
      <div style={{position: 'absolute', left: 2, top: 30, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, border: `4px solid ${color}`}} />
      <div style={{position: 'absolute', left: 44, top: 30, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, background: color}} />
    </div>;
  }
  if (kind === 'nodes') {
    return <div style={{position: 'relative', width: 72, height: 64}}>
      {[{l:4,t:24},{l:28,t:4},{l:48,t:30},{l:26,t:44}].map((p, i) => <div key={i} style={{position: 'absolute', left: p.l, top: p.t, width: 18, height: 18, borderRadius: 99, background: color, boxShadow: `0 0 18px ${color}88`}} />)}
      <div style={{position: 'absolute', left: 12, top: 30, width: 46, height: 4, background: color, transform: 'rotate(-20deg)', transformOrigin: 'center'}} />
      <div style={{position: 'absolute', left: 26, top: 20, width: 4, height: 32, background: color}} />
    </div>;
  }
  return <div style={{width: 60, height: 60, borderRadius: 18, background: `linear-gradient(135deg, ${color}, #0b1830)`, transform: 'skewX(-16deg) rotate(-8deg)', boxShadow: `0 0 24px ${color}66`}} />;
};

const DestinationCard = ({title, color, icon, progress}: {title: string; color: string; icon: string; progress: number}) => (
  <div style={{
    width: 460,
    height: 210,
    borderRadius: 30,
    border: `3px solid ${color}aa`,
    background: `linear-gradient(145deg, ${color}18, #0d192b 74%)`,
    boxShadow: `0 20px 60px #0007, 0 0 38px ${color}22`,
    display: 'flex',
    alignItems: 'center',
    gap: 30,
    padding: '0 38px',
    boxSizing: 'border-box',
    opacity: progress,
    transform: `translateY(${(1 - progress) * 34}px) scale(${0.92 + progress * 0.08})`,
  }}>
    <div style={{width: 90, display: 'grid', placeItems: 'center'}}><CardIcon kind={icon} color={color} /></div>
    <div>
      <div style={{fontSize: 38, fontWeight: 850, color: '#f7f9fd', lineHeight: 1.08}}>{title}</div>
    </div>
  </div>
);

const ConsumptionGift = ({open}: {open: number}) => (
  <div style={{position: 'relative', width: 400, height: 250, perspective: 900}}>
    <div style={{position: 'absolute', left: 25, top: 74, width: 350, height: 170, borderRadius: 28, border: `3px solid ${theme.consumer}`, background: `linear-gradient(145deg, ${theme.consumer}2e, #0d192b 72%)`, boxShadow: `0 25px 70px #0008, 0 0 48px ${theme.consumer}55`, display: 'grid', placeItems: 'center'}}>
      <div style={{fontSize: 40, fontWeight: 900, color: '#f7f9fd'}}>7</div>
      <div style={{fontSize: 22, fontWeight: 750, color: '#f7f9fd', marginTop: -42}}>Production Data</div>
    </div>
    <div style={{position: 'absolute', left: 12, top: 48, width: 376, height: 74, borderRadius: 22, border: `3px solid ${theme.consumer}`, background: `linear-gradient(160deg, ${theme.consumer}, #bc7533)`, boxShadow: `0 0 ${20 + open * 34}px ${theme.consumer}88`, transformOrigin: '50% 15%', transform: `translateY(${-open * 100}px) rotateX(${-open * 56}deg) rotateZ(${-open * 7}deg)`}} />
  </div>
);

const ConsumeScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const open = spring({frame: frame - seconds(0.5), fps, config: {damping: 15, stiffness: 90}});
  const destinationsEnter = destinations.map((_, index) =>
    spring({frame: frame - seconds(1.15) - index * 10, fps, config: {damping: 16, stiffness: 85}}),
  );
  const titleEnter = interpolate(frame, [seconds(1.2), seconds(2.1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 46%, #18365d 0%, #0b1830 36%, #060d19 78%)'}} />
    <div style={{position: 'absolute', left: 760, top: 425, transform: 'scale(1)', zIndex: 2}}>
      <ConsumptionGift open={open} />
    </div>
    {destinations.map((item, index) => {
      const p = Math.max(0, Math.min(1, destinationsEnter[index]));
      const startX = 960 - 230;
      const startY = 510 - 105;
      const x = interpolate(p, [0, 1], [startX, item.x]);
      const y = interpolate(p, [0, 1], [startY, item.y]);
      const arc = Math.sin(p * Math.PI) * (190 + index * 18);
      return <div key={item.title} style={{position: 'absolute', left: x, top: y - arc, zIndex: 3, pointerEvents: 'none'}}>
        <DestinationCard {...item} progress={p} />
      </div>;
    })}
    <div style={{position: 'absolute', left: 0, right: 0, top: 56, textAlign: 'center', fontSize: 50, fontWeight: 850, color: '#f7f9fd', opacity: titleEnter}}>One governed table. Many ways to consume.</div>
  </AbsoluteFill>;
};


const Teaser = ({heading, subheading, children}: {heading: string; subheading: string; children: React.ReactNode}) => (
  <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 42%, #17345a, #0b1830 43%, #060d19 82%)'}}>
    <div style={{position: 'absolute', top: 68, left: 110, fontSize: 23, fontWeight: 850, letterSpacing: 2, color: theme.governance}}>FABRICOPS · GUIDED DEMO</div>
    <div style={{position: 'absolute', top: 120, left: 110, fontSize: 69, fontWeight: 950}}>{heading}</div>
    <div style={{position: 'absolute', top: 220, left: 110, fontSize: 29, color: '#aebed3'}}>{subheading}</div>
    {children}
  </AbsoluteFill>
);
const Tile = ({x, w, color, title, children}: {x: number; w: number; color: string; title: string; children: React.ReactNode}) => (
  <div style={{position: 'absolute', left: x, top: 340, width: w, height: 465, boxSizing: 'border-box', padding: 32, borderRadius: 28, border: `2px solid ${color}88`, background: 'linear-gradient(145deg, #142943, #0b1729)', boxShadow: `0 20px 60px #0007, 0 0 30px ${color}18`}}>
    <div style={{fontSize: 24, fontWeight: 850, color}}>{title}</div>
    {children}
  </div>
);
const EngineeringTeaser = () => {
  const frame = useCurrentFrame();
  const appear = (sec: number) => spring({frame: frame - seconds(sec), fps: 30, config: {damping: 18, stiffness: 85}});
  return <Teaser heading="Plug-and-Play Data Pipelines" subheading="02A Full Refresh · configure your sources, transform with PySpark, publish governed targets">
    <Tile x={90} w={465} color={theme.engineering} title="THREE GOVERNED READS">
      {['Bronze · orders', 'Bronze · products', 'Gold · order_history'].map((t, i) => <div key={t} style={{opacity: appear(i * 0.65), fontSize: 29, padding: '24px 10px', marginTop: 15, borderBottom: '1px solid #34465f'}}>{t}</div>)}
    </Tile>
    <Tile x={615} w={690} color="#52d6c6" title="02_pipeline · READ → TRANSFORM → WRITE">
      <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 29, lineHeight: 2.2, marginTop: 34}}>
        <div style={{opacity: appear(2), color: '#93c7ff'}}>orchestrate_read(...)</div>
        <div style={{opacity: appear(3), color: '#f7f9fd'}}># Your PySpark transformation</div>
        <div style={{opacity: appear(4), color: '#72e6ad'}}>orchestrate_write(...)</div>
      </div>
      <div style={{fontSize: 25, color: '#aebed3', marginTop: 25}}>Profiles · Lineage · Guardrail stages</div>
    </Tile>
    <Tile x={1365} w={465} color={theme.production} title="TWO GOVERNED WRITES">
      {['Silver · curated_orders', 'Gold · customer_summary'].map((t, i) => <div key={t} style={{opacity: appear(5 + i), fontSize: 27, padding: '25px 6px', marginTop: 27, borderBottom: '1px solid #34465f'}}>{t}</div>)}
    </Tile>
    <div style={{position: 'absolute', bottom: 125, left: 120, right: 120, display: 'flex', justifyContent: 'space-between', opacity: appear(7)}}>
      {['02A · Full Refresh / Overwrite', '02B · Incremental Append', '02C · SCD1 / SCD2'].map(t => <div key={t} style={{fontSize: 25, fontWeight: 800, padding: '18px 30px', borderRadius: 18, background: '#173354', color: '#c7e2ff'}}>{t}</div>)}
    </div>
  </Teaser>;
};
const GovernanceTeaser = () => {
  const frame = useCurrentFrame();
  const later = frame >= seconds(9);
  const enter = spring({frame: frame - seconds(2), fps: 30, config: {damping: 18, stiffness: 90}});
  return <Teaser heading="Governance-as-Code" subheading="01_governance · AI-assisted authoring, human-reviewed decisions, executable guardrails">
    {!later ? <>
      <Tile x={110} w={810} color={theme.consumer} title="SENSITIVE DATA · curated_orders">
        <div style={{fontSize: 43, fontWeight: 850, marginTop: 48}}>customer_id</div>
        <div style={{fontSize: 31, color: '#c5d2e3', marginTop: 30}}>Discover → Classify → Review</div>
        <div style={{fontSize: 36, fontWeight: 850, marginTop: 44, color: '#ffbd76', opacity: enter}}>Treatment: Mask</div>
        <div style={{fontSize: 25, marginTop: 20, color: '#aebed3'}}>Treatment applied before DQ and publication</div>
      </Tile>
      <Tile x={1000} w={810} color={theme.governance} title="BUSINESS LANGUAGE → EXECUTABLE RULE">
        <div style={{fontSize: 33, lineHeight: 1.4, marginTop: 45}}>"Modified datetime must be on or after order datetime."</div>
        <div style={{fontFamily: 'ui-monospace, monospace', fontSize: 30, marginTop: 42, color: '#c5a8ff', opacity: enter}}>column_relationship</div>
        <div style={{fontSize: 29, marginTop: 22, color: '#cbd5e1', opacity: enter}}>modified_datetime ≥ order_datetime</div>
      </Tile>
      <div style={{position: 'absolute', bottom: 110, left: 0, right: 0, textAlign: 'center', fontSize: 30, fontWeight: 800, color: '#c5a8ff'}}>Review and freeze the Data Contract</div>
    </> : <>
      <Tile x={110} w={810} color={theme.governance} title="STEP 4 · VALIDATE FROZEN CONTRACT">
        <div style={{fontSize: 36, marginTop: 58}}>Dirty row: modified_datetime earlier than order_datetime</div>
        <div style={{fontSize: 34, marginTop: 42, color: '#ff9c8c', fontWeight: 850}}>Rule violation detected</div>
      </Tile>
      <Tile x={1000} w={810} color={theme.production} title="INTEGRATED INTO ENGINEERING">
        <div style={{fontSize: 33, marginTop: 54}}>orchestrate_write()</div>
        <div style={{fontSize: 29, color: '#c5d2e3', marginTop: 30}}>Validate without publishing</div>
        <div style={{fontSize: 28, color: '#aebed3', marginTop: 28}}>Warn / Block policies</div>
        <div style={{fontSize: 29, color: '#72e6ad', marginTop: 28, fontWeight: 850}}>Corrected row → PASS</div>
      </Tile>
      <div style={{position: 'absolute', bottom: 110, left: 0, right: 0, textAlign: 'center', fontSize: 32, fontWeight: 800, color: '#c5a8ff'}}>Governance executes inside the pipeline.</div>
    </>}
  </Teaser>;
};
const ClosingScene = () => {
  const frame = useCurrentFrame();
  const p = spring({frame, fps: 30, config: {damping: 18, stiffness: 85}});
  return <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 44%, #15334d, #07101f 72%)', display: 'grid', placeItems: 'center'}}>
    <div style={{textAlign: 'center', opacity: p, transform: `translateY(${(1 - p) * 40}px)`}}>
      <div style={{fontSize: 26, fontWeight: 850, color: '#72e6ad', letterSpacing: 2}}>FABRICOPS STARTER KIT</div>
      <div style={{fontSize: 75, fontWeight: 950, marginTop: 35}}>Plug-and-Play Pipelines.</div>
      <div style={{fontSize: 75, fontWeight: 950, color: '#c5a8ff'}}>Governance-as-Code.</div>
      <div style={{fontSize: 32, color: '#b9c8d9', marginTop: 44}}>Start with 00_env_config and the 02A Full Refresh demo.</div>
      <div style={{fontSize: 40, color: '#72e6ad', fontWeight: 850, marginTop: 48}}>Try the FabricOps Guided Demo</div>
      <div style={{fontSize: 27, color: '#aebed3', marginTop: 20}}>voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/</div>
    </div>
  </AbsoluteFill>;
};
// Start from the exact Part 1 lifecycle frame at 02:55, using its original scene and timing.
const PART_1_HANDOFF_FRAME = seconds(175);
const LIFECYCLE_LOCAL_FRAME = PART_1_HANDOFF_FRAME - SCENE_STARTS.workflow;
const LIFECYCLE_CONTINUATION_DURATION = seconds(7);
const CONSUME_DURATION = seconds(8);
const ENGINEERING_DURATION = seconds(12);
const GOVERNANCE_DURATION = seconds(18);
const CLOSING_DURATION = seconds(6);
const CONSUME_START = LIFECYCLE_CONTINUATION_DURATION;
const ENGINEERING_START = CONSUME_START + CONSUME_DURATION;
const GOVERNANCE_START = ENGINEERING_START + ENGINEERING_DURATION;
const CLOSING_START = GOVERNANCE_START + GOVERNANCE_DURATION;
export const FABRIC_OPS_PART_2_DURATION = CLOSING_START + CLOSING_DURATION;

const LifecycleZoom = () => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [seconds(4.5), seconds(6.9)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const scale = interpolate(zoom, [0, 1], [1, 3.1]);
  // Step 7 is centered at x=1615, y=840 in the original 1920x1080 lifecycle.
  // Keep its original geometry and styling throughout the camera move.
  return <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)'}}>
    <AbsoluteFill style={{transform: `translate(${(960 - 1615) * zoom}px, ${(540 - 840) * zoom}px) scale(${scale})`, transformOrigin: '1615px 840px'}}>
      <Sequence from={-LIFECYCLE_LOCAL_FRAME} durationInFrames={LIFECYCLE_LOCAL_FRAME + LIFECYCLE_CONTINUATION_DURATION}><LifecycleScene /></Sequence>
    </AbsoluteFill>
  </AbsoluteFill>;
};

export const FabricOpsPart2 = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <Sequence from={0} durationInFrames={LIFECYCLE_CONTINUATION_DURATION}><LifecycleZoom /></Sequence>
    <Sequence from={CONSUME_START} durationInFrames={CONSUME_DURATION} premountFor={30}><ConsumeScene /></Sequence>
    <Sequence from={ENGINEERING_START} durationInFrames={ENGINEERING_DURATION} premountFor={30}><EngineeringTeaser /></Sequence>
    <Sequence from={GOVERNANCE_START} durationInFrames={GOVERNANCE_DURATION} premountFor={30}><GovernanceTeaser /></Sequence>
    <Sequence from={CLOSING_START} durationInFrames={CLOSING_DURATION} premountFor={30}><ClosingScene /></Sequence>
  </AbsoluteFill>
);
