import {Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {AnimatedDataFlow, AnimatedFlowPath} from '../components/AnimatedDataFlow';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';
import {lifecycleFrame, VIDEO_TUNING} from '../videoTuning';

const workspaces = [
  {name: 'Governance', color: theme.governance, x: 55},
  {name: 'Engineering Development', color: theme.engineering, x: 510},
  {name: 'Engineering Production', color: theme.production, x: 965},
  {name: 'Consumer', color: theme.consumer, x: 1420},
];

export const STEP_7_LABEL = 'Consume approved\nProduction data';

const steps = [
  {number: 1, label: 'Data Stewards &\nData Agreement', color: theme.governance, x: 80, y: 205},
  {number: 2, label: 'ETL, Profile &\nCatalogue', color: theme.engineering, x: 535, y: 205},
  {number: 3, label: 'Author\nData Contract', color: theme.governance, x: 80, y: 485},
  {number: 4, label: 'ETL with Contract\nGuardrails', color: theme.engineering, x: 535, y: 485},
  {number: 5, label: 'Activate &\nPromote', color: theme.governance, x: 80, y: 765},
  {number: 6, label: 'Run Production\nPipeline', color: theme.production, x: 990, y: 765},
  {number: 7, label: STEP_7_LABEL, color: theme.consumer, x: 1445, y: 765},
];

const connectors = [
  {d: 'M420 280 H535', destination: 1},
  {d: 'M710 355 C710 420 255 420 255 485', destination: 2},
  {d: 'M420 560 H535', destination: 3},
  {d: 'M710 635 C710 700 255 700 255 765', destination: 4},
  {d: 'M420 840 H990', destination: 5},
  {d: 'M1330 840 H1445', destination: 6},
];

const LifecycleMascot = ({pose, x, y, size, enterAt}: {pose: MascotName; x: number; y: number; size: number; enterAt: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - enterAt, fps, durationInFrames: 20, config: {damping: 20, stiffness: 95}});
  return null;
};

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
};

export const StepCard = ({
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
}: StepCardProps) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{width: width ?? sizes.workflowCardWidth, height: height ?? sizes.workflowCardHeight, borderRadius, display: 'flex', alignItems: 'center', gap, padding: `0 ${horizontalPadding}px`, boxSizing: 'border-box', background: `linear-gradient(145deg, ${color}2e, #0d192b 72%)`, border: `3px solid ${active ? color : `${color}88`}`, boxShadow: active ? `0 0 48px ${color}55` : '0 18px 40px #0007', opacity: enter * (active ? 1 : 0.62), scale: 0.86 + enter * 0.14}}>
    <div style={{width: circleSize, height: circleSize, flex: '0 0 auto', borderRadius: 99, display: 'grid', placeItems: 'center', background: color, color: '#07101f', fontSize: circleSize * 0.55, fontWeight: 900}}>{number}</div>
    {subtitle ? <div style={{flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center'}}>
      <div style={{whiteSpace: singleLineLabel ? 'nowrap' : 'pre-line', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.08, fontWeight: 720, opacity: labelProgress}}>{label}</div>
      <div style={{marginTop: subtitleGap, color: '#94a3b8', fontSize: subtitleFontSize ?? (fontSize ?? text.workflow) * 0.52, lineHeight: 1.2, fontWeight: 600, letterSpacing: 0.4, opacity: subtitleOpacity}}>{subtitle}</div>
    </div> : <div style={{position: 'relative', flex: 1, height: (fontSize ?? text.workflow) * 2.3}}>
      {previousLabel ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', whiteSpace: 'pre-line', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.15, fontWeight: 720, opacity: interpolate(labelProgress, [0, 0.46], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{previousLabel}</div> : null}
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', whiteSpace: 'pre-line', color: '#f7f9fd', fontSize: fontSize ?? text.workflow, lineHeight: 1.15, fontWeight: 720, opacity: previousLabel ? interpolate(labelProgress, [0.54, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : labelProgress}}>{label}</div>
    </div>}
  </div>;
};

export const LifecycleScene = ({hideStep7 = false}: {hideStep7?: boolean}) => {
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
  const exit = hideStep7 ? 1 : interpolate(frame, [scenes.workflow - timing.sceneExit, scenes.workflow], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const loopEnter = interpolate(frame, [loopStart, loopStart + 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const loopExit = interpolate(frame, [loopEnd - 18, loopEnd], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const loopOpacity = loopEnter * loopExit;
  const loopRestingOpacity = loopEnter * 0.28;
  const tracerOffset = -((Math.max(0, frame - loopStart) * 11) % 1000);
  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    {workspaces.map((workspace, index) => {
      const enter = spring({frame: frame - index * 5, fps, config: {damping: 20, stiffness: 82}});
      return <div key={workspace.name} style={{position: 'absolute', left: workspace.x, top: 58, width: 445, height: 950, borderRadius: 34, border: `2px solid ${workspace.color}45`, background: `${workspace.color}0b`, opacity: enter}}><div style={{paddingTop: 28, textAlign: 'center', color: workspace.color, fontSize: 28, fontWeight: 800}}>{workspace.name}<br />Workspace</div></div>;
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
      <ellipse cx={loop.cx} cy={loop.cy} rx={loop.rx} ry={loop.ry} fill="none" stroke={theme.production} strokeWidth="10" strokeLinecap="round" pathLength="1000" strokeDasharray="125 875" strokeDashoffset={tracerOffset} opacity={loopOpacity} style={{filter: `drop-shadow(0 0 12px ${theme.production})`}} />
      <path d={`M${loop.cx + loop.rx - 8} ${loop.cy - 10} L${loop.cx + loop.rx + 8} ${loop.cy} L${loop.cx + loop.rx - 8} ${loop.cy + 10} Z`} fill={theme.governance} opacity={loopRestingOpacity * 2.2} />
    </AnimatedDataFlow>
    {steps.map((step, index) => {
      if (frame < stepTimes[index]) return null;
      if (hideStep7 && step.number === 7) return null;
      const enter = spring({frame: frame - stepTimes[index], fps, durationInFrames: timing.workflowStepEnter, config: {damping: 19, stiffness: 92}});
      return <div key={step.number} style={{position: 'absolute', left: step.x, top: step.y}}><StepCard {...step} enter={enter} active={activeIndex === index} /></div>;
    })}
    <LifecycleMascot pose="writing" x={68} y={365} size={96} enterAt={stepTimes[2]} />
    <LifecycleMascot pose="validate" x={820} y={890} size={90} enterAt={stepTimes[3] + 8} />
    <LifecycleMascot pose="prod" x={1110} y={535} size={150} enterAt={stepTimes[5]} />
    <div style={{position: 'absolute', left: loop.captionLeft, top: loop.captionTop, width: 300, textAlign: 'center', color: '#dce7f5', fontSize: 24, fontWeight: 720, opacity: loopOpacity}}>Iterate until validations pass</div>
  </div>;
};
