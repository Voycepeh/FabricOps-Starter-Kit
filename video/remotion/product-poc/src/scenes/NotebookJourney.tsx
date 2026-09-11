import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

const ModelCard = ({label, color, subtitle, opacity}: {label: string; color: string; subtitle?: string; opacity: number}) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{width: sizes.notebookWidth, height: sizes.notebookHeight, boxSizing: 'border-box', borderRadius: 40, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20, background: `linear-gradient(145deg, ${color}3d, #0d192b 72%)`, border: `3px solid ${color}`, boxShadow: `0 26px 65px #0009, 0 0 46px ${color}32`, opacity, transform: `scale(${0.88 + opacity * 0.12})`}}>
    <div style={{fontSize: text.notebook, lineHeight: 1, fontWeight: 840, color: '#fff'}}>{label}</div>
    {subtitle ? <div style={{fontSize: text.notebookEnvironment, fontWeight: 780, color}}>{subtitle}</div> : null}
  </div>;
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, sizes, timing} = VIDEO_CONFIG;
  const enter = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 20, stiffness: 82}});
  const environment = enter(0);
  const governance = enter(timing.itemStagger * 3);
  const pipeline = enter(timing.itemStagger * 6);
  const contract = enter(timing.operatingContractDelay);
  const handshake = interpolate(frame, [timing.operatingHandshakeDelay, timing.operatingHandshakeDelay + 45], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pulse = 0.55 + Math.sin(Math.max(0, frame - timing.operatingHandshakeDelay) / 10) * 0.18;
  const exit = interpolate(frame, [scenes.notebooks - timing.sceneExit, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <div style={{position: 'absolute', left: 740, top: 85}}><ModelCard label="00_env_config" color={theme.neutral} opacity={environment} /></div>
    <div style={{position: 'absolute', left: 170, top: 590}}><ModelCard label="01_governance" color={theme.governance} opacity={governance} /></div>
    <div style={{position: 'absolute', left: 1310, top: 590}}><ModelCard label="02_pipeline" subtitle="Development" color={theme.engineering} opacity={pipeline} /></div>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      <defs><linearGradient id="handshake-gradient"><stop stopColor={theme.governance} /><stop offset="0.5" stopColor="#a995ec" /><stop offset="1" stopColor={theme.engineering} /></linearGradient></defs>
      <path d="M610 705 C700 610 755 610 800 675" fill="none" stroke="url(#handshake-gradient)" strokeWidth="9" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - handshake} opacity={handshake * 0.82} />
      <path d="M1120 675 C1165 610 1220 610 1310 705" fill="none" stroke="url(#handshake-gradient)" strokeWidth="9" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - handshake} opacity={handshake * 0.82} />
    </svg>
    <div style={{position: 'absolute', left: 800, top: 615, width: sizes.contractWidth, height: sizes.contractHeight, boxSizing: 'border-box', borderRadius: 46, display: 'grid', placeItems: 'center', background: `linear-gradient(115deg, ${theme.governance}58, #353967, ${theme.engineering}58)`, border: '3px solid #b2a7f4', boxShadow: `0 24px 70px #000a, 0 0 ${30 + handshake * 24}px rgba(151, 132, 235, ${pulse})`, color: '#fff', fontSize: 42, fontWeight: 860, opacity: contract, transform: `scale(${0.72 + contract * 0.28 + handshake * 0.03})`}}>Data Contract</div>
  </div>;
};
