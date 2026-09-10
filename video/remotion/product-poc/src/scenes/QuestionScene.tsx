import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const QuestionScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - 8, fps, config: {damping: 18, stiffness: 72}});
  const exit = interpolate(frame, [135, 180], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: `rgba(5, 11, 22, ${interpolate(frame, [0, 45], [0, 0.76], {extrapolateRight: 'clamp'})})`, opacity: exit}}>
    <div style={{fontSize: 132, lineHeight: 1, fontWeight: 800, letterSpacing: -6, color: '#fff', textShadow: '0 18px 70px #000', transform: `translateY(${(1 - enter) * 45}px) scale(${0.9 + enter * 0.1})`, opacity: enter}}>Where do I start?</div>
  </div>;
};
