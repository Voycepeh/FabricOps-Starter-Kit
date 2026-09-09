import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

export const FinishScene=()=>{
 const frame=useCurrentFrame(); const {fps}=useVideoConfig();
 const enter=spring({frame,fps,config:{damping:22,stiffness:80}});
 const cta=interpolate(frame,[35,75],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column'}}>
   <div style={{fontSize:92,fontWeight:780,letterSpacing:-5,color:theme.text,opacity:enter,transform:`translateY(${(1-enter)*24}px)`}}>Fabric<span style={{color:theme.production}}>Ops</span></div>
   <div style={{display:'flex',gap:13,marginTop:24,color:theme.muted,fontSize:18,letterSpacing:.4,opacity:enter}}><span>Lightweight.</span><span>Self-contained.</span><span style={{color:'#dbe6f2'}}>Built for Microsoft Fabric.</span></div>
   <div style={{display:'flex',gap:16,marginTop:55,opacity:cta}}><div style={{padding:'14px 22px',borderRadius:99,border:'1px solid #74869e66',color:'#dbe5f2',background:'#101b2b'}}>How FabricOps works&nbsp; →</div><div style={{padding:'14px 22px',borderRadius:99,border:`1px solid ${theme.production}77`,color:theme.production,background:`${theme.production}12`}}>Guided demo&nbsp; →</div></div>
 </div>;
};
