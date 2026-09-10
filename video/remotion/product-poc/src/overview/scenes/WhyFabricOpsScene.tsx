import type {ComponentType, ReactNode, SVGProps} from 'react';
import {Fabric48Color, Notebook48Item, Pipeline48Item} from '@fabric-msft/svg-icons';
import {useCurrentFrame} from 'remotion';
import {theme} from '../../theme';
import {FabricOpsLogo, Rail, SceneTitle, clamp} from '../components/OverviewPrimitives';

type Icon = ComponentType<SVGProps<SVGSVGElement>>;
const Team = () => <svg width="140" height="120" viewBox="0 0 140 120" aria-hidden="true"><g fill={`${theme.engineering}28`} stroke={theme.engineering} strokeWidth="6"><circle cx="70" cy="34" r="22" /><circle cx="28" cy="46" r="16" /><circle cx="112" cy="46" r="16" /><path d="M32 112c2-32 15-48 38-48s36 16 38 48M4 112c1-24 9-38 25-38 10 0 18 5 23 14M136 112c-1-24-9-38-25-38-10 0-18 5-23 14" fill="none" strokeLinecap="round" /></g></svg>;
const Stop = ({Icon, visual, label, color}: {Icon?: Icon; visual?: ReactNode; label: string; color: string}) => <div style={{width: 260, textAlign: 'center'}}><div style={{height: 180, display: 'grid', placeItems: 'center', filter: 'drop-shadow(0 26px 36px #0009)'}}>{visual ?? (Icon ? <Icon width={140} height={140} /> : null)}</div><div style={{fontSize: 30, fontWeight: 720, marginTop: 20, color}}>{label}</div></div>;

export const WhyFabricOpsScene = () => {
  const frame = useCurrentFrame();
  const align = clamp(frame, 650, 1050);
  return <div style={{position: 'absolute', inset: 0}}>
    <SceneTitle kicker="WHY FABRICOPS">Different routes become one practice.</SceneTitle>
    <div style={{position: 'absolute', left: 130, right: 130, top: 350, display: 'flex', justifyContent: 'space-between'}}><Stop visual={<Team />} label="Engineering team" color={theme.engineering} /><Stop Icon={Pipeline48Item} label="Data pipeline" color={theme.engineering} /><Stop Icon={Notebook48Item} label="Notebook" color={theme.governance} /><Stop Icon={Fabric48Color} label="Microsoft Fabric" color={theme.production} /></div>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: 1 - align}}>{[0, 1, 2].map(index => <path key={index} d={`M260 ${650 + index * 38} C600 ${530 + index * 95},1170 ${760 - index * 80},1660 ${650 + index * 20}`} fill="none" stroke={[theme.engineering, theme.governance, theme.consumer][index]} strokeWidth="5" opacity=".55" />)}</svg>
    <Rail progress={align} style={{position: 'absolute', left: 250, right: 250, top: 720, height: 14}} />
    <FabricOpsLogo size={48} style={{position: 'absolute', left: 820, top: 748, opacity: align}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 110, textAlign: 'center', fontSize: 44, fontWeight: 760, opacity: clamp(frame, 1050, 1300)}}>Same platform. One operating practice.</div>
  </div>;
};
