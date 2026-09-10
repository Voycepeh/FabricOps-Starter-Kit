import {DataWarehouse48Item} from '@fabric-msft/svg-icons';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

const OutcomeCard = ({label, delay}: {label: string; delay: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - delay, fps, config: {damping: 19, stiffness: 90}});
  return <div style={{width: 230, height: 135, borderRadius: 28, display: 'grid', placeItems: 'center', textAlign: 'center', whiteSpace: 'pre-line', background: `${theme.consumer}1c`, border: `2px solid ${theme.consumer}88`, color: '#fff', fontSize: 29, fontWeight: 760, opacity: enter, transform: `translateY(${(1 - enter) * 30}px)`}}>{label}</div>;
};

export const OutcomeScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const production = spring({frame, fps, config: {damping: 20, stiffness: 80}});
  const data = spring({frame: frame - 45, fps, config: {damping: 20, stiffness: 80}});
  const consumer = spring({frame: frame - 85, fps, config: {damping: 20, stiffness: 80}});
  const exit = interpolate(frame, [205, 240], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', padding: '0 105px', gap: 35, opacity: exit}}>
    <div style={{width: 340, height: 310, flex: '0 0 auto', borderRadius: 42, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20, background: `${theme.production}1a`, border: `3px solid ${theme.production}`, opacity: production, transform: `scale(${0.88 + production * 0.12})`}}><DataWarehouse48Item width={105} height={105} /><div style={{fontSize: 34, lineHeight: 1.15, textAlign: 'center', fontWeight: 800}}>Engineering Production</div></div>
    <div style={{display: 'flex', alignItems: 'center', gap: 12, opacity: data}}><div style={{width: 80, height: 6, background: theme.production}} /><div style={{padding: '22px 24px', borderRadius: 99, background: theme.production, color: '#07101f', fontSize: 27, fontWeight: 850, textAlign: 'center'}}>approved<br />Production data</div><div style={{width: 80, height: 6, background: theme.consumer}} /></div>
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 28, opacity: consumer}}><div style={{fontSize: 38, color: theme.consumer, fontWeight: 850}}>Consumer Workspace</div><div style={{display: 'flex', gap: 20}}><OutcomeCard label="Power BI" delay={105} /><OutcomeCard label={'AI / machine\nlearning'} delay={125} /><OutcomeCard label="Data Science" delay={145} /></div></div>
  </div>;
};
