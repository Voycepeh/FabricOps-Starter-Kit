import {AbsoluteFill, Easing, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';
import {LifecycleScene, STEP_7_LABEL, StepCard} from './scenes/LifecycleScene';
import {SCENE_STARTS} from './videoConfig';

const seconds = (value: number) => Math.round(value * 30);

// Use the same mascot artwork as the documentation. Motion is limited to scene
// entrances; the robot remains stationary while viewers read the information.
const Mascot = ({pose, x, y, size = 260, delay = 0}: {pose: 'neutral' | 'writing' | 'scanning' | 'masking' | 'carrying' | 'pointing' | 'dev' | 'prod'; x: number; y: number; size?: number; delay?: number}) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [delay, delay + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return <Img src={staticFile(`mascots/robot-${pose}.png`)} style={{
    position: 'absolute', left: x, top: y, width: size, height: size,
    objectFit: 'contain', opacity: enter,
    transform: `translateY(${(1 - enter) * 22}px)`,
    filter: 'drop-shadow(0 12px 22px #0006)', pointerEvents: 'none',
  }} />;
};


const consumers = [
  {title: 'Dashboards', color: '#f2c811', left: 180, icon: 'bars'},
  {title: 'Data Agents', color: '#38d991', left: 600, icon: 'hex'},
  {title: 'Applications', color: '#52d6c6', left: 1020, icon: 'app'},
  {title: 'ML Models', color: '#a879ff', left: 1440, icon: 'nodes'},
] as const;

// Part 2 starts at the exact Part 1 lifecycle frame at 02:55.
const PART_1_HANDOFF_FRAME = seconds(175);
const LIFECYCLE_LOCAL_FRAME = PART_1_HANDOFF_FRAME - SCENE_STARTS.workflow;
const STEP_7_REVEAL = seconds(178.7) - PART_1_HANDOFF_FRAME;
const STEP_7_FOCUS_START = seconds(4.5);
const STEP_7_FOCUS_END = seconds(6.9);
const FOUNDATION_TRANSFORMATION_START = seconds(7);
const FOUNDATION_TRANSFORMATION_END = seconds(9.2);
const CONSUMER_REVEAL_START = seconds(9.8);
const CONSUMER_STAGGER_INTERVAL = seconds(0.35);
const CONSUMER_REVEAL_DURATION = seconds(0.55);
const CONSUMPTION_SCENE_HOLD = seconds(12);
const CONSUMPTION_SCENE_FADE_START = seconds(23.1);
const CONSUMPTION_SCENE_END = seconds(24);

const CardIcon = ({kind, color}: {kind: string; color: string}) => {
  if (kind === 'bars') {
    return <div style={{display: 'flex', alignItems: 'end', gap: 8, height: 64}}>
      {[34, 50, 64].map((height) => <div key={height} style={{width: 22, height, borderRadius: 7, background: color}} />)}
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
  return <div style={{width: 72, height: 58, borderRadius: 12, border: `4px solid ${color}`, overflow: 'hidden'}}>
    <div style={{height: 12, background: color}} />
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 18px)', gap: 7, padding: '8px 11px'}}>
      {[0, 1, 2, 3].map((i) => <div key={i} style={{height: 8, borderRadius: 4, background: i === 0 ? color : `${color}88`}} />)}
    </div>
  </div>;
};

const ConsumerCard = ({title, color, icon, progress}: {title: string; color: string; icon: string; progress: number}) => (
  <div style={{
    width: 300,
    height: 230,
    borderRadius: 24,
    border: `2px solid ${color}99`,
    background: 'linear-gradient(145deg, #14263d, #0d192b 76%)',
    boxShadow: '0 18px 38px #0007',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 22,
    padding: '24px 28px',
    boxSizing: 'border-box',
    opacity: progress,
    translate: `0 ${(1 - progress) * 18}px`,
  }}>
    <div style={{height: 72, display: 'grid', placeItems: 'center'}}><CardIcon kind={icon} color={color} /></div>
    <div style={{fontSize: 29, fontWeight: 820, color: '#f7f9fd', lineHeight: 1.12, textAlign: 'center'}}>{title}</div>
  </div>
);

const LifecycleConsumptionScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const stepEnter = spring({frame: frame - STEP_7_REVEAL, fps, durationInFrames: 18, config: {damping: 19, stiffness: 92}});
  const focus = interpolate(frame, [STEP_7_FOCUS_START, STEP_7_FOCUS_END], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const foundation = interpolate(frame, [FOUNDATION_TRANSFORMATION_START, FOUNDATION_TRANSFORMATION_END], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)});
  const pipelineOpacity = interpolate(frame, [FOUNDATION_TRANSFORMATION_START, FOUNDATION_TRANSFORMATION_START + seconds(0.6)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const holdLabelOpacity = interpolate(frame, [CONSUMPTION_SCENE_HOLD, CONSUMPTION_SCENE_HOLD + seconds(0.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const sceneOpacity = interpolate(frame, [CONSUMPTION_SCENE_FADE_START, CONSUMPTION_SCENE_END], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const cardScale = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [1, 3.1]) : interpolate(foundation, [0, 1], [3.1, 1]);
  const cardCenterX = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [1615, 960]) : 960;
  const cardCenterY = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [840, 540]) : interpolate(foundation, [0, 1], [540, 865]);
  const visualCardWidth = frame < FOUNDATION_TRANSFORMATION_START ? 340 * cardScale : interpolate(foundation, [0, 1], [1054, 1640]);
  const visualCardHeight = frame < FOUNDATION_TRANSFORMATION_START ? 150 * cardScale : interpolate(foundation, [0, 1], [465, 180]);
  const cardWidth = visualCardWidth / cardScale;
  const cardHeight = visualCardHeight / cardScale;
  const visualCircleSize = frame < FOUNDATION_TRANSFORMATION_START ? 62 * cardScale : interpolate(foundation, [0, 1], [192, 78]);
  const visualFontSize = frame < FOUNDATION_TRANSFORMATION_START ? 24 * cardScale : interpolate(foundation, [0, 1], [32, 42]);
  const lifecycleZoomScale = interpolate(focus, [0, 1], [1, 3.1]);

  return <AbsoluteFill style={{opacity: sceneOpacity}}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 38%, #18365d 0%, #0b1830 40%, #060d19 82%)'}} />
    <AbsoluteFill style={{opacity: pipelineOpacity, transform: `translate(${(960 - 1615) * focus}px, ${(540 - 840) * focus}px) scale(${lifecycleZoomScale})`, transformOrigin: '1615px 840px'}}>
      <Sequence from={-LIFECYCLE_LOCAL_FRAME} durationInFrames={LIFECYCLE_LOCAL_FRAME + CONSUMPTION_SCENE_END} premountFor={fps}>
        <LifecycleScene hideStep7 />
      </Sequence>
    </AbsoluteFill>

    {frame >= STEP_7_REVEAL ? <div style={{position: 'absolute', left: cardCenterX - cardWidth / 2, top: cardCenterY - cardHeight / 2, width: cardWidth, height: cardHeight, scale: cardScale, transformOrigin: '50% 50%', zIndex: 4}}>
      <StepCard
        number={7}
        label={STEP_7_LABEL}
        subtitle="Governed · Reliable · Fit for downstream use"
        subtitleFontSize={22 / cardScale}
        subtitleGap={9 / cardScale}
        subtitleOpacity={holdLabelOpacity}
        singleLineLabel={frame >= FOUNDATION_TRANSFORMATION_START}
        color={theme.consumer}
        enter={stepEnter}
        active
        width={cardWidth}
        height={cardHeight}
        borderRadius={interpolate(foundation, [0, 1], [28, 24])}
        circleSize={visualCircleSize / cardScale}
        fontSize={visualFontSize / cardScale}
        gap={interpolate(foundation, [0, 1], [22, 32]) / cardScale}
        horizontalPadding={interpolate(foundation, [0, 1], [25, 44]) / cardScale}
      />
      <div style={{position: 'absolute', left: 34, right: 34, bottom: -18, height: 18, borderRadius: '0 0 12px 12px', background: '#9a5c28', opacity: foundation}} />
    </div> : null}

    <Mascot pose="prod" x={840} y={580} size={190} delay={CONSUMER_REVEAL_START} />
    {consumers.map((consumer, index) => {
      const progress = interpolate(frame, [CONSUMER_REVEAL_START + index * CONSUMER_STAGGER_INTERVAL, CONSUMER_REVEAL_START + index * CONSUMER_STAGGER_INTERVAL + CONSUMER_REVEAL_DURATION], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)});
      return <div key={consumer.title} style={{position: 'absolute', left: consumer.left, top: 250, zIndex: 2}}>
        <ConsumerCard {...consumer} progress={progress} />
        <div style={{position: 'absolute', left: 148, top: 230, width: 4, height: 295, borderRadius: 4, background: `linear-gradient(${consumer.color}99, ${theme.consumer})`, opacity: progress * 0.72}} />
        <div style={{position: 'absolute', left: 140, top: 516, width: 20, height: 20, borderRadius: 4, border: `3px solid ${theme.consumer}`, background: '#0d192b', opacity: progress}} />
      </div>;
    })}

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
<Mascot pose="carrying" x={1540} y={90} size={230} delay={seconds(2)} />
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
    <Mascot pose={later ? "scanning" : "writing"} x={1580} y={65} size={190} delay={seconds(1)} />
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
    <Mascot pose="pointing" x={1470} y={650} size={300} delay={seconds(1)} />
    <div style={{textAlign: 'center', opacity: p, transform: `translateY(${(1 - p) * 40}px)`}}>
      <div style={{fontSize: 26, fontWeight: 850, color: '#72e6ad', letterSpacing: 2}}>FABRICOPS STARTER KIT</div>
      <div style={{fontSize: 75, fontWeight: 950, marginTop: 35}}>Plug-and-Play Pipelines.</div>
      <div style={{fontSize: 75, fontWeight: 950, color: '#c5a8ff'}}>Governance-as-Code.</div>
      <div style={{fontSize: 32, color: '#b9c8d9', marginTop: 44}}>A faster, more consistent data foundation for the age of AI.</div>
      <div style={{fontSize: 40, color: '#72e6ad', fontWeight: 850, marginTop: 48}}>See How FabricOps Works · Guided Demo</div>
      <div style={{fontSize: 27, color: '#aebed3', marginTop: 20}}>voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/</div>
    </div>
  </AbsoluteFill>;
};
const ENGINEERING_DURATION = seconds(12);
const GOVERNANCE_DURATION = seconds(18);
const CLOSING_DURATION = seconds(6);
const ENGINEERING_START = CONSUMPTION_SCENE_END;
const GOVERNANCE_START = ENGINEERING_START + ENGINEERING_DURATION;
const CLOSING_START = GOVERNANCE_START + GOVERNANCE_DURATION;
export const FABRIC_OPS_PART_2_DURATION = CLOSING_START + CLOSING_DURATION;

export const FabricOpsPart2 = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <Sequence from={0} durationInFrames={CONSUMPTION_SCENE_END} premountFor={30}><LifecycleConsumptionScene /></Sequence>
    <Sequence from={ENGINEERING_START} durationInFrames={ENGINEERING_DURATION} premountFor={30}><EngineeringTeaser /></Sequence>
    <Sequence from={GOVERNANCE_START} durationInFrames={GOVERNANCE_DURATION} premountFor={30}><GovernanceTeaser /></Sequence>
    <Sequence from={CLOSING_START} durationInFrames={CLOSING_DURATION} premountFor={30}><ClosingScene /></Sequence>
  </AbsoluteFill>
);
