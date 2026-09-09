import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Connector, DataContract, Notebook, StatusBadge, ValidationPulse, Workspace} from '../components/Primitives';
import {theme} from '../theme';

export const OperatingModelScene = () => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 90}});
  const contract = spring({frame: frame-40, fps, config: {damping: 20, stiffness: 100}});
  const flow = interpolate(frame, [82, 128], [0,1], {extrapolateLeft:'clamp', extrapolateRight:'clamp', easing:Easing.inOut(Easing.cubic)});
  const pass = spring({frame: frame-132, fps, config: {damping: 16, stiffness: 145}});
  return <div style={{position:'absolute', inset:0}}>
    <div style={{position:'absolute', top:72, left:0, right:0, textAlign:'center', opacity:enter}}><div style={{fontSize:18, letterSpacing:4, color:theme.muted, fontWeight:700}}>ONE OPERATING MODEL</div><div style={{fontSize:48, color:theme.text, fontWeight:720, marginTop:10, letterSpacing:-1.7}}>Governance defines. Engineering delivers.</div></div>
    <div style={{transform:`translateX(${(1-enter)*-90}px)`, opacity:enter}}><Workspace label="Governance workspace" color={theme.governance} style={{left:115, top:260, width:560, height:520}}><div style={{position:'absolute', left:155, top:175}}><div style={{fontSize:17, color:theme.governance, marginBottom:17, textAlign:'center', fontWeight:700}}>OWNS</div><DataContract /></div></Workspace></div>
    <div style={{transform:`translateX(${(1-enter)*90}px)`, opacity:enter}}><Workspace label="Engineering Development" color={theme.engineering} style={{right:115, top:260, width:560, height:520}}><div style={{position:'absolute', left:160, top:184}}><Notebook /></div><div style={{position:'absolute', left:200, top:340, fontSize:15, letterSpacing:2, fontWeight:750, color:theme.engineering}}>BUILD · RUN · VALIDATE</div></Workspace></div>
    <div style={{position:'absolute', left:836, top:425, opacity:contract, transform:`scale(${.7+.3*contract})`, zIndex:4}}><DataContract /></div>
    <Connector x1={675} y1={525} x2={836} y2={510} color={theme.governance} progress={contract} />
    <Connector x1={1084} y1={555} x2={1245} y2={525} color={theme.engineering} progress={contract} />
    <Connector x1={1245} y1={620} x2={1084} y2={620} color={theme.production} progress={flow} width={4} />
    {flow>.1 && <div style={{position:'absolute', left:855, top:508, zIndex:3}}><ValidationPulse start={112} /></div>}
    <div style={{position:'absolute', left:859, top:665, opacity:pass, transform:`scale(${.7+.3*pass})`}}><StatusBadge /></div>
  </div>;
};
