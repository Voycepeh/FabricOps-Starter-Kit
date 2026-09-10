import type {CSSProperties} from 'react';
import {theme} from '../theme';

export const ConceptChip = ({label, color = theme.neutral, style}: {label: string; color?: string; style?: CSSProperties}) => (
  <div style={{position: 'absolute', padding: '11px 17px', borderRadius: 99, background: '#111d30e8', border: `1px solid ${color}77`, boxShadow: '0 12px 30px #0008', color: '#d6deea', fontFamily: 'monospace', fontSize: 15, ...style}}>{label}</div>
);

export const DataStore = ({label, color = theme.engineering}: {label: string; color?: string}) => (
  <div style={{width: 150, height: 120, position: 'relative', color: theme.text, textAlign: 'center', fontSize: 15}}>
    <div style={{position: 'absolute', top: 10, left: 20, width: 110, height: 72, border: `2px solid ${color}`, borderRadius: '50% / 18%', background: `linear-gradient(180deg, ${color}33, #101c2f)`, boxShadow: `0 18px 35px #0007`}} />
    <div style={{position: 'absolute', top: 25, left: 20, width: 110, height: 55, borderBottom: `2px solid ${color}`, borderRadius: '0 0 50% 50% / 0 0 20% 20%'}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 7}}>{label}</div>
  </div>
);

export const LineageGraph = () => <svg width="165" height="105" viewBox="0 0 165 105" style={{filter: 'drop-shadow(0 14px 22px #0008)'}}>
  <path d="M25 51 C58 5 99 12 139 34 M25 51 C65 94 105 92 139 70" fill="none" stroke={theme.governance} strokeWidth="2" opacity=".75" />
  {[[25,51],[82,19],[82,87],[139,34],[139,70]].map(([x,y],i)=><rect key={i} x={x-9} y={y-9} width="18" height="18" rx="5" fill="#15233a" stroke={theme.governance} strokeWidth="2" />)}
  <text x="82" y="103" textAnchor="middle" fill="#d5c5f7" fontSize="13">Data Lineage</text>
</svg>;

export const QualityCheck = () => <div style={{width: 135, height: 92, borderRadius: 20, background: '#102238', border: `1px solid ${theme.production}77`, display: 'grid', placeItems: 'center', boxShadow: '0 14px 30px #0007'}}><span style={{width: 39, height: 39, borderRadius: 99, display: 'grid', placeItems: 'center', background: `${theme.production}22`, border: `2px solid ${theme.production}`, color: theme.production, fontSize: 23}}>✓</span><span style={{position: 'absolute', marginTop: 65, color: '#bcebd5', fontSize: 13}}>Data Quality</span></div>;

export const ParallelFlow = () => <svg width="180" height="95" viewBox="0 0 180 95"><path d="M12 47 H48 M48 47 C70 47 66 18 92 18 H166 M48 47 H166 M48 47 C70 47 66 76 92 76 H166" fill="none" stroke={theme.engineering} strokeWidth="3" strokeLinecap="round"/><circle cx="12" cy="47" r="7" fill={theme.engineering}/><text x="90" y="93" textAnchor="middle" fill="#b8d9ff" fontSize="13">Parallel Processing</text></svg>;
