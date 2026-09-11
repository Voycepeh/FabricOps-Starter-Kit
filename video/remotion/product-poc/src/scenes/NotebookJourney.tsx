import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const NOTEBOOK = {
  width: 410,
  height: 220,
  borderRadius: 28,
  padding: 34,
  glyphSize: 48,
  titleSize: 31,
  subtitleSize: 21,
} as const;

const LAYOUT = {
  environment: {left: 755, top: 235},
  governance: {left: 220, top: 650},
  contract: {left: 785, top: 555, width: 350, height: 400},
  pipeline: {left: 1290, top: 650},
} as const;

const NotebookGlyph = ({color}: {color: string}) => (
  <div style={{position: 'relative', width: NOTEBOOK.glyphSize, height: NOTEBOOK.glyphSize, flex: '0 0 auto'}}>
    <div style={{position: 'absolute', inset: 0, border: `2px solid ${color}`, borderRadius: 8, background: `${color}12`}} />
    <div style={{position: 'absolute', left: -5, top: 9, width: 10, height: 4, borderRadius: 4, background: color, boxShadow: `0 11px 0 ${color}, 0 22px 0 ${color}`}} />
    <div style={{position: 'absolute', left: 13, right: 8, top: 14, height: 3, borderRadius: 3, background: color, boxShadow: `0 9px 0 ${color}99, 0 18px 0 ${color}66`}} />
  </div>
);

const NotebookCard = ({title, subtitle, color, progress, position}: {
  title: string;
  subtitle: string;
  color: string;
  progress: number;
  position: {left: number; top: number};
}) => (
  <div style={{position: 'absolute', ...position, width: NOTEBOOK.width, height: NOTEBOOK.height, boxSizing: 'border-box', borderRadius: NOTEBOOK.borderRadius, padding: NOTEBOOK.padding, display: 'flex', alignItems: 'center', background: `linear-gradient(145deg, ${color}24, #0b1525 74%)`, border: `2px solid ${color}cc`, boxShadow: `0 24px 58px #0008, 0 0 30px ${color}16, inset 0px 1px 0 #ffffff12`, opacity: progress, transform: `translateY(${(1 - progress) * 20}px) scale(${0.94 + progress * 0.06})`}}>
    <div style={{position: 'absolute', top: -2, left: 34, width: 80, height: 9, borderRadius: '0 0 8px 8px', background: color}} />
    <div style={{display: 'flex', alignItems: 'center', gap: 26, width: '100%'}}>
      <NotebookGlyph color={color} />
      <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 12, minWidth: 0}}>
        <div style={{fontSize: NOTEBOOK.titleSize, lineHeight: 1.15, fontWeight: 820, color: theme.text, whiteSpace: 'nowrap'}}>{title}</div>
        <div style={{fontSize: NOTEBOOK.subtitleSize, lineHeight: 1.25, fontWeight: 680, color}}>{subtitle}</div>
      </div>
    </div>
  </div>
);

const ContractDocument = ({progress}: {progress: number}) => {
  const guardrails = ['Schema', 'Freshness', 'Data Quality', 'Sensitivity', 'Source Stability'];
  return (
    <div style={{position: 'absolute', ...LAYOUT.contract, boxSizing: 'border-box', padding: '34px 38px 24px', background: 'linear-gradient(150deg, #303a49, #1b2432 78%)', border: '2px solid #7f8b9b', borderRadius: '16px 16px 20px 20px', boxShadow: '0 28px 65px #0009, inset 0 1px 0 #ffffff1a', opacity: progress, transform: `translateY(${(1 - progress) * 18}px) scale(${0.95 + progress * 0.05})`, overflow: 'hidden'}}>
      <div style={{position: 'absolute', top: -2, right: -2, width: 66, height: 66, background: '#111a27', clipPath: 'polygon(100% 0, 0 0, 100% 100%)'}} />
      <div style={{position: 'absolute', top: 0, right: 0, width: 66, height: 66, background: '#697586', clipPath: 'polygon(0 0, 0 100%, 100% 100%)', opacity: 0.72}} />
      <div style={{width: 42, height: 48, boxSizing: 'border-box', border: '2px solid #aab3bf', borderRadius: 6, position: 'relative', marginBottom: 16}}>
        <div style={{position: 'absolute', left: 10, right: 8, top: 13, height: 3, borderRadius: 2, background: '#aab3bf', boxShadow: '0 9px 0 #8f9aa9, 0 18px 0 #768292'}} />
      </div>
      <div style={{fontSize: 30, lineHeight: 1.15, fontWeight: 820, color: '#f5f7fa', whiteSpace: 'nowrap'}}>Data Contract</div>
      <div style={{marginTop: 18, marginBottom: 9, fontSize: 19, lineHeight: 1.25, fontWeight: 740, color: '#aeb7c3', letterSpacing: 1, textTransform: 'uppercase'}}>Guardrails</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 7}}>
        {guardrails.map((guardrail) => (
          <div key={guardrail} style={{minHeight: 29, display: 'flex', alignItems: 'center', gap: 13, fontSize: 21, lineHeight: 1.3, fontWeight: 560, color: '#dce1e8'}}>
            <span style={{width: 7, height: 7, flex: '0 0 auto', borderRadius: 7, background: '#9ca7b5'}} />
            {guardrail}
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
  const enter = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 21, stiffness: 88}});
  const heading = enter(0);
  const environment = enter(22);
  const foundationFlow = interpolate(frame, [68, 112], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const lowerNotebooks = enter(104);
  const contract = enter(132);
  const relationshipFlow = interpolate(frame, [154, 198], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pulse = 0.42 + Math.sin(Math.max(0, frame - 198) / 10) * 0.18;
  const exit = interpolate(frame, [scenes.notebooks - timing.sceneExit, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <div style={{position: 'absolute', left: 120, right: 120, top: 72, textAlign: 'center', opacity: heading, transform: `translateY(${(1 - heading) * 14}px)`}}>
      <div style={{fontSize: 60, lineHeight: 1.08, fontWeight: 850, letterSpacing: -1.8, color: theme.text, whiteSpace: 'nowrap'}}>Code-first, notebook-first workflow</div>
      <div style={{marginTop: 15, fontSize: 27, lineHeight: 1.25, fontWeight: 500, color: theme.muted, whiteSpace: 'nowrap'}}>Shared configuration powers governance and ETL through reusable notebooks</div>
    </div>

    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
      <defs>
        <linearGradient id="governance-contract"><stop stopColor={theme.governance} /><stop offset="1" stopColor="#949eac" /></linearGradient>
        <linearGradient id="contract-pipeline"><stop stopColor="#949eac" /><stop offset="1" stopColor={theme.engineering} /></linearGradient>
        <marker id="notebook-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill={theme.neutral} /></marker>
      </defs>
      <g fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M855 455 C855 535 425 535 425 638" stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.72} markerEnd="url(#notebook-arrow)" />
        <path d="M1065 455 C1065 535 1495 535 1495 638" stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.72} markerEnd="url(#notebook-arrow)" />
        <path d="M630 720 C688 690 727 690 785 720" stroke="url(#governance-contract)" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow * 0.86} />
        <path d="M1135 720 C1193 690 1232 690 1290 720" stroke="url(#contract-pipeline)" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow * 0.86} />
        <path d="M785 778 C727 808 688 808 630 778" stroke="url(#governance-contract)" strokeWidth="3" strokeDasharray="9 13" opacity={relationshipFlow * pulse} />
        <path d="M1290 778 C1232 808 1193 808 1135 778" stroke="url(#contract-pipeline)" strokeWidth="3" strokeDasharray="9 13" opacity={relationshipFlow * pulse} />
      </g>
    </svg>

    <NotebookCard title="00_env_config" subtitle="Config-driven" color={theme.neutral} progress={environment} position={LAYOUT.environment} />
    <NotebookCard title="01_governance" subtitle="Governance" color={theme.governance} progress={lowerNotebooks} position={LAYOUT.governance} />
    <ContractDocument progress={contract} />
    <NotebookCard title="02_pipeline" subtitle="ETL Pipeline" color={theme.engineering} progress={lowerNotebooks} position={LAYOUT.pipeline} />
  </div>;
};
