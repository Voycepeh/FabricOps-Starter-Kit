import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {GUIDED_DEMO_DURATION, GuidedDemoJourney} from './GuidedDemoJourney';
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

const audiences = [
  {title: 'Data Engineers', subtitle: 'Build and operate pipelines', color: theme.engineering, x: 115, y: 230},
  {title: 'Analysts', subtitle: 'Turn trusted data into insight', color: '#52d6c6', x: 115, y: 600},
  {title: 'Data Scientists', subtitle: 'Build models on governed data', color: theme.governance, x: 1305, y: 230},
  {title: 'Governance', subtitle: 'Define and oversee expectations', color: theme.consumer, x: 1305, y: 600},
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

const AudienceCard = ({title, subtitle, color, progress}: {title: string; subtitle: string; color: string; progress: number}) => (
  <div style={{width: 500, height: 220, borderRadius: 30, border: `3px solid ${color}88`, background: `linear-gradient(145deg, ${color}18, #0d192b 74%)`, boxShadow: `0 18px 50px #0006, 0 0 32px ${color}22`, padding: '40px 44px', boxSizing: 'border-box', opacity: progress, transform: `translateY(${(1 - progress) * 26}px) scale(${0.94 + progress * 0.06})`}}>
    <div style={{fontSize: 44, fontWeight: 900, color: '#f7f9fd'}}>{title}</div>
    <div style={{fontSize: 25, lineHeight: 1.25, color: '#aebed3', marginTop: 16}}>{subtitle}</div>
  </div>
);

const AudienceScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const title = spring({frame, fps, config: {damping: 18, stiffness: 90}});
  const hub = spring({frame: frame - 10, fps, config: {damping: 18, stiffness: 88}});
  const cardEnters = audiences.map((_, index) => spring({frame: frame - 18 - index * 5, fps, config: {damping: 19, stiffness: 85}}));
  const message = interpolate(frame, [seconds(2.2), seconds(3.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

  return <AbsoluteFill>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 48%, #163a49 0%, #0b1830 38%, #060d19 78%)'}} />
    <div style={{position: 'absolute', top: 72, left: 0, right: 0, textAlign: 'center', fontSize: 78, fontWeight: 950, color: '#f7f9fd', opacity: title, transform: `translateY(${(1 - title) * 30}px)`}}>Who is FabricOps for?</div>

    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: hub}}>
      {audiences.map((item) => <path key={item.title} d={item.x < 960 ? `M720 520 C620 520 650 ${item.y + 110} 615 ${item.y + 110}` : `M1200 520 C1300 520 1270 ${item.y + 110} 1305 ${item.y + 110}`} fill="none" stroke={item.color} strokeWidth="4" opacity="0.62" />)}
    </svg>

    <div style={{position: 'absolute', left: 760, top: 350, width: 400, height: 330, borderRadius: 42, border: '3px solid #38d991aa', background: 'linear-gradient(145deg, #38d99122, #0d192b 72%)', boxShadow: '0 0 64px #38d99133, 0 24px 70px #0008', display: 'grid', placeItems: 'center', opacity: hub, transform: `scale(${0.9 + hub * 0.1})`}}>
      <div style={{textAlign: 'center'}}>
        <div style={{fontSize: 62, fontWeight: 950, color: '#f7f9fd'}}>FabricOps</div>
        <div style={{fontSize: 26, marginTop: 14, color: '#a9bfd0'}}>Governed engineering foundation</div>
      </div>
    </div>

    {audiences.map((item, index) => <div key={item.title} style={{position: 'absolute', left: item.x, top: item.y}}><AudienceCard {...item} progress={cardEnters[index]} /></div>)}

    <div style={{position: 'absolute', left: 245, right: 245, bottom: 70, textAlign: 'center', opacity: message}}>
      <div style={{fontSize: 38, lineHeight: 1.28, fontWeight: 700, color: '#f7f9fd'}}>
        For data teams that already have data available and want to use the Fabric ecosystem
        <span style={{color: '#63e8b1'}}> without rebuilding governance and engineering foundations from scratch.</span>
      </div>
      <div style={{fontSize: 29, lineHeight: 1.3, color: '#aebed3', marginTop: 22}}>
        Especially useful when the number of decisions, services and setup steps feels overwhelming.
      </div>
    </div>
  </AbsoluteFill>;
};

// Start from the exact Part 1 lifecycle frame at 02:55, using its original scene and timing.
const PART_1_HANDOFF_FRAME = seconds(175);
const LIFECYCLE_LOCAL_FRAME = PART_1_HANDOFF_FRAME - SCENE_STARTS.workflow;
const LIFECYCLE_CONTINUATION_DURATION = seconds(7);
const CONSUME_DURATION = seconds(8);
const AUDIENCE_DURATION = seconds(8);
const CONSUME_START = LIFECYCLE_CONTINUATION_DURATION;
const GUIDED_DEMO_START = CONSUME_START + CONSUME_DURATION;
const AUDIENCE_START = GUIDED_DEMO_START + GUIDED_DEMO_DURATION;

export const FABRIC_OPS_PART_2_DURATION = AUDIENCE_START + AUDIENCE_DURATION;

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
    <Sequence from={GUIDED_DEMO_START} durationInFrames={GUIDED_DEMO_DURATION} premountFor={30}><GuidedDemoJourney /></Sequence>
    <Sequence from={AUDIENCE_START} durationInFrames={AUDIENCE_DURATION} premountFor={30}><AudienceScene /></Sequence>
  </AbsoluteFill>
);
