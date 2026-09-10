import {Notebook48Item} from '@fabric-msft/svg-icons';

export const NotebookNode = ({name, color, active = false}: {name: string; color: string; active?: boolean}) => (
  <div style={{width: 330, height: 210, borderRadius: 34, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, background: `linear-gradient(150deg, ${color}30, #0d1a2d 72%)`, border: `3px solid ${color}${active ? 'ff' : '99'}`, boxShadow: active ? `0 0 62px ${color}66` : '0 24px 50px #0007'}}>
    <Notebook48Item width={90} height={90} aria-hidden="true" />
    <div style={{fontSize: 32, fontWeight: 750, color: '#f7f9fd', letterSpacing: -0.7}}>{name}</div>
  </div>
);
