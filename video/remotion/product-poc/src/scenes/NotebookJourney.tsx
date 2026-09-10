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
  governance: {x: 120, y: 470},
  contract: {x: 780, y: 495},
  development: {x: 1360, y: 470},
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, sizes, timing} = VIDEO_CONFIG;
  const enter = (index: number) => spring({frame: frame - index * timing.itemStagger, fps, config: {damping: 20, stiffness: 82}});
  const contract = spring({frame: frame - timing.operatingContractDelay, fps, config: {damping: 20, stiffness: 80}});
  const handshake = interpolate(frame, [timing.operatingContractDelay + 15, timing.operatingContractDelay + 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const splitStart = timing.operatingPromotionDelay;
  const splitMoveStart = splitStart + timing.cloneOverlap;
  const splitEnd = splitMoveStart + timing.cloneDuration;
  const split = interpolate(frame, [splitMoveStart, splitEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const splitActive = frame >= splitStart;
  const productionMix = interpolate(split, [0.35, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const productionColor = interpolateColors(productionMix, [0, 1], [theme.engineering, theme.production]);
  const productionLink = interpolate(frame, [splitMoveStart, splitEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sceneExit = interpolate(frame, [scenes.notebooks - timing.sceneExit, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, opacity: sceneExit}}>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      <defs><linearGradient id="contract-gradient"><stop stopColor={theme.governance} /><stop offset="1" stopColor={theme.engineering} /></linearGradient></defs>
      <path d="M560 585 H780 M1140 585 H1360" fill="none" stroke="url(#contract-gradient)" strokeWidth="8" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - handshake} opacity={handshake * 0.82} />
      <path d="M960 675 L1360 865" fill="none" stroke={theme.production} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - productionLink} opacity={productionLink * 0.72} />
    </svg>
    <div style={{position: 'absolute', left: positions.environment.x, top: positions.environment.y, opacity: enter(0)}}><NotebookCard label="00_env_config" color={theme.neutral} /></div>
    <div style={{position: 'absolute', left: positions.governance.x, top: positions.governance.y, opacity: enter(1)}}><NotebookCard label="01_governance" color={theme.governance} /></div>
    {!splitActive ? <div style={{position: 'absolute', left: positions.development.x, top: positions.development.y, opacity: enter(2)}}><NotebookCard label="02_pipeline" color={theme.engineering} environment="Development" /></div> : null}
    <div style={{position: 'absolute', left: positions.contract.x, top: positions.contract.y, width: sizes.contractWidth, height: sizes.contractHeight, boxSizing: 'border-box', borderRadius: 42, display: 'grid', placeItems: 'center', background: `linear-gradient(110deg, ${theme.governance}48, ${theme.engineering}48)`, border: '3px solid #a99bea', boxShadow: `0 20px 55px #0009, 0 0 ${28 + handshake * 20}px #8d85e344`, color: '#fff', fontSize: 38, fontWeight: 840, opacity: contract, transform: `scaleX(${0.22 + contract * 0.78})`}}>Data Contract</div>
    {splitActive ? <>
      <div style={{position: 'absolute', left: positions.development.x, top: positions.development.y, zIndex: 3}}><NotebookCard label="02_pipeline" color={theme.engineering} environment="Development" /></div>
      <div style={{position: 'absolute', left: positions.development.x + split * timing.cloneTravelX, top: positions.development.y + split * timing.cloneTravelY, zIndex: 4}}><NotebookCard label="02_pipeline" color={productionColor} environment="Development" productionMix={productionMix} /></div>
    </> : null}
  </div>;
};
