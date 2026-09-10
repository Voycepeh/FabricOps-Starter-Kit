import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

const workspaces = [
  {name: 'Governance', color: theme.governance, x: 55},
  {name: 'Engineering Development', color: theme.engineering, x: 510},
  {name: 'Engineering Production', color: theme.production, x: 965},
  {name: 'Consumer', color: theme.consumer, x: 1420},
];

const steps = [
  {number: 1, label: 'Data Stewards &\nData Agreement', color: theme.governance, x: 80, y: 205},
  {number: 2, label: 'ETL, Profile &\nCatalogue', color: theme.engineering, x: 535, y: 205},
  {number: 3, label: 'Author\nData Contract', color: theme.governance, x: 80, y: 485},
  {number: 4, label: 'ETL with Contract\nGuardrails', color: theme.engineering, x: 535, y: 485},
  {number: 5, label: 'Activate &\nPromote', color: theme.governance, x: 80, y: 765},
  {number: 6, label: 'Run Production\nPipeline', color: theme.production, x: 990, y: 765},
  {number: 7, label: 'Consume approved\nProduction data', color: theme.consumer, x: 1445, y: 765},
];

const connectors = [
  {d: 'M420 280 H535', delay: 65},
  {d: 'M710 355 C710 420 255 420 255 485', delay: 115},
  {d: 'M420 560 H535', delay: 165},
  {d: 'M710 635 C710 700 255 700 255 765', delay: 265},
  {d: 'M420 840 H990', delay: 315},
  {d: 'M1330 840 H1445', delay: 365},
];

const StepCard = ({number, label, color, enter, active}: {number: number; label: string; color: string; enter: number; active: boolean}) => (
  <div style={{width: 340, height: 150, borderRadius: 28, display: 'flex', alignItems: 'center', gap: 22, padding: '0 25px', boxSizing: 'border-box', background: `linear-gradient(145deg, ${color}2e, #0d192b 72%)`, border: `3px solid ${active ? color : `${color}88`}`, boxShadow: active ? `0 0 48px ${color}55` : '0 18px 40px #0007', opacity: enter, transform: `scale(${0.86 + enter * 0.14})`}}>
    <div style={{width: 62, height: 62, flex: '0 0 auto', borderRadius: 99, display: 'grid', placeItems: 'center', background: color, color: '#07101f', fontSize: 34, fontWeight: 900}}>{number}</div>
    <div style={{whiteSpace: 'pre-line', color: '#f7f9fd', fontSize: 27, lineHeight: 1.15, fontWeight: 720}}>{label}</div>
  </div>
);

export const LifecycleScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const exit = interpolate(frame, [505, 540], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const loop = interpolate(frame, [205, 245], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    {workspaces.map((workspace, index) => {
      const enter = spring({frame: frame - index * 32, fps, config: {damping: 20, stiffness: 82}});
      return <div key={workspace.name} style={{position: 'absolute', left: workspace.x, top: 58, width: 445, height: 950, borderRadius: 34, border: `2px solid ${workspace.color}45`, background: `${workspace.color}0b`, opacity: enter}}><div style={{paddingTop: 28, textAlign: 'center', color: workspace.color, fontSize: 28, fontWeight: 800}}>{workspace.name}<br />Workspace</div></div>;
    })}
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      <defs><marker id="lifecycle-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#9db0c8" /></marker></defs>
      {connectors.map((connector) => {
        const draw = interpolate(frame, [connector.delay, connector.delay + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <path key={connector.d} d={connector.d} fill="none" stroke="#8198b5" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - draw} markerEnd={draw > 0.96 ? 'url(#lifecycle-arrow)' : undefined} />;
      })}
      <path d="M535 610 C500 685 455 685 420 610" fill="none" stroke={theme.governance} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - loop} markerEnd={loop > 0.96 ? 'url(#lifecycle-arrow)' : undefined} />
      <path d="M420 510 C455 435 500 435 535 510" fill="none" stroke={theme.engineering} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - loop} markerEnd={loop > 0.96 ? 'url(#lifecycle-arrow)' : undefined} />
    </svg>
    {steps.map((step, index) => {
      const enter = spring({frame: frame - 25 - index * 50, fps, config: {damping: 19, stiffness: 92}});
      const active = frame >= 25 + index * 50 && frame < 75 + index * 50;
      return <div key={step.number} style={{position: 'absolute', left: step.x, top: step.y}}><StepCard {...step} enter={enter} active={active} /></div>;
    })}
    <div style={{position: 'absolute', left: 357, top: 674, width: 300, textAlign: 'center', color: '#dce7f5', fontSize: 24, fontWeight: 720, opacity: loop}}>Iterate until validations pass</div>
  </div>;
};
