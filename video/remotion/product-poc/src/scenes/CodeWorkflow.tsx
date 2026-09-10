import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {CodePanel, type CodeLine} from '../components/CodePanel';
import {theme} from '../theme';

const config: CodeLine[] = [
  {tokens: [{text: 'environment', color: theme.engineering}, {text: ' = "development"'}]},
  {tokens: [{text: 'source_path', color: theme.production}, {text: ' = paths.raw / "orders"'}]},
  {tokens: [{text: 'target_path', color: theme.production}, {text: ' = paths.curated / "orders"'}]},
  {tokens: [{text: 'metadata_path', color: theme.governance}, {text: ' = paths.metadata'}]},
];
const governance: CodeLine[] = [
  {tokens: [{text: 'contract', color: theme.governance}, {text: ' = DataContract('}]},
  {tokens: [{text: '    schema', color: theme.consumer}, {text: '=orders_schema,'}]},
  {tokens: [{text: '    freshness', color: theme.consumer}, {text: '="24 hours",'}]},
  {tokens: [{text: '    quality', color: theme.consumer}, {text: '=quality_rules,'}]},
  {tokens: [{text: '    sensitivity', color: theme.consumer}, {text: '="Confidential")'}]},
];
const pipeline: CodeLine[] = [
  {tokens: [{text: 'orders', color: theme.engineering}, {text: ' = read(source_path)'}]},
  {tokens: [{text: 'curated', color: theme.engineering}, {text: ' = transform(orders)'}]},
  {tokens: [{text: 'checked', color: theme.production}, {text: ' = validate(curated, checks, guardrails)'}]},
  {tokens: [{text: 'write', color: theme.consumer}, {text: '(checked, target_path)'}]},
];

const phases = [
  {title: '00_env_config', lines: config, start: 0, end: 165},
  {title: '01_governance · Data Contract', lines: governance, start: 150, end: 330},
  {title: '02_pipeline', lines: pipeline, start: 315, end: 510},
];

export const CodeWorkflow = () => {
  const frame = useCurrentFrame();
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center'}}>
    {phases.map((phase) => {
      const opacity = interpolate(frame, [phase.start, phase.start + 28, phase.end - 28, phase.end], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
      const progress = Math.max(0, frame - phase.start - 35);
      const activeLine = Math.min(phase.lines.length - 1, Math.floor(progress / 30));
      return <div key={phase.title} style={{position: 'absolute', opacity, transform: `translateX(${interpolate(opacity, [0, 1], [35, 0])}px) scale(${0.98 + opacity * 0.02})`}}><CodePanel title={phase.title} lines={phase.lines} activeLine={activeLine} /></div>;
    })}
  </div>;
};
