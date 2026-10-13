import {AbsoluteFill, Easing, Img, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {mascotSrc, type MascotName} from '../mascotAssets';
import {NARRATION_CUE_SHEET} from '../narrationCues';
import {theme} from '../theme';
import {GUIDED_SCENE_DURATIONS, LIFECYCLE_HANDOFF_LOCAL_FRAME, OVERVIEW_HANDOFF_FRAME, seconds} from '../videoConfig';
import {LifecycleScene, STEP_7_LABEL, StepCard} from './LifecycleScene';

// Use the same mascot artwork as the documentation. Motion is limited to scene
// entrances; the robot remains stationary while viewers read the information.
const Mascot = ({pose, x, y, size = 260, delay = 0}: {pose: MascotName; x: number; y: number; size?: number; delay?: number}) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [delay, delay + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return <Img src={mascotSrc(pose)} style={{
    position: 'absolute', left: x, top: y, width: size, height: size,
    objectFit: 'contain', opacity: enter,
    transform: `translateY(${(1 - enter) * 22}px)`,
    filter: 'drop-shadow(0 12px 22px #0006)', pointerEvents: 'none',
  }} />;
};


const consumers = [
  {title: 'Dashboards', color: '#f2c811', left: 180, icon: 'bars'},
  {title: 'Data Agents', color: '#38d991', left: 600, icon: 'hex'},
  {title: 'Applications', color: '#52d6c6', left: 1020, icon: 'app'},
  {title: 'ML Models', color: '#a879ff', left: 1440, icon: 'nodes'},
] as const;

// Consumption continues at the lifecycle handoff and follows the master narration cues.
const CONSUMPTION_CUE = NARRATION_CUE_SHEET.consumption;
const localCueFrame = (index: number) => CONSUMPTION_CUE.keyPhrases[index].triggerFrame - CONSUMPTION_CUE.startFrame;
const STEP_7_REVEAL = localCueFrame(0);
const STEP_7_CARD_ENTER_FRAMES = 18;
const STEP_7_LABEL_DELAY_FRAMES = 5;
const STEP_7_LABEL_FADE_FRAMES = 8;
const STEP_7_FOCUS_START = localCueFrame(1);
const STEP_7_FOCUS_END = localCueFrame(2);
const FOUNDATION_TRANSFORMATION_START = localCueFrame(2) + seconds(0.35);
const FOUNDATION_TRANSFORMATION_END = localCueFrame(3) - seconds(0.45);
const CONSUMER_REVEAL_FRAMES = [localCueFrame(3), localCueFrame(4), localCueFrame(5), localCueFrame(6)];
const CONSUMER_REVEAL_DURATION = seconds(0.55);
const CONSUMPTION_SCENE_END = GUIDED_SCENE_DURATIONS.consumption;
const CONSUMPTION_SCENE_FADE_START = CONSUMPTION_SCENE_END - seconds(0.6);

const CardIcon = ({kind, color}: {kind: string; color: string}) => {
  if (kind === 'bars') {
    return <div style={{display: 'flex', alignItems: 'end', gap: 8, height: 64}}>
      {[34, 50, 64].map((height) => <div key={height} style={{width: 22, height, borderRadius: 7, background: color}} />)}
    </div>;
  }
  if (kind === 'hex') {
    return <div style={{position: 'relative', width: 72, height: 62}}>
      <div style={{position: 'absolute', left: 24, top: 0, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, background: color}} />
      <div style={{position: 'absolute', left: 2, top: 30, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, border: `4px solid ${color}`}} />
      <div style={{position: 'absolute', left: 44, top: 30, width: 30, height: 30, transform: 'rotate(30deg)', borderRadius: 8, background: color}} />
    </div>;
  }
  if (kind === 'nodes') {
    return <div style={{position: 'relative', width: 72, height: 64}}>
      {[{l:4,t:24},{l:28,t:4},{l:48,t:30},{l:26,t:44}].map((p, i) => <div key={i} style={{position: 'absolute', left: p.l, top: p.t, width: 18, height: 18, borderRadius: 99, background: color, boxShadow: `0 0 18px ${color}88`}} />)}
      <div style={{position: 'absolute', left: 12, top: 30, width: 46, height: 4, background: color, transform: 'rotate(-20deg)', transformOrigin: 'center'}} />
      <div style={{position: 'absolute', left: 26, top: 20, width: 4, height: 32, background: color}} />
    </div>;
  }
  return <div style={{width: 72, height: 58, borderRadius: 12, border: `4px solid ${color}`, overflow: 'hidden'}}>
    <div style={{height: 12, background: color}} />
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 18px)', gap: 7, padding: '8px 11px'}}>
      {[0, 1, 2, 3].map((i) => <div key={i} style={{height: 8, borderRadius: 4, background: i === 0 ? color : `${color}88`}} />)}
    </div>
  </div>;
};

const ConsumerCard = ({title, color, icon, progress}: {title: string; color: string; icon: string; progress: number}) => (
  <div style={{
    width: 300,
    height: 230,
    borderRadius: 24,
    border: `2px solid ${color}99`,
    background: 'linear-gradient(145deg, #14263d, #0d192b 76%)',
    boxShadow: '0 18px 38px #0007',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 22,
    padding: '24px 28px',
    boxSizing: 'border-box',
    opacity: progress,
    translate: `0 ${(1 - progress) * 18}px`,
  }}>
    <div style={{height: 72, display: 'grid', placeItems: 'center'}}><CardIcon kind={icon} color={color} /></div>
    <div style={{fontSize: 29, fontWeight: 820, color: '#f7f9fd', lineHeight: 1.12, textAlign: 'center'}}>{title}</div>
  </div>
);

export const ConsumptionScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const stepEnter = spring({frame: frame - STEP_7_REVEAL, fps, durationInFrames: STEP_7_CARD_ENTER_FRAMES, config: {damping: 19, stiffness: 92}});
  const stepLabelEnter = interpolate(
    frame,
    [
      STEP_7_REVEAL + STEP_7_CARD_ENTER_FRAMES + STEP_7_LABEL_DELAY_FRAMES,
      STEP_7_REVEAL + STEP_7_CARD_ENTER_FRAMES + STEP_7_LABEL_DELAY_FRAMES + STEP_7_LABEL_FADE_FRAMES,
    ],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)},
  );
  const focus = interpolate(frame, [STEP_7_FOCUS_START, STEP_7_FOCUS_END], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const foundation = interpolate(frame, [FOUNDATION_TRANSFORMATION_START, FOUNDATION_TRANSFORMATION_END], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)});
  const pipelineOpacity = interpolate(frame, [FOUNDATION_TRANSFORMATION_START, FOUNDATION_TRANSFORMATION_START + seconds(0.6)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const holdLabelOpacity = interpolate(frame, [CONSUMER_REVEAL_FRAMES[3], CONSUMER_REVEAL_FRAMES[3] + seconds(0.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const sceneOpacity = interpolate(frame, [CONSUMPTION_SCENE_FADE_START, CONSUMPTION_SCENE_END], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const cardScale = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [1, 3.1]) : interpolate(foundation, [0, 1], [3.1, 1]);
  const cardCenterX = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [1615, 960]) : 960;
  const cardCenterY = frame < FOUNDATION_TRANSFORMATION_START ? interpolate(focus, [0, 1], [840, 540]) : interpolate(foundation, [0, 1], [540, 865]);
  const visualCardWidth = frame < FOUNDATION_TRANSFORMATION_START ? 340 * cardScale : interpolate(foundation, [0, 1], [1054, 1640]);
  const visualCardHeight = frame < FOUNDATION_TRANSFORMATION_START ? 150 * cardScale : interpolate(foundation, [0, 1], [465, 180]);
  const cardWidth = visualCardWidth / cardScale;
  const cardHeight = visualCardHeight / cardScale;
  const visualCircleSize = frame < FOUNDATION_TRANSFORMATION_START ? 62 * cardScale : interpolate(foundation, [0, 1], [192, 78]);
  const visualFontSize = frame < FOUNDATION_TRANSFORMATION_START ? 24 * cardScale : interpolate(foundation, [0, 1], [32, 42]);
  const lifecycleZoomScale = interpolate(focus, [0, 1], [1, 3.1]);

  return <AbsoluteFill style={{opacity: sceneOpacity}}>
    <AbsoluteFill style={{opacity: pipelineOpacity, transform: `translate(${(960 - 1615) * focus}px, ${(540 - 840) * focus}px) scale(${lifecycleZoomScale})`, transformOrigin: '1615px 840px'}}>
      <Sequence from={-LIFECYCLE_HANDOFF_LOCAL_FRAME} durationInFrames={LIFECYCLE_HANDOFF_LOCAL_FRAME + CONSUMPTION_SCENE_END} premountFor={fps}>
        <LifecycleScene hideStep7 />
      </Sequence>
    </AbsoluteFill>

    {frame >= STEP_7_REVEAL ? <div style={{position: 'absolute', left: cardCenterX - cardWidth / 2, top: cardCenterY - cardHeight / 2, width: cardWidth, height: cardHeight, scale: cardScale, transformOrigin: '50% 50%', zIndex: 4}}>
      <StepCard
        number={7}
        label={STEP_7_LABEL}
        subtitle="Governed · Reliable · Fit for downstream use"
        subtitleFontSize={22 / cardScale}
        subtitleGap={9 / cardScale}
        subtitleOpacity={holdLabelOpacity}
        singleLineLabel={frame >= FOUNDATION_TRANSFORMATION_START}
        color={theme.consumer}
        enter={stepEnter}
        labelProgress={stepLabelEnter}
        active
        width={cardWidth}
        height={cardHeight}
        borderRadius={interpolate(foundation, [0, 1], [28, 24])}
        circleSize={visualCircleSize / cardScale}
        fontSize={visualFontSize / cardScale}
        gap={interpolate(foundation, [0, 1], [22, 32]) / cardScale}
        horizontalPadding={interpolate(foundation, [0, 1], [25, 44]) / cardScale}
      />
      <div style={{position: 'absolute', left: 34, right: 34, bottom: -18, height: 18, borderRadius: '0 0 12px 12px', background: '#9a5c28', opacity: foundation}} />
    </div> : null}

    <Mascot pose="prod" x={840} y={580} size={190} delay={CONSUMER_REVEAL_FRAMES[0]} />
    {consumers.map((consumer, index) => {
      const progress = interpolate(frame, [CONSUMER_REVEAL_FRAMES[index], CONSUMER_REVEAL_FRAMES[index] + CONSUMER_REVEAL_DURATION], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)});
      return <div key={consumer.title} style={{position: 'absolute', left: consumer.left, top: 250, zIndex: 2}}>
        <ConsumerCard {...consumer} progress={progress} />
        <div style={{position: 'absolute', left: 148, top: 230, width: 4, height: 295, borderRadius: 4, background: `linear-gradient(${consumer.color}99, ${theme.consumer})`, opacity: progress * 0.72}} />
        <div style={{position: 'absolute', left: 140, top: 516, width: 20, height: 20, borderRadius: 4, border: `3px solid ${theme.consumer}`, background: '#0d192b', opacity: progress}} />
      </div>;
    })}

  </AbsoluteFill>;
};
