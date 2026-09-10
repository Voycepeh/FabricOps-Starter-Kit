import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {NotebookNode} from '../components/NotebookNode';
import {theme} from '../theme';

const nodes = [
  {name: '00_env_config', color: theme.neutral, x: 235, y: 175},
  {name: '01_governance', color: theme.governance, x: 1355, y: 175},
  {name: '02_pipeline', color: theme.engineering, x: 1355, y: 695},
  {name: '99_explore', color: theme.consumer, x: 235, y: 695},
];

export const NotebookWorkflow = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const exit = interpolate(frame, [380, 420], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lineProgress = interpolate(frame, [120, 230], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pulse = interpolate(frame, [235, 350], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const paths = ['M565 280 H1355', 'M1520 385 V695', 'M1355 800 H565', 'M400 695 V385'];
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <defs><marker id="workflow-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#83a0c4" /></marker></defs>
      {paths.map((path, index) => {
        const segment = Math.max(0, Math.min(1, lineProgress * 4 - index));
        return <path key={path} d={path} fill="none" stroke="#5f7899" strokeWidth="8" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - segment} opacity="0.75" markerEnd={segment > 0.96 ? 'url(#workflow-arrow)' : undefined} />;
      })}
    </svg>
    {nodes.map((node, index) => {
      const enter = spring({frame: frame - 18 - index * 24, fps, config: {damping: 18, stiffness: 88}});
      const active = pulse > index * 0.25 && pulse < (index + 1) * 0.25 + 0.1;
      return <div key={node.name} style={{position: 'absolute', left: node.x, top: node.y, opacity: enter, transform: `scale(${0.8 + enter * 0.2})`}}><NotebookNode name={node.name} color={node.color} active={active} /></div>;
    })}
    <div style={{position: 'absolute', left: 700, top: 458, width: 520, textAlign: 'center', fontSize: 68, fontWeight: 810, lineHeight: 1.08}}>How FabricOps<br /><span style={{color: theme.production}}>works</span></div>
  </div>;
};
