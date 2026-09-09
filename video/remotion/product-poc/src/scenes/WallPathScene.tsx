import type {ReactNode} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ConceptChip, DataStore, LineageGraph, ParallelFlow, QualityCheck} from '../components/Concepts';
import {Connector, DataContract, EnvironmentConfig, Notebook, Pipeline} from '../components/Primitives';
import {theme} from '../theme';

const Tile = ({children, x, y, depth, delay = 0}: {children: ReactNode; x: number; y: number; depth: number; delay?: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - delay, fps, config: {damping: 20, stiffness: 75}});
  const simplify = interpolate(frame, [230, 330], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', left: x, top: y, opacity: enter * interpolate(simplify, [0, 1], [1, depth < 0.7 ? 0.12 : 0.28]), filter: `blur(${(1 - enter) * 8 + simplify * (1-depth) * 3}px)`, transform: `translateY(${(1-enter)*70 + simplify*(1-depth)*30}px) scale(${0.86 + enter*0.14 - simplify*(1-depth)*0.08})`}}>{children}</div>;
};

const Marker = ({x, y, label, color, progress}: {x: number; y: number; label: string; color: string; progress: number}) => <div style={{position: 'absolute', left: x - 28, top: y - 28, width: 56, height: 56, borderRadius: 99, display: 'grid', placeItems: 'center', background: '#0b1729', border: `2px solid ${color}`, color, fontSize: 13, fontWeight: 850, opacity: progress, transform: `scale(${0.65 + progress * 0.35})`, boxShadow: `0 0 32px ${color}55`, zIndex: 6}}>{label}</div>;

export const WallPathScene = () => {
  const frame = useCurrentFrame();
  const select = interpolate(frame, [225, 285], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const path = interpolate(frame, [278, 415], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const question = interpolate(frame, [105, 140, 205, 235], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const points = [{x: 435, y: 560, n: '00', c: theme.neutral}, {x: 760, y: 465, n: '01', c: theme.governance}, {x: 1090, y: 570, n: '02', c: theme.engineering}, {x: 1440, y: 430, n: '99', c: theme.consumer}];
  return <div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', inset: -30, transform: `perspective(1000px) rotateX(2deg) scale(${interpolate(frame, [0, 450], [1.08, .98])})`}}>
      <Tile x={90} y={120} depth={0.9}><Notebook label="Notebook" /></Tile>
      <Tile x={420} y={105} depth={0.65} delay={5}><Pipeline /></Tile>
      <Tile x={745} y={92} depth={0.85} delay={10}><DataStore label="Lakehouse" /></Tile>
      <Tile x={1035} y={90} depth={0.55} delay={15}><ConceptChip label="SQL" style={{position:'relative'}} /></Tile>
      <Tile x={1225} y={90} depth={0.8} delay={20}><DataStore label="Warehouse" color={theme.consumer} /></Tile>
      <Tile x={1530} y={120} depth={0.55} delay={24}><ConceptChip label="Python" style={{position:'relative'}} /></Tile>
      <Tile x={180} y={350} depth={0.55} delay={28}><LineageGraph /></Tile>
      <Tile x={520} y={340} depth={0.88} delay={31}><EnvironmentConfig /></Tile>
      <Tile x={815} y={300} depth={0.65} delay={34}><ParallelFlow /></Tile>
      <Tile x={1185} y={315} depth={0.9} delay={37}><DataContract compact /></Tile>
      <Tile x={1515} y={335} depth={0.6} delay={40}><QualityCheck /></Tile>
      <Tile x={75} y={660} depth={0.62} delay={43}><ConceptChip label="PySpark" style={{position:'relative'}} /></Tile>
      <Tile x={325} y={645} depth={0.8} delay={46}><DataStore label="Metadata" color={theme.governance} /></Tile>
      <Tile x={655} y={700} depth={0.5} delay={49}><ConceptChip label="R" style={{position:'relative'}} /></Tile>
      <Tile x={850} y={650} depth={0.68} delay={52}><QualityCheck /></Tile>
      <Tile x={1090} y={680} depth={0.52} delay={55}><ConceptChip label="Incremental Refresh" color={theme.production} style={{position:'relative'}} /></Tile>
      <Tile x={1470} y={655} depth={0.78} delay={58}><Pipeline color={theme.production} compact /></Tile>
      <Tile x={1650} y={560} depth={0.5} delay={61}><ConceptChip label="Monitoring" color={theme.consumer} style={{position:'relative'}} /></Tile>
      <Tile x={150} y={880} depth={0.48} delay={64}><ConceptChip label="Dataflow" style={{position:'relative'}} /></Tile>
      <Tile x={660} y={875} depth={0.7} delay={67}><ConceptChip label="Governance" color={theme.governance} style={{position:'relative'}} /></Tile>
      <Tile x={1310} y={865} depth={0.45} delay={70}><ConceptChip label="Production" color={theme.production} style={{position:'relative'}} /></Tile>
    </div>
    <div style={{position: 'absolute', left: 0, right: 0, top: 505, textAlign: 'center', color: '#d9e3f0', fontSize: 22, letterSpacing: 1, opacity: question}}>Where do I start?</div>
    <div style={{position: 'absolute', left: 260, top: 220, color: theme.text, opacity: select, zIndex: 7}}><span style={{fontSize: 38, fontWeight: 760}}>Fabric<span style={{color: theme.production}}>Ops</span></span><span style={{fontSize: 15, color: theme.muted, marginLeft: 18}}>an opinionated path</span></div>
    <Connector from={points[0]} to={points[1]} color={theme.governance} progress={Math.min(1, path * 3)} route="curve" opacity={0.92} />
    <Connector from={points[1]} to={points[2]} color={theme.engineering} progress={Math.max(0, Math.min(1, path * 3 - 1))} route="curve" opacity={0.92} />
    <Connector from={points[2]} to={points[3]} color={theme.consumer} progress={Math.max(0, Math.min(1, path * 3 - 2))} route="curve" opacity={0.92} />
    {points.map((p, i) => <Marker key={p.n} x={p.x} y={p.y} label={p.n} color={p.c} progress={Math.max(0, Math.min(1, select * 2 - i * .18))} />)}
    <div style={{position:'absolute',left:455,top:625,display:'flex',gap:12,opacity:path,zIndex:7}}>{['config driven','code first','notebook first','governance as code'].map((label,i)=><span key={label} style={{padding:'7px 11px',borderRadius:99,border:'1px solid #60728d66',background:'#0a1525dd',color:i===3?'#c9aefe':'#9fb0c5',fontSize:12}}>{label}</span>)}</div>
  </div>;
};
