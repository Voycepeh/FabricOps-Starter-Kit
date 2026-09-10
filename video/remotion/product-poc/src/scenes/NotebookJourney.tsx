import {Notebook48Item} from '@fabric-msft/svg-icons';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type NotebookCardProps = {
  label: string;
  color: string;
  opacity?: number;
  transform?: string;
  subtitle?: string;
};

const NotebookCard = ({label, color, opacity = 1, transform, subtitle}: NotebookCardProps) => (
  <div style={{width: 400, height: 220, borderRadius: 38, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, background: `linear-gradient(145deg, ${color}32, #0d192b 72%)`, border: `3px solid ${color}bb`, boxShadow: `0 24px 60px #0009, 0 0 42px ${color}28`, opacity, transform}}>
    <Notebook48Item width={92} height={92} aria-hidden="true" />
    <div style={{fontSize: 34, fontWeight: 800, color: '#fff'}}>{label}</div>
    {subtitle ? <div style={{fontSize: 26, fontWeight: 750, color}}>{subtitle}</div> : null}
  </div>
);

const MapConnectors = ({opacity}: {opacity: number}) => <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity}}>
  <defs><marker id="notebook-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#8da0b8" /></marker></defs>
  <path d="M960 355 V485 H400 V650 M960 485 V650 M960 485 H1520 V650" fill="none" stroke="#8da0b8" strokeWidth="7" strokeLinejoin="round" markerEnd="url(#notebook-arrow)" />
</svg>;

const NotebookMap = ({opacity, governanceFocus = 0, pipelineFocus = 0, pipelineOpacity = 1}: {opacity: number; governanceFocus?: number; pipelineFocus?: number; pipelineOpacity?: number}) => (
  <div style={{position: 'absolute', inset: 0, opacity}}>
    <MapConnectors opacity={0.75 * (1 - Math.max(governanceFocus, pipelineFocus) * 0.65)} />
    <div style={{position: 'absolute', left: 760, top: 135}}><NotebookCard label="00_env_config" color={theme.neutral} opacity={1 - Math.max(governanceFocus, pipelineFocus) * 0.6} /></div>
    <div style={{position: 'absolute', left: 200, top: 650, zIndex: governanceFocus > 0 ? 3 : 1}}><NotebookCard label="01_governance" color={theme.governance} opacity={1 - pipelineFocus * 0.7} transform={`translate(${governanceFocus * 560}px, ${governanceFocus * -190}px) scale(${1 + governanceFocus * 0.38})`} /></div>
    <div style={{position: 'absolute', left: 760, top: 650, zIndex: pipelineFocus > 0 ? 3 : 1}}><NotebookCard label="02_pipeline" color={theme.engineering} opacity={pipelineOpacity * (1 - governanceFocus * 0.7)} transform={`translateY(${pipelineFocus * -190}px) scale(${1 + pipelineFocus * 0.38})`} /></div>
    <div style={{position: 'absolute', left: 1320, top: 650}}><NotebookCard label="99_explore" color={theme.consumer} opacity={1 - Math.max(governanceFocus, pipelineFocus) * 0.7} /></div>
  </div>
);

export const NotebookStructure = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 78}});
  const exit = interpolate(frame, [120, 150], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <NotebookMap opacity={enter * exit} />;
};

export const GovernanceFocus = () => {
  const frame = useCurrentFrame();
  const focus = interpolate(frame, [20, 55, 90, 120], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const exit = interpolate(frame, [120, 150], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <NotebookMap opacity={exit} governanceFocus={focus} />;
};

export const PipelineSplit = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const focus = interpolate(frame, [20, 55, 90, 125], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const split = interpolate(frame, [110, 145], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const exit = interpolate(frame, [180, 210], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const dev = spring({frame: frame - 112, fps, config: {damping: 19, stiffness: 84}});
  const production = spring({frame: frame - 124, fps, config: {damping: 19, stiffness: 84}});
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <NotebookMap opacity={1 - split} pipelineFocus={focus} pipelineOpacity={1 - split} />
    <div style={{position: 'absolute', left: 490, top: 430, opacity: split * dev, transform: `translateX(${(1 - dev) * 120}px)`}}><NotebookCard label="02_pipeline" color={theme.engineering} subtitle="Engineering Development" /></div>
    <div style={{position: 'absolute', left: 1030, top: 430, opacity: split * production, transform: `translateX(${(1 - production) * -120}px)`}}><NotebookCard label="02_pipeline" color={theme.production} subtitle="Engineering Production" /></div>
  </div>;
};
