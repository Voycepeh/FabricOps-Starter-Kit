import type {ReactNode} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const LAYOUT = {
  environment: {left: 745, top: 250, width: 430, height: 180},
  governance: {left: 260, top: 620, width: 320, height: 190},
  contract: {left: 810, top: 580, width: 300, height: 280},
  pipeline: {left: 1340, top: 620, width: 320, height: 190},
} as const;

const revealStyle = (progress: number, distance = 20) => ({
  opacity: progress,
  transform: `translateY(${(1 - progress) * distance}px)`,
});

const NotebookGlyph = ({color}: {color: string}) => (
  <div style={{position: 'relative', width: 44, height: 48, flex: '0 0 auto'}}>
    <div style={{position: 'absolute', inset: 0, border: `2px solid ${color}`, borderRadius: 8, background: `${color}12`}} />
    <div style={{position: 'absolute', left: -5, top: 9, width: 10, height: 4, borderRadius: 4, background: color, boxShadow: `0 10px 0 ${color}, 0 20px 0 ${color}`}} />
    <div style={{position: 'absolute', left: 12, right: 8, top: 14, height: 3, borderRadius: 3, background: color, boxShadow: `0 9px 0 ${color}99, 0 18px 0 ${color}66`}} />
  </div>
);

const NotebookCard = ({title, subtitle, color, progress, foundation = false, footer}: {
  title: string;
  subtitle: string;
  color: string;
  progress: number;
  foundation?: boolean;
  footer?: ReactNode;
}) => {
  const box = foundation ? LAYOUT.environment : title === '01_governance' ? LAYOUT.governance : LAYOUT.pipeline;
  return (
    <div style={{position: 'absolute', ...box, boxSizing: 'border-box', borderRadius: 26, padding: foundation ? '30px 38px' : '30px 32px', background: foundation ? 'linear-gradient(145deg, #17263c, #0b1525)' : `linear-gradient(145deg, ${color}24, #0b1525 74%)`, border: `2px solid ${color}${foundation ? 'aa' : 'cc'}`, boxShadow: foundation ? '0 24px 60px #0008, inset 0 1px 0 #ffffff16' : `0 22px 55px #0008, 0 0 34px ${color}16`, ...revealStyle(progress)}}>
      <div style={{position: 'absolute', top: -2, left: 30, width: 76, height: 9, borderRadius: '0 0 8px 8px', background: color}} />
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        <NotebookGlyph color={color} />
        <div style={{minWidth: 0}}>
          <div style={{fontSize: foundation ? 34 : 30, lineHeight: 1.15, fontWeight: 800, color: theme.text, whiteSpace: 'nowrap'}}>{title}</div>
          <div style={{marginTop: 10, fontSize: 21, lineHeight: 1.2, fontWeight: 650, color}}>{subtitle}</div>
        </div>
      </div>
      {footer}
    </div>
  );
};

const ContractCard = ({progress}: {progress: number}) => {
  const guardrails = ['Schema', 'Freshness', 'Data Quality', 'Sensitivity', 'Source Stability'];
  return (
    <div style={{position: 'absolute', ...LAYOUT.contract, boxSizing: 'border-box', borderRadius: 22, padding: '25px 28px', background: 'linear-gradient(155deg, #252b4c, #111a2d 72%)', border: '2px solid #b6a8f4', boxShadow: '0 28px 70px #0009, inset 0 1px 0 #ffffff1c', ...revealStyle(progress, 14)}}>
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <div style={{fontSize: 30, lineHeight: 1.1, fontWeight: 820, color: theme.text}}>Data Contract</div>
        <div style={{width: 34, height: 34, borderRadius: 9, display: 'grid', placeItems: 'center', background: '#a995ec22', color: '#c9bcff', fontSize: 21}}>◇</div>
      </div>
      <div style={{marginTop: 18, marginBottom: 9, color: '#bdb2f4', fontSize: 18, lineHeight: 1.2, fontWeight: 760, letterSpacing: 1.3, textTransform: 'uppercase'}}>Guardrails</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 4}}>
        {guardrails.map((item) => (
          <div key={item} style={{height: 28, display: 'flex', alignItems: 'center', gap: 11, borderTop: '1px solid #ffffff10', color: '#e9edf6', fontSize: 20, lineHeight: 1.2, fontWeight: 560}}>
            <span style={{width: 6, height: 6, borderRadius: 6, background: '#aa95ee', boxShadow: '0 0 10px #aa95ee88'}} />{item}
          </div>
        ))}
      </div>
    </div>
  );
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, timing} = VIDEO_CONFIG;
  const enter = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 22, stiffness: 90, mass: 0.9}});
  const heading = enter(0);
  const environment = enter(24);
  const foundationFlow = interpolate(frame, [62, 104], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const lowerCards = enter(96);
  const contract = enter(126);
  const relationshipFlow = interpolate(frame, [146, 188], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pulse = interpolate((frame - 188) % 40, [0, 20, 40], [0.32, 0.9, 0.32], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const exit = interpolate(frame, [scenes.notebooks - timing.sceneExit, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <div style={{position: 'absolute', left: 120, right: 120, top: 92, textAlign: 'center', ...revealStyle(heading, 16)}}>
      <div style={{fontSize: 60, lineHeight: 1.08, fontWeight: 850, letterSpacing: -1.8, color: theme.text, whiteSpace: 'nowrap'}}>Code-first, notebook-first workflow</div>
      <div style={{marginTop: 18, fontSize: 27, lineHeight: 1.25, fontWeight: 500, color: theme.muted, whiteSpace: 'nowrap'}}>Shared configuration powers governance and ETL through reusable notebooks</div>
    </div>

    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
      <defs>
        <linearGradient id="governance-contract" x1="0" x2="1"><stop stopColor={theme.governance} /><stop offset="1" stopColor="#a995ec" /></linearGradient>
        <linearGradient id="contract-pipeline" x1="0" x2="1"><stop stopColor="#a995ec" /><stop offset="1" stopColor={theme.engineering} /></linearGradient>
        <marker id="flow-arrow-neutral" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill={theme.neutral} /></marker>
      </defs>
      <g fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M855 430 C855 515 420 505 420 610" stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.7} markerEnd="url(#flow-arrow-neutral)" />
        <path d="M1065 430 C1065 515 1500 505 1500 610" stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.7} markerEnd="url(#flow-arrow-neutral)" />
        <path d="M580 704 C660 672 730 672 810 704" stroke="url(#governance-contract)" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow * 0.9} />
        <path d="M1110 704 C1190 672 1260 672 1340 704" stroke="url(#contract-pipeline)" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow * 0.9} />
        <path d="M810 754 C730 786 660 786 580 754" stroke="url(#governance-contract)" strokeWidth="3" opacity={relationshipFlow * pulse} strokeDasharray="9 14" />
        <path d="M1340 754 C1260 786 1190 786 1110 754" stroke="url(#contract-pipeline)" strokeWidth="3" opacity={relationshipFlow * pulse} strokeDasharray="9 14" />
      </g>
    </svg>

    <NotebookCard title="00_env_config" subtitle="Config-driven" color={theme.neutral} progress={environment} foundation footer={<div style={{marginTop: 24, display: 'flex', gap: 8}}>{['Workspace', 'Lakehouse', 'Warehouse', 'Parameters'].map((item) => <span key={item} style={{padding: '6px 9px', borderRadius: 7, background: '#ffffff0b', border: '1px solid #ffffff15', color: '#aebbd0', fontSize: 13, lineHeight: 1}}>{item}</span>)}</div>} />
    <NotebookCard title="01_governance" subtitle="Governance" color={theme.governance} progress={lowerCards} />
    <ContractCard progress={contract} />
    <NotebookCard title="02_pipeline" subtitle="ETL Pipeline" color={theme.engineering} progress={lowerCards} />
  </div>;
};
