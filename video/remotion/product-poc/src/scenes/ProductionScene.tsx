import {Easing, interpolate, interpolateColors, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {DataContract, Notebook, StatusBadge, Workspace} from '../components/Primitives';
import {theme} from '../theme';

export const ProductionScene = () => {
  const frame=useCurrentFrame(); const {fps}=useVideoConfig();
  const travel=interpolate(frame,[35,112],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
  const lock=spring({frame:frame-110,fps,config:{damping:18,stiffness:140}});
  return <div style={{position:'absolute',inset:0}}>
    <div style={{position:'absolute',top:85,left:0,right:0,textAlign:'center'}}><div style={{fontSize:18,letterSpacing:4,color:theme.production,fontWeight:800}}>CONTROLLED PROMOTION</div><div style={{fontSize:49,color:theme.text,fontWeight:720,marginTop:12}}>Validated together. Promoted together.</div></div>
    <Workspace label="Production" color={theme.production} style={{left:435,top:330,width:1050,height:540,opacity:interpolate(frame,[0,28],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),transform:`perspective(900px) rotateX(${interpolate(frame,[0,40],[7,0],{extrapolateRight:'clamp'})}deg)`}}>
      <div style={{position:'absolute',left:240,top:205,width:570,height:2,background:`linear-gradient(90deg,transparent,${theme.production},transparent)`,opacity:lock}} />
    </Workspace>
    <div style={{position:'absolute',left:interpolate(travel,[0,1],[1235,650]),top:interpolate(travel,[0,1],[665,520]),transform:`scale(${interpolate(travel,[0,1],[.82,1])})`,zIndex:4}}><Notebook color={interpolateColors(travel,[0,1],[theme.engineering,theme.production])} /></div>
    <div style={{position:'absolute',left:interpolate(travel,[0,1],[836,1025]),top:interpolate(travel,[0,1],[460,495]),transform:`scale(${interpolate(travel,[0,1],[.82,1])})`,zIndex:4}}><DataContract active={travel>.72} /></div>
    <div style={{position:'absolute',left:860,top:740,opacity:lock,transform:`translateY(${(1-lock)*18}px)`}}><StatusBadge label="LOCKED FOR PRODUCTION" /></div>
    <div style={{position:'absolute',left:930,top:565,fontSize:34,color:theme.production,opacity:lock,transform:`scale(${lock})`}}>＋</div>
  </div>;
};
