import {Easing, interpolate, interpolateColors, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

type NotebookCardProps = {
  label: string;
  color: string;
  opacity?: number;
  environment?: string;
  productionMix?: number;
};

const NotebookCard = ({label, color, opacity = 1, environment, productionMix = 0}: NotebookCardProps) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{position: 'relative', width: sizes.notebookWidth, height: sizes.notebookHeight, boxSizing: 'border-box', borderRadius: 38, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, background: `linear-gradient(145deg, ${color}38, #0d192b 72%)`, border: `3px solid ${color}`, boxShadow: `0 24px 60px #0009, 0 0 44px ${color}30`, opacity}}>
    <div style={{fontSize: text.notebook, lineHeight: 1, fontWeight: 840, color: '#fff'}}>{label}</div>
    {environment ? <div style={{position: 'relative', width: '100%', height: 34, fontSize: text.notebookEnvironment, lineHeight: '34px', fontWeight: 780, color}}>
      <div style={{position: 'absolute', inset: 0, textAlign: 'center', opacity: 1 - productionMix}}>{environment}</div>
      <div style={{position: 'absolute', inset: 0, textAlign: 'center', opacity: productionMix}}>Production</div>
    </div> : null}
  </div>;
};

const positions = {
  environment: {x: 740, y: 80},
  governance: {x: 80, y: 470},
  development: {x: 880, y: 470},
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, sizes, timing} = VIDEO_CONFIG;
  const enter = (index: number) => spring({frame: frame - index * timing.itemStagger, fps, config: {damping: 20, stiffness: 82}});
  const arrows = interpolate(frame, [70, 95], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const contract = spring({frame: frame - 105, fps, config: {damping: 20, stiffness: 80}});
  const splitStart = 185;
  const splitMoveStart = splitStart + timing.cloneOverlap;
  const splitEnd = splitMoveStart + timing.cloneDuration;
  const split = interpolate(frame, [splitMoveStart, splitEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const splitActive = frame >= splitStart;
  const productionColor = interpolateColors(split, [0, 1], [theme.engineering, theme.production]);
  const productionLink = interpolate(frame, [splitMoveStart, splitEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sceneExit = interpolate(frame, [scenes.notebooks - 30, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, opacity: sceneExit}}>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      <defs><marker id="setup-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#8da0b8" /></marker></defs>
      <path d="M960 310 C960 390 300 380 300 470 M960 310 C960 390 1100 380 1100 470" fill="none" stroke="#8da0b8" strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - arrows} markerEnd={arrows > 0.96 ? 'url(#setup-arrow)' : undefined} opacity="0.65" />
      <path d="M520 585 H540 M840 585 H880" fill="none" stroke="url(#contract-gradient)" strokeWidth="8" opacity={contract} />
      <defs><linearGradient id="contract-gradient"><stop stopColor={theme.governance} /><stop offset="1" stopColor={theme.engineering} /></linearGradient></defs>
      <path d="M690 660 C760 930 1230 970 1400 765" fill="none" stroke={theme.production} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - productionLink} opacity={productionLink * 0.8} />
    </svg>
    <div style={{position: 'absolute', left: positions.environment.x, top: positions.environment.y, opacity: enter(0)}}><NotebookCard label="00_env_config" color={theme.neutral} /></div>
    <div style={{position: 'absolute', left: positions.governance.x, top: positions.governance.y, opacity: enter(1)}}><NotebookCard label="01_governance" color={theme.governance} /></div>
    {!splitActive ? <div style={{position: 'absolute', left: positions.development.x, top: positions.development.y, opacity: enter(2)}}><NotebookCard label="02_pipeline" color={theme.engineering} environment="Development" /></div> : null}
    <div style={{position: 'absolute', left: 540, top: 510, width: sizes.contractWidth, height: sizes.contractHeight, boxSizing: 'border-box', borderRadius: 75, display: 'grid', placeItems: 'center', background: `linear-gradient(110deg, ${theme.governance}40, ${theme.engineering}40)`, border: '3px solid #a99bea', boxShadow: '0 20px 50px #0009', color: '#fff', fontSize: 34, fontWeight: 840, opacity: contract, transform: `scale(${0.88 + contract * 0.12})`}}>Data Contract</div>
    {splitActive ? <>
      <div style={{position: 'absolute', left: positions.development.x, top: positions.development.y, zIndex: 3}}><NotebookCard label="02_pipeline" color={theme.engineering} environment="Development" /></div>
      <div style={{position: 'absolute', left: positions.development.x + split * timing.cloneTravelX, top: positions.development.y + split * timing.cloneTravelY, zIndex: 4}}><NotebookCard label="02_pipeline" color={productionColor} environment="Development" productionMix={split} /></div>
    </> : null}
  </div>;
};
