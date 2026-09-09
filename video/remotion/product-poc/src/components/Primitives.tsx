import type {CSSProperties, ReactNode} from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type WorkspaceProps = {
  label: string;
  color: string;
  children?: ReactNode;
  style?: CSSProperties;
  compact?: boolean;
};

export const Workspace = ({label, color, children, style, compact}: WorkspaceProps) => (
  <div
    style={{
      position: 'absolute',
      borderRadius: compact ? 24 : 36,
      border: `1.5px solid ${color}66`,
      background: `linear-gradient(145deg, ${color}18, #0c1728e8 46%)`,
      boxShadow: `0 30px 80px #0008, inset 0 1px 0 #fff12`,
      overflow: 'hidden',
      ...style,
    }}
  >
    <div style={{height: compact ? 8 : 11, background: `linear-gradient(90deg, ${color}, ${color}33)`}} />
    <div style={{display: 'flex', alignItems: 'center', gap: 13, padding: compact ? '19px 22px' : '27px 32px', color: theme.text, fontSize: compact ? 20 : 25, fontWeight: 650}}>
      <span style={{width: 11, height: 11, borderRadius: 99, background: color, boxShadow: `0 0 22px ${color}`}} />
      {label}
    </div>
    {children}
  </div>
);

export const Notebook = ({label = '02 Engineer', color = theme.engineering}: {label?: string; color?: string}) => (
  <div style={{width: 220, height: 122, borderRadius: 17, background: '#111f35', border: `1px solid ${color}88`, boxShadow: '0 18px 42px #0007', position: 'relative', overflow: 'hidden'}}>
    <div style={{position: 'absolute', inset: '0 auto 0 0', width: 13, background: color}} />
    {[27, 50, 73, 96].map((y) => <span key={y} style={{position: 'absolute', left: 6, top: y, width: 14, height: 6, borderRadius: 5, background: '#c8d4e5'}} />)}
    <div style={{padding: '22px 24px 0 36px', color: theme.text, fontWeight: 700, fontSize: 19}}>{label}</div>
    <div style={{display: 'flex', gap: 7, padding: '17px 24px 0 36px'}}>{[31, 52, 38].map((w, i) => <span key={i} style={{height: 7, width: w, borderRadius: 9, background: `${color}${i === 1 ? '99' : '44'}`}} />)}</div>
    <div style={{margin: '12px 24px 0 36px', height: 7, width: 120, borderRadius: 9, background: '#8da0b83b'}} />
  </div>
);

export const Pipeline = ({color = theme.engineering, compact = false}: {color?: string; compact?: boolean}) => (
  <div style={{width: compact ? 165 : 250, height: compact ? 68 : 104, borderRadius: 56, border: `1px solid ${color}77`, background: '#0d1a2de8', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: compact ? 10 : 18, boxShadow: '0 18px 45px #0007'}}>
    {[0, 1, 2].map((i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: compact ? 9 : 16}}><span style={{width: compact ? 17 : i === 1 ? 32 : 25, height: compact ? 17 : i === 1 ? 32 : 25, borderRadius: i === 1 ? 8 : 99, border: `${compact ? 2 : 3}px solid ${color}`, background: `${color}20`}} />{i < 2 && <span style={{width: compact ? 12 : 20, height: 2, background: color}} />}</div>)}
  </div>
);

export const DataContract = ({active = false, compact = false}: {active?: boolean; compact?: boolean}) => {
  const color = active ? theme.production : theme.governance;
  return <div style={{width: compact ? 184 : 238, height: compact ? 126 : 168, borderRadius: 20, padding: compact ? 18 : 24, boxSizing: 'border-box', color: theme.text, background: `linear-gradient(145deg, ${color}28, #111c31)`, border: `1.5px solid ${color}`, boxShadow: `0 22px 55px #0008, 0 0 30px ${color}25`, position: 'relative'}}>
    <div style={{position: 'absolute', right: 0, top: 0, width: compact ? 32 : 40, height: compact ? 32 : 40, clipPath: 'polygon(0 0,100% 100%,100% 0)', background: `${color}99`}} />
    <div style={{fontSize: compact ? 11 : 13, letterSpacing: 2, color, fontWeight: 800}}>DATA CONTRACT</div>
    <div style={{fontSize: compact ? 17 : 22, marginTop: 10, fontWeight: 700}}>Schema</div>
    <div style={{marginTop: 13, display: 'grid', gridTemplateColumns: compact ? '42px 1fr' : '54px 1fr', gap: '7px 12px', fontSize: compact ? 10 : 12, color: theme.muted}}><span>id</span><span style={{color}}>string ✓</span><span>value</span><span style={{color}}>decimal ✓</span></div>
  </div>;
};

export const EnvironmentConfig = () => <div style={{width: 180, borderRadius: 17, padding: '18px 22px', background: '#111b2a', border: `1px solid ${theme.neutral}66`, color: theme.text, boxShadow: '0 18px 38px #0007'}}><div style={{fontFamily: 'monospace', fontSize: 16, color: theme.neutral}}>00 Configure</div><div style={{height: 6, width: 112, borderRadius: 6, background: '#72819755', marginTop: 13}} /></div>;

export const StatusBadge = ({label = 'ALIGNED'}: {label?: string}) => <div style={{display: 'flex', gap: 9, alignItems: 'center', border: `1px solid ${theme.production}99`, borderRadius: 99, padding: '9px 15px', color: theme.production, background: `${theme.production}15`, fontSize: 14, fontWeight: 800, letterSpacing: 1}}><span>✓</span>{label}</div>;

type Point = {x: number; y: number};
type ConnectorProps = {from: Point; to: Point; color: string; progress?: number; route?: 'curve' | 'elbow'; lane?: number; width?: number; pulse?: boolean; opacity?: number};

export const Connector = ({from, to, color, progress = 1, route = 'curve', lane, width = 3, pulse = true, opacity = 0.82}: ConnectorProps) => {
  const bend = lane ?? (from.x + to.x) / 2;
  const path = route === 'elbow'
    ? `M ${from.x} ${from.y} H ${bend} V ${to.y} H ${to.x}`
    : `M ${from.x} ${from.y} C ${bend} ${from.y}, ${bend} ${to.y}, ${to.x} ${to.y}`;
  const pulsePoint = route === 'elbow'
    ? pointOnElbow(from, to, bend, progress)
    : pointOnBezier(from, to, bend, progress);
  return <svg style={{position: 'absolute', inset: 0, overflow: 'visible', pointerEvents: 'none'}} width="1920" height="1080">
    <path d={path} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - progress} opacity={opacity} />
    {pulse && progress > 0.02 && progress < 0.99 ? <circle cx={pulsePoint.x} cy={pulsePoint.y} r={width + 3} fill={color} style={{filter: `drop-shadow(0 0 7px ${color})`}} /> : null}
  </svg>;
};

const pointOnBezier = (from: Point, to: Point, bend: number, t: number): Point => {
  const u = 1 - t;
  return {
    x: u ** 3 * from.x + 3 * u ** 2 * t * bend + 3 * u * t ** 2 * bend + t ** 3 * to.x,
    y: u ** 3 * from.y + 3 * u ** 2 * t * from.y + 3 * u * t ** 2 * to.y + t ** 3 * to.y,
  };
};

const pointOnElbow = (from: Point, to: Point, bend: number, t: number): Point => {
  const lengths = [Math.abs(bend - from.x), Math.abs(to.y - from.y), Math.abs(to.x - bend)];
  const distance = t * lengths.reduce((sum, value) => sum + value, 0);
  if (distance <= lengths[0]) return {x: from.x + Math.sign(bend - from.x) * distance, y: from.y};
  if (distance <= lengths[0] + lengths[1]) return {x: bend, y: from.y + Math.sign(to.y - from.y) * (distance - lengths[0])};
  return {x: bend + Math.sign(to.x - bend) * (distance - lengths[0] - lengths[1]), y: to.y};
};

export const ValidationPulse = ({start, size = 180}: {start: number; size?: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - start, fps, config: {damping: 18, stiffness: 150}});
  return <div style={{position: 'absolute', width: size, height: size, borderRadius: 999, border: `3px solid ${theme.production}`, opacity: interpolate(p, [0, 1], [0.8, 0]), transform: `scale(${interpolate(p, [0, 1], [0.25, 1.15])})`, boxShadow: `0 0 44px ${theme.production}66`}} />;
};
