import type {CSSProperties, ReactNode} from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type WorkspaceProps = {label: string; color: string; children?: ReactNode; style?: CSSProperties; compact?: boolean};
export const Workspace = ({label, color, children, style, compact}: WorkspaceProps) => (
  <div style={{position: 'absolute', borderRadius: compact ? 24 : 36, border: `1.5px solid ${color}66`, background: `linear-gradient(145deg, ${color}18, #0c1728e8 46%)`, boxShadow: `0 30px 80px #0008, inset 0 1px 0 #fff12`, overflow: 'hidden', ...style}}>
    <div style={{height: compact ? 8 : 11, background: `linear-gradient(90deg, ${color}, ${color}33)`}} />
    <div style={{display: 'flex', alignItems: 'center', gap: 13, padding: compact ? '19px 22px' : '27px 32px', color: theme.text, fontSize: compact ? 22 : 27, fontWeight: 650, letterSpacing: -0.5}}>
      <span style={{width: compact ? 10 : 13, height: compact ? 10 : 13, borderRadius: 99, background: color, boxShadow: `0 0 22px ${color}`}} />{label}
    </div>
    {children}
  </div>
);

export const Notebook = ({label = '02 Pipeline', color = theme.engineering}: {label?: string; color?: string}) => (
  <div style={{width: 240, height: 132, borderRadius: 18, background: '#111f35', border: `1px solid ${color}88`, boxShadow: '0 18px 42px #0007', position: 'relative', overflow: 'hidden'}}>
    <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 14, background: color}} />
    {[29, 53, 77, 101].map((y) => <span key={y} style={{position: 'absolute', left: 7, top: y, width: 14, height: 7, borderRadius: 5, background: '#c8d4e5'}} />)}
    <div style={{padding: '23px 25px 0 39px', color: theme.text, fontWeight: 700, fontSize: 20}}>{label}</div>
    <div style={{display: 'flex', gap: 8, padding: '18px 25px 0 39px'}}>{[36, 57, 42].map((w, i) => <span key={i} style={{height: 8, width: w, borderRadius: 9, background: `${color}${i === 1 ? '99' : '44'}`}} />)}</div>
    <div style={{margin: '13px 25px 0 39px', height: 7, width: 128, borderRadius: 9, background: '#8da0b83b'}} />
  </div>
);

export const Pipeline = ({color = theme.engineering}: {color?: string}) => (
  <div style={{width: 260, height: 112, borderRadius: 56, border: `1px solid ${color}77`, background: '#0d1a2dcc', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22, boxShadow: `0 18px 45px #0007`}}>
    {[0, 1, 2].map((i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: 20}}><span style={{width: i === 1 ? 36 : 27, height: i === 1 ? 36 : 27, borderRadius: i === 1 ? 10 : 99, border: `3px solid ${color}`, background: `${color}20`, boxShadow: i === 1 ? `0 0 22px ${color}88` : undefined}} />{i < 2 && <span style={{width: 24, height: 2, background: color}} />}</div>)}
  </div>
);

export const DataContract = ({active = false}: {active?: boolean}) => {
  const color = active ? theme.production : theme.governance;
  return <div style={{width: 248, height: 178, borderRadius: 22, padding: 25, boxSizing: 'border-box', color: theme.text, background: `linear-gradient(145deg, ${color}28, #111c31)`, border: `1.5px solid ${color}`, boxShadow: `0 22px 55px #0008, 0 0 30px ${color}25`, position: 'relative'}}>
    <div style={{position: 'absolute', right: 0, top: 0, width: 42, height: 42, clipPath: 'polygon(0 0,100% 100%,100% 0)', background: `${color}99`}} />
    <div style={{fontSize: 14, letterSpacing: 2.2, color, fontWeight: 800}}>DATA CONTRACT</div>
    <div style={{fontSize: 23, marginTop: 12, fontWeight: 700}}>Orders schema</div>
    <div style={{marginTop: 17, display: 'grid', gridTemplateColumns: '55px 1fr', gap: '9px 14px', fontSize: 13, color: theme.muted}}><span>order_id</span><span style={{color}}>string ✓</span><span>amount</span><span style={{color}}>decimal ✓</span></div>
  </div>;
};

export const EnvironmentConfig = () => <div style={{width: 190, borderRadius: 18, padding: '20px 24px', background: '#111b2a', border: `1px solid ${theme.neutral}66`, color: theme.text, boxShadow: '0 18px 38px #0007'}}><div style={{fontFamily: 'monospace', fontSize: 18, color: theme.neutral}}>00_env_config</div><div style={{height: 7, width: 120, borderRadius: 6, background: '#72819755', marginTop: 15}} /></div>;

export const StatusBadge = ({label = 'VALIDATION PASS'}: {label?: string}) => <div style={{display: 'flex', gap: 10, alignItems: 'center', border: `1px solid ${theme.production}99`, borderRadius: 99, padding: '11px 18px', color: theme.production, background: `${theme.production}15`, fontSize: 16, fontWeight: 800, letterSpacing: 1.1}}><span style={{fontSize: 20}}>✓</span>{label}</div>;

export const Connector = ({x1, y1, x2, y2, color, progress = 1, dashed = false, width = 3}: {x1: number; y1: number; x2: number; y2: number; color: string; progress?: number; dashed?: boolean; width?: number}) => {
  const dx = x2 - x1; const dy = y2 - y1; const length = Math.sqrt(dx * dx + dy * dy);
  return <svg style={{position: 'absolute', inset: 0, overflow: 'visible', pointerEvents: 'none'}} width="1920" height="1080"><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeLinecap="round" strokeDasharray={dashed ? `10 13` : length} strokeDashoffset={dashed ? 0 : length * (1 - progress)} opacity={0.78} /><circle cx={x1 + dx * progress} cy={y1 + dy * progress} r={width + 3} fill={color} opacity={progress < 1 ? 1 : 0} /></svg>;
};

export const ValidationPulse = ({start}: {start: number}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig();
  const p = spring({frame: frame - start, fps, config: {damping: 18, stiffness: 150}});
  return <div style={{position: 'absolute', width: 210, height: 210, borderRadius: 999, border: `3px solid ${theme.production}`, opacity: interpolate(p, [0, 1], [0.8, 0]), transform: `scale(${interpolate(p, [0, 1], [0.25, 1.15])})`, boxShadow: `0 0 44px ${theme.production}66`}} />;
};
