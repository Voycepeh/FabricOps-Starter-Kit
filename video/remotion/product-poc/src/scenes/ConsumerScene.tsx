import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ConsumerWorkspace} from '../components/ConsumerWorkspace';
import {Connector, DataContract, Notebook, Workspace} from '../components/Primitives';
import {theme} from '../theme';

const points=[{x:85,y:180},{x:85,y:450},{x:85,y:720},{x:1657,y:180},{x:1657,y:450},{x:1657,y:720},{x:871,y:880}];
export const ConsumerScene=()=>{
 const frame=useCurrentFrame(); const {fps}=useVideoConfig();
 const hero=spring({frame,fps,config:{damping:20,stiffness:80}});
 const lines=interpolate(frame,[46,112],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
 const title=interpolate(frame,[125,165],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <div style={{position:'absolute',inset:0}}>
   <div style={{position:'absolute',left:610,top:285,transform:`scale(${.82+.18*hero})`,opacity:hero,zIndex:3}}><Workspace label="Production" color={theme.production} compact style={{position:'relative',width:700,height:470}}><div style={{position:'absolute',left:66,top:155,transform:'scale(.78)'}}><Notebook color={theme.production}/></div><div style={{position:'absolute',right:70,top:124,transform:'scale(.78)'}}><DataContract active/></div><div style={{position:'absolute',left:260,top:360,color:theme.production,fontSize:15,fontWeight:800,letterSpacing:2}}>ONLY APPROVED SOURCE</div></Workspace></div>
   {points.map((p,i)=>{const cx=p.x+89,cy=p.y+39;const startX=cx<960?610:cx>960?1310:960;const startY=520;const pLine=interpolate(lines,[i*.06,Math.min(1,i*.06+.58)],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});const enter=spring({frame:frame-44-i*6,fps,config:{damping:19,stiffness:110}});return <div key={i}><Connector x1={startX} y1={startY} x2={cx} y2={cy} color={theme.consumer} progress={pLine} width={2}/><div style={{position:'absolute',left:p.x,top:p.y,opacity:enter,transform:`scale(${.72+.28*enter})`,zIndex:4}}><ConsumerWorkspace label={`Consumer ${i+1}`}/></div></div>})}
   <div style={{position:'absolute',top:65,left:0,right:0,textAlign:'center',opacity:title}}><div style={{fontSize:57,fontWeight:760,letterSpacing:-2,color:theme.text}}>Governed delivery, end to end.</div><div style={{fontSize:22,color:theme.muted,marginTop:15}}>Seven consumers · one Production source</div></div>
 </div>;
};
