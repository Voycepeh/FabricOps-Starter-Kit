import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../../theme';
import {Contract, NotebookNode, Rail, SceneTitle, TableNode, clamp} from '../components/OverviewPrimitives';

const phaseOpacity = (frame: number, start: number, end: number) => interpolate(frame, [start, start + 90, end - 90, end], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const EngineeringChoicesScene = () => {
  const frame = useCurrentFrame();
  const configuration = phaseOpacity(frame, 0, 520);
  const pyspark = phaseOpacity(frame, 430, 980);
  const governance = phaseOpacity(frame, 890, 1420);
  const summary = clamp(frame, 1420, 1580);
  const flow = (offset: number) => interpolate((frame - 560 - offset) % 150, [0, 150], [-180, 310]);
  return <div style={{position: 'absolute', inset: 0}}>
    <SceneTitle kicker="ENGINEERING CHOICES">Three principles. One system.</SceneTitle>
    <div style={{position: 'absolute', inset: '260px 0 0'}}>
      <div style={{position: 'absolute', inset: 0, opacity: configuration, transform: `scale(${.92 + configuration * .08})`}}>
        <NotebookNode number="00" label="Environment Config" color={theme.neutral} style={{position: 'absolute', left: 760, top: 70, width: 400, height: 220}} />
        <div style={{position: 'absolute', left: 430, top: 430, display: 'flex', gap: 170}}>{['01 Governance', '02 Engineering', '99 Explore'].map((label, index) => <NotebookNode key={label} number={label.slice(0, 2)} label={label.slice(3)} color={index === 0 ? theme.governance : index === 2 ? theme.consumer : theme.engineering} />)}</div>
        <svg width="1920" height="820" style={{position: 'absolute', inset: 0}}>{[560, 960, 1360].map((x, index) => <path key={x} d={`M960 290 C960 380 ${x} 350 ${x} 430`} fill="none" stroke={[theme.governance, theme.engineering, theme.consumer][index]} strokeWidth="6" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - clamp(frame, 130 + index * 45, 330 + index * 45)} />)}</svg>
      </div>
      <div style={{position: 'absolute', inset: 0, opacity: pyspark, transform: `scale(${.92 + pyspark * .08})`}}>
        <TableNode label="source data" style={{position: 'absolute', left: 260, top: 260, width: 300, height: 210}} />
        <NotebookNode number="02" label="PySpark transformation" style={{position: 'absolute', left: 710, top: 130, width: 500, height: 310}} />
        <TableNode label="engineered data" active style={{position: 'absolute', right: 260, top: 260, width: 300, height: 210}} />
        {[0, 1, 2].map(index => <div key={index} style={{position: 'absolute', left: flow(index * 45) + 560, top: 350 + index * 32, width: 70, height: 22, borderRadius: 5, background: theme.engineering, boxShadow: `0 0 22px ${theme.engineering}`}} />)}
      </div>
      <div style={{position: 'absolute', inset: 0, opacity: governance, transform: `scale(${.92 + governance * .08})`}}>
        <TableNode label="engineering table" style={{position: 'absolute', left: 330, top: 230, width: 360, height: 240, transform: `translateX(${clamp(frame, 980, 1240) * 190}px)`}} />
        <Rail progress={clamp(frame, 1040, 1280)} color={theme.governance} style={{position: 'absolute', left: 700, top: 350, width: 300, height: 10}} />
        <Contract label="Validation contract" active={frame > 1250} style={{position: 'absolute', right: 410, top: 190, width: 380, height: 300}} />
      </div>
    </div>
    <div style={{position: 'absolute', left: 180, right: 180, bottom: 145, display: 'flex', justifyContent: 'space-between', opacity: summary}}>{[['Configuration driven', theme.neutral], ['PySpark first', theme.engineering], ['Governance as Code', theme.governance]].map(([label, color]) => <div key={label} style={{fontSize: 38, fontWeight: 780, color}}>{label}</div>)}</div>
  </div>;
};
