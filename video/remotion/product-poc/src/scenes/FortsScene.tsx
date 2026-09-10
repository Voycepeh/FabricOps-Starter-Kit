import type {ReactNode} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Connector, DataContract, Notebook, Pipeline, StatusBadge, ValidationPulse} from '../components/Primitives';
import {theme} from '../theme';

const Fort = ({side, color, children}: {side: 'left'|'right'; color: string; children: ReactNode}) => {
  const frame=useCurrentFrame(); const {fps}=useVideoConfig();
  const build=spring({frame:frame-(side==='left'?0:12),fps,config:{damping:19,stiffness:85}});
  const left=side==='left'?135:1135;
  return <div style={{position:'absolute',left,top:230,width:650,height:600,opacity:build,transform:`translateY(${(1-build)*70}px)`}}>
    <div style={{position:'absolute',left:30,right:30,bottom:0,height:410,border:`1px solid ${color}66`,borderRadius:'110px 110px 32px 32px',background:`linear-gradient(155deg,${color}14,#0b1628e8)`,boxShadow:`0 35px 80px #0009,inset 0 1px #fff12`}} />
    <div style={{position:'absolute',left:0,bottom:0,width:145,height:265,border:`1px solid ${color}77`,borderRadius:'46px 46px 24px 24px',background:'#101d31'}} />
    <div style={{position:'absolute',right:0,bottom:0,width:145,height:265,border:`1px solid ${color}77`,borderRadius:'46px 46px 24px 24px',background:'#101d31'}} />
    <div style={{position:'absolute',left:62,right:62,top:0,bottom:38}}>{children}</div>
  </div>;
};

export const FortsScene=()=>{
 const frame=useCurrentFrame(); const {fps}=useVideoConfig();
 const bridge=interpolate(frame,[115,205],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
 const align=spring({frame:frame-200,fps,config:{damping:18,stiffness:130}});
 return <div style={{position:'absolute',inset:0}}>
   <Fort side="left" color={theme.governance}><div style={{position:'absolute',left:130,top:82,color:theme.governance,fontWeight:750,fontSize:19}}>Governance</div><div style={{position:'absolute',left:95,top:145,display:'grid',gridTemplateColumns:'repeat(2,100px)',gap:20}}>{['POLICY','METADATA','RULES','TERMS'].map((v,i)=><div key={v} style={{height:76,borderRadius:16,border:`1px solid ${theme.governance}55`,background:`${theme.governance}${i===0?'25':'12'}`,display:'grid',placeItems:'center',color:'#d9c8fa',fontSize:12,letterSpacing:1}}>{v}</div>)}</div></Fort>
   <Fort side="right" color={theme.engineering}><div style={{position:'absolute',left:150,top:82,color:theme.engineering,fontWeight:750,fontSize:19}}>Engineering</div><div style={{position:'absolute',left:90,top:150}}><Notebook /></div><div style={{position:'absolute',left:118,top:315,transform:'scale(.72)'}}><Pipeline /></div></Fort>
   <Connector from={{x:785,y:570}} to={{x:841,y:522}} color={theme.governance} progress={bridge} route="curve" lane={815} />
   <Connector from={{x:1135,y:570}} to={{x:1079,y:522}} color={theme.engineering} progress={Math.max(0,bridge*1.4-.4)} route="curve" lane={1105} />
   <div style={{position:'absolute',left:841,top:438,opacity:bridge,transform:`scale(${.65+.35*bridge})`,zIndex:5}}><DataContract active={align>.65}/></div>
   {bridge>.5?<div style={{position:'absolute',left:870,top:430,zIndex:4}}><ValidationPulse start={180} size={180}/></div>:null}
   <div style={{position:'absolute',left:915,top:630,opacity:align,transform:`translateY(${(1-align)*14}px)`,zIndex:6}}><StatusBadge/></div>
 </div>;
};
