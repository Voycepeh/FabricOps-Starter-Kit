import {theme} from '../theme';

export type CodeLine = {tokens: Array<{text: string; color?: string}>};

export const CodePanel = ({title, lines, activeLine}: {title: string; lines: CodeLine[]; activeLine: number}) => (
  <div style={{width: 1420, borderRadius: 30, overflow: 'hidden', background: '#091321', border: '1px solid #7691b055', boxShadow: '0 35px 100px #000a'}}>
    <div style={{height: 82, display: 'flex', alignItems: 'center', padding: '0 34px', gap: 12, background: '#111f34', borderBottom: '1px solid #7b91ad33'}}>
      {[theme.consumer, '#f2c94c', theme.production].map((color) => <div key={color} style={{width: 17, height: 17, borderRadius: 99, background: color}} />)}
      <div style={{marginLeft: 25, fontSize: 29, fontWeight: 720, color: theme.text}}>{title}</div>
    </div>
    <div style={{padding: '30px 34px 34px', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace', fontSize: 32, lineHeight: 1.75}}>
      {lines.map((line, index) => <div key={index} style={{display: 'flex', borderRadius: 10, padding: '0 18px', background: index === activeLine ? '#4ea1ff22' : 'transparent', borderLeft: index === activeLine ? `5px solid ${theme.engineering}` : '5px solid transparent', opacity: index === activeLine ? 1 : 0.58}}>
        <span style={{width: 54, color: '#63758d', userSelect: 'none'}}>{index + 1}</span>
        <span>{line.tokens.map((token, tokenIndex) => <span key={tokenIndex} style={{color: token.color ?? '#d8e4f3'}}>{token.text}</span>)}</span>
      </div>)}
    </div>
  </div>
);
