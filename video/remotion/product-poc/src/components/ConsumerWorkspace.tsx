import {theme} from '../theme';

export const ConsumerWorkspace = ({label}: {label: string}) => (
  <div style={{width: 178, height: 78, borderRadius: 22, border: `1px solid ${theme.consumer}88`, background: `linear-gradient(135deg, ${theme.consumer}18, #111b2bdd)`, boxShadow: '0 16px 35px #0006', display: 'flex', gap: 13, alignItems: 'center', justifyContent: 'center', color: '#f8dec4', fontSize: 17, fontWeight: 650}}>
    <span style={{display: 'grid', gridTemplateColumns: 'repeat(2, 7px)', gap: 4}}>{[0,1,2,3].map(i => <i key={i} style={{width: 7, height: 7, borderRadius: 2, background: theme.consumer}} />)}</span>{label}
  </div>
);
