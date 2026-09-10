import {Notebook48Item} from '@fabric-msft/svg-icons';
import {Easing, interpolate, interpolateColors, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

type NotebookCardProps = {
  label: string;
  color: string;
  opacity?: number;
  scale?: number;
  subtitle?: string;
  subtitleOpacity?: number;
};

const NotebookCard = ({label, color, opacity = 1, scale = 1, subtitle, subtitleOpacity = 1}: NotebookCardProps) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{position: 'relative', width: sizes.notebookWidth, height: sizes.notebookHeight, borderRadius: 40, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, background: `linear-gradient(145deg, ${color}36, #0d192b 72%)`, border: `3px solid ${color}cc`, boxShadow: `0 24px 60px #0009, 0 0 48px ${color}32`, opacity, transform: `scale(${scale})`}}>
    <Notebook48Item width={sizes.notebookIcon} height={sizes.notebookIcon} aria-hidden="true" />
    <div style={{fontSize: text.notebook, fontWeight: 820, color: '#fff'}}>{label}</div>
    {subtitle ? <div style={{position: 'absolute', bottom: 17, left: 0, right: 0, textAlign: 'center', fontSize: text.notebookEnvironment, fontWeight: 760, color, opacity: subtitleOpacity}}>{subtitle}</div> : null}
  </div>;
};

const positions = {
  environment: {x: 740, y: 80},
  governance: {x: 130, y: 650},
  pipeline: {x: 740, y: 650},
  explore: {x: 1350, y: 650},
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, sizes, timing} = VIDEO_CONFIG;
  const governanceStart = timing.itemStagger * 4 + 40;
  const governanceHoldStart = governanceStart + timing.focusIn;
  const governanceOutStart = governanceHoldStart + timing.focusHold;
  const governanceEnd = governanceOutStart + timing.focusOut;
  const pipelineStart = governanceEnd + timing.itemStagger;
  const pipelineHoldStart = pipelineStart + timing.focusIn;
  const pipelineOutStart = pipelineHoldStart + timing.focusHold;
  const pipelineEnd = pipelineOutStart + timing.focusOut;
  const splitStart = pipelineEnd + 10;
  const splitMoveStart = splitStart + timing.splitOverlap;
  const splitEnd = splitMoveStart + timing.splitMove;
  const sceneExit = interpolate(frame, [scenes.notebooks - 30, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const governanceFocus = interpolate(frame, [governanceStart, governanceHoldStart, governanceOutStart, governanceEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pipelineFocus = interpolate(frame, [pipelineStart, pipelineHoldStart, pipelineOutStart, pipelineEnd], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const split = interpolate(frame, [splitMoveStart, splitEnd], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const splitActive = frame >= splitStart;
  const dim = Math.max(governanceFocus, pipelineFocus);
  const enter = (index: number) => spring({frame: frame - index * timing.itemStagger, fps, config: {damping: 20, stiffness: 82}});
  const normalPipelineOpacity = enter(2) * (splitActive ? 0 : 1);
  const otherOpacity = (index: number) => enter(index) * (1 - dim * 0.72) * (1 - (splitActive ? split * 0.88 : 0));
  const cloneX = positions.pipeline.x;
  const cloneY = positions.pipeline.y;
  return <div style={{position: 'absolute', inset: 0, opacity: sceneExit}}>
    <div style={{position: 'absolute', left: positions.environment.x, top: positions.environment.y}}><NotebookCard label="00_env_config" color={theme.neutral} opacity={otherOpacity(0)} /></div>
    <div style={{position: 'absolute', left: positions.governance.x + governanceFocus * 70, top: positions.governance.y - governanceFocus * 28, zIndex: governanceFocus > 0 ? 3 : 1}}><NotebookCard label="01_governance" color={theme.governance} opacity={enter(1) * (1 - pipelineFocus * 0.72) * (1 - (splitActive ? split * 0.88 : 0))} scale={1 + governanceFocus * (sizes.notebookFocusScale - 1)} /></div>
    <div style={{position: 'absolute', left: positions.pipeline.x, top: positions.pipeline.y - pipelineFocus * 28, zIndex: pipelineFocus > 0 ? 3 : 1}}><NotebookCard label="02_pipeline" color={theme.engineering} opacity={normalPipelineOpacity * (1 - governanceFocus * 0.72)} scale={1 + pipelineFocus * (sizes.notebookFocusScale - 1)} /></div>
    <div style={{position: 'absolute', left: positions.explore.x, top: positions.explore.y}}><NotebookCard label="99_explore" color={theme.consumer} opacity={otherOpacity(3)} /></div>
    {splitActive ? <>
      <div style={{position: 'absolute', left: cloneX - split * 270, top: cloneY - split * 175, zIndex: 4}}><NotebookCard label="02_pipeline" color={theme.engineering} subtitle="Engineering Development" subtitleOpacity={split} /></div>
      <div style={{position: 'absolute', left: cloneX + split * 270, top: cloneY - split * 175, zIndex: 4}}><NotebookCard label="02_pipeline" color={interpolateColors(split, [0, 1], [theme.engineering, theme.production])} subtitle="Engineering Production" subtitleOpacity={split} /></div>
    </> : null}
  </div>;
};
