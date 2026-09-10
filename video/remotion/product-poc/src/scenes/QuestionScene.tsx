import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {VIDEO_CONFIG} from '../videoConfig';

export const QuestionScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 72}});
  const exitStart = VIDEO_CONFIG.scenes.question - 30;
  const exit = interpolate(frame, [exitStart, VIDEO_CONFIG.scenes.question], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: exit}}>
    <div style={{fontSize: VIDEO_CONFIG.text.question, lineHeight: 1, fontWeight: 820, letterSpacing: -6, color: '#fff', transform: `scale(${0.9 + enter * 0.1})`, opacity: enter}}>Where do I start?</div>
  </div>;
};
