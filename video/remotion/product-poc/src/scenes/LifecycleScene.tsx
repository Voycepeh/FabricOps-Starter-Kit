import {memo} from 'react';
import {Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {AnimatedDataFlow, AnimatedFlowPath} from '../components/AnimatedDataFlow';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';
import {lifecycleFrame, VIDEO_TUNING} from '../videoTuning';

const WORKSPACE_WIDTH = 580;
const STEP_CARD_WIDTH = WORKSPACE_WIDTH * 0.8;
const STEP_CARD_HEIGHT = VIDEO_CONFIG.sizes.workflowCardHeight * 1.2;

const workspaces = [
  {name: 'Governance', color: theme.governance, x: 55},
  {name: 'Engineering', color: theme.engineering, x: 670},
  {name: 'Consumption', color: theme.consumer, x: 1285},
];

export const STEP_7_LABEL = 'Consume Data\nStored in Engineering\nWorkspace';

const steps = [
  {number: 1, label: 'Data Stewards &\nData Agreement', color: theme.governance, x: 113, y: 205},
  {number: 2, label: 'Pipeline\nRead · Transform · Write · Profile', color: theme.engineering, x: 728, y: 205},
  {number: 3, label: 'Author\nData Contract', color: theme.governance, x: 113, y: 485},
  {number: 4, label: 'Dry Run & Validate\nData Contract within Pipeline', color: theme.engineering, x: 728, y: 485},
  {number: 5, label: 'Activate Data Contract\nand Pipeline', color: theme.governance, x: 113, y: 765},
  {number: 6, label: 'Run Governed\nPipeline', color: theme.production, x: 728, y: 765},
  {number: 7, label: STEP_7_LABEL, color: theme.consumer, x: 1343, y: 765},
];

const connectors = [
  {d: 'M577 295 H728', destination: 1},
  {d: 'M960 385 C960 435 345 435 345 485', destination: 2},
  {d: 'M577 575 H728', destination: 3},
  {d: 'M960 665 C960 715 345 715 345 765', destination: 4},
  {d: 'M577 855 H728', destination: 5},
  {d: 'M1192 855 H1343', destination: 6},
];

const MascotBadgeArtwork = memo(({pose}: {pose: MascotName}) => <Img src={mascotSrc(pose)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 7px 12px #0007)'}} />);

type StepCardProps = {
  number: number;
  label: string;
  color: string;
  enter: number;
  active: boolean;
  width?: number;
  height?: number;
  borderRadius?: number;
  circleSize?: number;
  fontSize?: number;
  gap?: number;
  horizontalPadding?: number;
  previousLabel?: string;
  labelProgress?: number;
  subtitle?: string;
  subtitleFontSize?: number;
  subtitleGap?: number;
  subtitleOpacity?: number;
  singleLineLabel?: boolean;
  centerContent?: boolean;
  badgeMascot?: MascotName;
  badgeProgress?: number;
  labelAlignmentProgress?: number;
};

export const StepCard = memo(({
  number,
  label,
  color,
  enter,
  active,
  width,
  height,
  borderRadius = 28,
  circleSize = 62,
  fontSize,
  gap = 22,
  horizontalPadding = 25,
  previousLabel,
  labelProgress = 1,
  subtitle,
  subtitleFontSize,
  subtitleGap = 8,
  subtitleOpacity = 1,
  singleLineLabel = false,
  centerContent = false,
  badgeMascot,
  badgeProgress = 0,
  labelAlignmentProgress = 0,
}: StepCardProps) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{width: width ?? sizes.workflowCardWidth, height: height ?? sizes.workflowCardHeight, borderRadius, display: 'flex', alignItems: 'center', gap, padding: `0 ${horizontalPadding}px`, boxSizing: 'border-box', background: `linear-gradient(145deg, ${color}2e, #0d192b 72%)`, border: `3px solid ${active ? color : `${color}88`}`, boxShadow: active ? `0 0 48px ${color}55` : '0 18px 40px #0007', opacity: enter * (active ? 1 : 0.62), scale: 0.86 + enter * 0.14}}>
    <div style={{position: 'relative', width: circleSize, height: circleSize, flex: '0 0 auto'}}>
      <div style={{position: 'absolute', inset: 0, borderRadius: 99, display: 'grid', placeItems: 'center', background: color, color: '#07101f', fontSize: circleSize * 0.55, fontWeight: 900, opacity: 1 - badgeProgress}}>{number}</div>
      {badgeMascot ? <div style={{position: 'absolute', inset: 0, opacity: badgeProgress, scale: 0.84 + badgeProgress * 0.16}}><MascotBadgeArtwork pose={badgeMascot} /></div> : null}
    </div>
    {subtitle ? <div style={{position: centerContent ? 'relative' : undefined, flex: 1, alignSelf: 'stretch', minWidth: 0, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center', textAlign: 'left'}}>
      <div style={{position: centerContent ? 'absolute' : undefined, top: centerContent ? 0 : undefined, bottom: centerContent ? 0 : undefined, left: centerContent ? `${interpolate(labelAlignmentProgress, [0, 1], [50, 0])}%` : undefined, width: centerContent ? 'max-content' : undefined, maxWidth: centerContent ? '100%' : undefined, display: centerContent ? 'flex' : undefined, alignItems: centerContent ? 'center' : undefined, translate: centerContent ? `${interpolate(labelAlignmentProgress, [0, 1], [-50, 0])}% 0` : undefined, whiteSpace: singleLineLabel ? 'nowrap' : 'pre-line', textAlign: 'left', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.08, fontWeight: 720, opacity: labelProgress}}>{label}</div>
      <div style={{position: centerContent ? 'absolute' : undefined, left: centerContent ? 0 : undefined, right: centerContent ? 0 : undefined, bottom: centerContent ? subtitleGap : undefined, marginTop: centerContent ? 0 : subtitleGap, color: '#94a3b8', fontSize: subtitleFontSize ?? (fontSize ?? text.workflow) * 0.52, lineHeight: 1.2, fontWeight: 600, letterSpacing: 0.4, opacity: subtitleOpacity}}>{subtitle}</div>
    </div> : <div style={{position: 'relative', flex: 1, height: (fontSize ?? text.workflow) * 2.3}}>
      {previousLabel ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', whiteSpace: singleLineLabel ? 'nowrap' : 'pre-line', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.15, fontWeight: 720, opacity: interpolate(labelProgress, [0, 0.46], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{previousLabel}</div> : null}
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', whiteSpace: singleLineLabel ? 'nowrap' : 'pre-line', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.15, fontWeight: 720, opacity: previousLabel ? interpolate(labelProgress, [0.54, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : labelProgress}}>{label}</div>
    </div>}
  </div>;
});

export const LifecycleScene = ({hideStep7 = false, seamlessHandoff = true}: {hideStep7?: boolean; seamlessHandoff?: boolean}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, timing} = VIDEO_CONFIG;
  const {timingSeconds, loop} = VIDEO_TUNING.lifecycle;
  const stepTimes = timingSeconds.steps.map((seconds) => lifecycleFrame(seconds, fps));
  const loopStart = lifecycleFrame(timingSeconds.loopStart, fps);
  const loopEnd = lifecycleFrame(timingSeconds.loopEnd, fps);
  const productionArrowStart = lifecycleFrame(timingSeconds.productionArrowStart, fps);
  const productionArrowEnd = lifecycleFrame(timingSeconds.productionArrowEnd, fps);
  const activeIndex = stepTimes.reduce((latest, reveal, index) => frame >= reveal ? index : latest, -1);
  const exit = hideStep7 || seamlessHandoff ? 1 : interpolate(frame, [scenes.workflow - timing.sceneExit, scenes.workflow], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const loopEnter = interpolate(frame, [loopStart, loopStart + 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const loopExit = interpolate(frame, [loopEnd - 18, loopEnd], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const loopOpacity = loopEnter * loopExit;
  const loopRestingOpacity = loopEnter * 0.28;
  const tracerOffset = -((Math.max(0, frame - loopStart) * 11) % 1000);
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    {workspaces.map((workspace, index) => {
      const enter = spring({frame: frame - index * 5, fps, config: {damping: 20, stiffness: 82}});
      return <div key={workspace.name} style={{position: 'absolute', left: workspace.x, top: 58, width: WORKSPACE_WIDTH, height: 950, borderRadius: 34, border: `2px solid ${workspace.color}45`, background: `${workspace.color}0b`, opacity: enter}}><div style={{paddingTop: 28, textAlign: 'center', color: workspace.color, fontSize: 28, fontWeight: 800}}>{workspace.name}<br />Workspace</div></div>;
    })}
    <AnimatedDataFlow>
      {connectors.map((connector) => {
        const isProductionArrow = connector.destination === 5;
        const reveal = isProductionArrow ? productionArrowStart : stepTimes[connector.destination];
        const complete = isProductionArrow ? productionArrowEnd : reveal + timing.workflowStepEnter;
        if (frame < reveal) return null;
        const draw = interpolate(frame, [reveal, complete], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: isProductionArrow ? Easing.inOut(Easing.cubic) : Easing.linear});
        return <AnimatedFlowPath key={connector.d} id={`lifecycle-${connector.destination}`} d={connector.d} progress={draw} color={steps[connector.destination].color} baseColor="#405571" strokeWidth={6} />;
      })}
      <ellipse cx={loop.cx} cy={loop.cy} rx={loop.rx} ry={loop.ry} fill="none" stroke={theme.governance} strokeWidth="4" strokeDasharray="12 11" opacity={loopRestingOpacity} />
      {loopOpacity > 0 ? <ellipse cx={loop.cx} cy={loop.cy} rx={loop.rx} ry={loop.ry} fill="none" stroke={theme.production} strokeWidth="10" strokeLinecap="round" pathLength="1000" strokeDasharray="125 875" strokeDashoffset={tracerOffset} opacity={loopOpacity} style={{filter: `drop-shadow(0 0 12px ${theme.production})`}} /> : null}
      <path d={`M${loop.cx + loop.rx - 8} ${loop.cy - 10} L${loop.cx + loop.rx + 8} ${loop.cy} L${loop.cx + loop.rx - 8} ${loop.cy + 10} Z`} fill={theme.governance} opacity={loopRestingOpacity * 2.2} />
    </AnimatedDataFlow>
    {steps.map((step, index) => {
      if (frame < stepTimes[index]) return null;
      if (hideStep7 && step.number === 7) return null;
      const enter = spring({frame: frame - stepTimes[index], fps, durationInFrames: timing.workflowStepEnter, config: {damping: 19, stiffness: 92}});
      return <div key={step.number} style={{position: 'absolute', left: step.x, top: step.y}}><StepCard {...step} width={STEP_CARD_WIDTH} height={STEP_CARD_HEIGHT} enter={enter} active={activeIndex === index} /></div>;
    })}
    {loopOpacity > 0 ? <div style={{position: 'absolute', left: loop.captionLeft, top: loop.captionTop, width: 300, textAlign: 'center', color: '#dce7f5', fontSize: 24, fontWeight: 720, opacity: loopOpacity}}>Iterate until validations pass</div> : null}
  </div>;
};
