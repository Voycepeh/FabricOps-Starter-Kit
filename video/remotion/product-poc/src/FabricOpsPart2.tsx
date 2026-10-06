import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {font, theme} from './theme';

const seconds = (value: number) => Math.round(value * 30);

const destinations = [
  {title: 'Power BI', subtitle: 'Reports & semantic models', color: '#f2c811', x: 135, y: 170, icon: 'bars'},
  {title: 'Machine Learning', subtitle: 'Models & predictions', color: '#a879ff', x: 135, y: 610, icon: 'nodes'},
  {title: 'Data Agents', subtitle: 'Natural language access', color: '#38d991', x: 1325, y: 170, icon: 'hex'},
  {title: 'External Apps', subtitle: 'APIs & applications', color: '#4ea1ff', x: 1325, y: 610, icon: 'grid'},
  {title: 'Fabric Apps', subtitle: 'Purpose-built experiences', color: '#52d6c6', x: 735, y: 790, icon: 'ribbon'},
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

const DestinationCard = ({title, subtitle, color, icon, progress}: {title: string; subtitle: string; color: string; icon: string; progress: number}) => (
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
      <div style={{fontSize: 42, fontWeight: 850, color: '#f7f9fd', lineHeight: 1.04}}>{title}</div>
      <div style={{fontSize: 24, marginTop: 14, color: '#aebed3', lineHeight: 1.2}}>{subtitle}</div>
    </div>
  </div>
);

const ProductionTable = ({progress}: {progress: number}) => (
  <div style={{marginTop: 30, width: 330, height: 190, borderRadius: 24, border: '3px solid #ffad5599', background: '#111e31', overflow: 'hidden', boxShadow: '0 0 36px #ffad5533', transform: `scale(${0.9 + 0.1 * progress})`}}>
    <div style={{height: 38, background: '#ffad55'}} />
    <div style={{display: 'grid', gridTemplateColumns: '1fr 1.4fr 1fr', gap: 10, padding: 18}}>
      {Array.from({length: 9}).map((_, i) => <div key={i} style={{height: 26, borderRadius: 7, background: i % 3 === 1 ? '#36506f' : '#28405e'}} />)}
    </div>
  </div>
);

const ConsumeScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cardEnter = spring({frame, fps, config: {damping: 18, stiffness: 92}});
  const zoom = interpolate(frame, [seconds(1.6), seconds(3.3)], [1, 1.26], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const shift = interpolate(frame, [seconds(1.6), seconds(3.3)], [0, -250], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const labelFade = interpolate(frame, [seconds(2.2), seconds(3.0)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const destinationsEnter = destinations.map((_, index) => spring({frame: frame - seconds(3.0) - index * 5, fps, config: {damping: 18, stiffness: 86}}));
  const connectorOpacity = interpolate(frame, [seconds(3.0), seconds(3.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return <AbsoluteFill>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 46%, #18365d 0%, #0b1830 36%, #060d19 78%)'}} />
    <div style={{position: 'absolute', left: '50%', top: 90, transform: 'translateX(-50%)', fontSize: 34, letterSpacing: 2.4, color: theme.consumer, fontWeight: 850, opacity: labelFade}}>STEP 7</div>

    <div style={{position: 'absolute', left: 960, top: 470, width: 560, height: 470, marginLeft: -280, marginTop: -235, transform: `translateY(${shift}px) scale(${zoom})`, transformOrigin: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderRadius: 36, border: `3px solid ${theme.consumer}`, background: `linear-gradient(145deg, ${theme.consumer}22, #0d192b 72%)`, boxShadow: `0 24px 80px #0009, 0 0 58px ${theme.consumer}33`, opacity: cardEnter}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        <div style={{width: 74, height: 74, borderRadius: 99, display: 'grid', placeItems: 'center', background: theme.consumer, color: '#07101f', fontSize: 42, fontWeight: 950}}>7</div>
        <div style={{fontSize: 50, fontWeight: 900, color: '#f7f9fd'}}>Consume the Production data</div>
      </div>
      <ProductionTable progress={cardEnter} />
    </div>

    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: connectorOpacity}}>
      <defs><marker id="consume-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#9db0c8" /></marker></defs>
      <path d="M760 390 C620 390 610 280 595 280" fill="none" stroke="#9db0c8" strokeWidth="5" markerEnd="url(#consume-arrow)" />
      <path d="M760 470 C620 520 610 715 595 715" fill="none" stroke="#9db0c8" strokeWidth="5" markerEnd="url(#consume-arrow)" />
      <path d="M1160 390 C1300 390 1310 280 1325 280" fill="none" stroke="#9db0c8" strokeWidth="5" markerEnd="url(#consume-arrow)" />
      <path d="M1160 470 C1300 520 1310 715 1325 715" fill="none" stroke="#9db0c8" strokeWidth="5" markerEnd="url(#consume-arrow)" />
      <path d="M960 610 V790" fill="none" stroke="#9db0c8" strokeWidth="5" markerEnd="url(#consume-arrow)" />
    </svg>

    {destinations.map((item, index) => <div key={item.title} style={{position: 'absolute', left: item.x, top: item.y}}><DestinationCard {...item} progress={destinationsEnter[index]} /></div>)}

    <div style={{position: 'absolute', left: 0, right: 0, bottom: 44, textAlign: 'center', color: '#c8d4e3', fontSize: 30, fontWeight: 650, opacity: interpolate(frame, [seconds(5.2), seconds(6.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
      Govern once. Build the foundation. Reuse the data across the Fabric ecosystem.
    </div>
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

export const FABRIC_OPS_PART_2_DURATION = seconds(16);

export const FabricOpsPart2 = () => (
  <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <Sequence from={0} durationInFrames={seconds(8)} premountFor={30}><ConsumeScene /></Sequence>
    <Sequence from={seconds(8)} durationInFrames={seconds(8)} premountFor={30}><AudienceScene /></Sequence>
  </AbsoluteFill>
);
