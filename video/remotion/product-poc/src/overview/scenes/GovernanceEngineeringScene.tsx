import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../../theme';
import {Contract, NotebookNode, TableNode, WorkspacePanel, clamp} from '../components/OverviewPrimitives';

const governanceSteps = ['Data Agreement', 'Catalogue', 'Enrichment + Guardrails', 'Data Contract'];
const engineeringSteps = ['ETL', 'Profile', 'Catalogue metadata', 'Select Data Contract', 'Validate'];
const Progress = ({steps, active, color}: {steps: string[]; active: number; color: string}) => <div style={{position: 'absolute', left: 36, right: 36, bottom: 38, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>{steps.map((step, index) => <div key={step} style={{fontSize: index === active ? 25 : 20, fontWeight: index === active ? 800 : 600, color: index === active ? color : theme.muted, opacity: index === active ? 1 : .42, textAlign: 'center', maxWidth: 180}}>{step}</div>)}</div>;
const GovernanceVisual = ({active}: {active: number}) => <div style={{position: 'absolute', left: 85, right: 85, top: 135, height: 390, display: 'grid', placeItems: 'center'}}>{active === 3 ? <Contract style={{width: 430, height: 310}} /> : active === 1 ? <TableNode label="METADATA_DATA_CATALOGUE" style={{width: 500, height: 300}} /> : <div style={{fontSize: active === 0 ? 62 : 52, fontWeight: 800, color: theme.governance, textAlign: 'center'}}>{governanceSteps[active]}<div style={{width: 340, height: 10, background: theme.governance, margin: '45px auto 0', borderRadius: 10}} /></div>}</div>;
const EngineeringVisual = ({active}: {active: number}) => <div style={{position: 'absolute', left: 70, right: 70, top: 135, height: 390, display: 'grid', placeItems: 'center'}}>{active === 2 ? <TableNode label="Catalogue metadata" active style={{width: 500, height: 300}} /> : active === 3 ? <Contract label="Selected Data Contract" style={{width: 430, height: 310}} /> : <NotebookNode number="02" label={engineeringSteps[active]} color={active === 4 ? theme.production : theme.engineering} style={{width: 500, height: 310}} />}</div>;

export const GovernanceEngineeringScene = () => {
  const frame = useCurrentFrame();
  const focus = clamp(frame, 1450, 1900);
  const validation = clamp(frame, 2450, 3000);
  const governanceActive = Math.min(3, Math.floor(frame / 340));
  const engineeringActive = Math.min(4, Math.max(0, Math.floor((frame - 1550) / 300)));
  const focusedWidth = 1050;
  const quietWidth = 560;
  const gap = 70;
  const leftMargin = 120;
  const governanceWidth = interpolate(focus, [0, 1], [focusedWidth, quietWidth]);
  const engineeringWidth = interpolate(focus, [0, 1], [quietWidth, focusedWidth]);
  const engineeringLeft = leftMargin + governanceWidth + gap;
  return <div style={{position: 'absolute', inset: 0}}>
    <WorkspacePanel title="Governance workspace" color={theme.governance} style={{position: 'absolute', left: leftMargin, top: 150, width: governanceWidth, height: 760, opacity: 1 - focus * .55}}><GovernanceVisual active={governanceActive} /><Progress steps={governanceSteps} active={governanceActive} color={theme.governance} /></WorkspacePanel>
    <WorkspacePanel title="Engineering workspace" color={theme.engineering} style={{position: 'absolute', left: engineeringLeft, top: 150, width: engineeringWidth, height: 760, opacity: .45 + focus * .55}}><EngineeringVisual active={engineeringActive} /><Progress steps={engineeringSteps} active={engineeringActive} color={engineeringActive === 4 ? theme.production : theme.engineering} /></WorkspacePanel>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}><path d="M570 920 C610 1040 1310 1040 1350 920 M1350 150 C1310 55 610 55 570 150" fill="none" stroke={theme.production} strokeWidth="8" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - validation} opacity={.8} /></svg>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 25, textAlign: 'center', fontSize: 30, fontWeight: 760, color: theme.production, opacity: validation}}>Validation results return to Governance</div>
  </div>;
};
