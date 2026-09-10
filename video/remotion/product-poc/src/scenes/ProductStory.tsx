import type {CSSProperties} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {FabricIconCard, SELECTED_FABRIC_ICONS} from '../components/FabricIcons';
import {DataContract, StatusBadge} from '../components/Primitives';
import {theme} from '../theme';

const clamp=(frame:number,input:number[],output:number[])=>interpolate(frame,input,output,{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const items=[
  {key:'notebook',start:[680,330],chaos:[80,115,-7,1.18],group:'g',end:[300,560]},
  {key:'environment',start:[920,330],chaos:[1535,90,6,.9],group:'g',end:[520,560]},
  {key:'lakehouse',start:[1160,330],chaos:[1420,730,-5,1.3],group:'g',end:[410,720]},
  {key:'warehouse',start:[680,570],chaos:[-30,720,8,1.1],group:'e',end:[1300,705]},
  {key:'dataPipeline',start:[920,570],chaos:[1640,410,-7,1.18],group:'e',end:[1515,545]},
  {key:'dataflowGen2',start:[1160,570],chaos:[250,-40,5,.88],group:'e',end:[1515,705]},
] as const;

const Owned=({label,color=theme.governance,style}:{label:string;color?:string;style?:CSSProperties})=><div style={{padding:'10px 16px',borderRadius:12,border:`1px solid ${color}75`,background:`linear-gradient(135deg,${color}25,#101b2b)`,color:'#e9e2f7',fontSize:14,fontWeight:650,boxShadow:'0 14px 28px #0007',...style}}>{label}</div>;

const Workspace=({kind,opacity}:{kind:'Governance'|'Engineering';opacity:number})=>{
 const governance=kind==='Governance',color=governance?theme.governance:theme.engineering,left=governance?120:1050;
 return <div style={{position:'absolute',left,top:430,width:750,height:440,borderRadius:30,border:`1.5px solid ${color}70`,background:`linear-gradient(145deg,${color}18,#0b1729ed 48%)`,boxShadow:`0 32px 85px #0009,inset 0 1px #fff14`,opacity,transform:`translateY(${(1-opacity)*70}px)`}}>
   <div style={{position:'absolute',left:28,top:18,display:'flex',alignItems:'center',gap:13,color,fontSize:23,fontWeight:760}}><FabricIconCard {...SELECTED_FABRIC_ICONS.workspace} style={{minWidth:0,flexDirection:'row',gap:0}}/><span>{kind}</span><span style={{fontSize:12,color:theme.muted,fontWeight:500,letterSpacing:1}}>WORKSPACE</span></div>
   {governance&&<div style={{position:'absolute',left:240,top:95,display:'flex',gap:12}}><Owned label="Metadata"/><Owned label="Policy"/><Owned label="Rules"/></div>}
 </div>;
};

export const ProductStory=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const platformIn=spring({frame:frame-10,fps,config:{damping:20,stiffness:70}});
 const explode=clamp(frame,[145,285],[0,1]);
 const dim=clamp(frame,[292,320,375,405],[0,.86,.86,1]);
 const question=clamp(frame,[294,325,372,405],[0,1,1,0]);
 const organize=clamp(frame,[425,520,650],[0,.05,1]);
 const workspaces=clamp(frame,[485,555],[0,1]);
 const contract=clamp(frame,[680,720],[0,1]);
 const active=clamp(frame,[735,765],[0,1]);
 const cta=clamp(frame,[775,810],[0,1]);
 const sceneOpacity=clamp(frame,[750,790],[1,0]);
 const logoReveal=clamp(frame,[378,420,500,535],[0,1,1,0]);
 return <div style={{position:'absolute',inset:0}}>
  <div style={{position:'absolute',inset:0,opacity:sceneOpacity}}>
   <div style={{position:'absolute',left:430,top:125,width:1060,height:725,borderRadius:42,border:'1px solid #63b7ff68',background:'linear-gradient(145deg,#123258ba,#0a1729d9)',boxShadow:'0 50px 130px #000b, inset 0 1px #bfe3ff24',opacity:platformIn*(1-explode*.72)*(1-dim),transform:`scale(${.88+platformIn*.12-explode*.05})`}}>
    <div style={{position:'absolute',left:52,top:42,display:'flex',alignItems:'center',gap:20}}><FabricIconCard {...SELECTED_FABRIC_ICONS.fabric} style={{minWidth:0,flexDirection:'row'}}/><span style={{fontSize:13,color:'#88a4c4',letterSpacing:2}}>ONE COHESIVE PLATFORM</span></div>
   </div>
   {items.map((item,i)=>{const icon=SELECTED_FABRIC_ICONS[item.key];const [sx,sy]=item.start,[cx,cy,rot,scale]=item.chaos;const pop=clamp(frame,[110+i*16,175+i*16],[0,1]);const x=organize?interpolate(organize,[0,1],[cx,item.end[0]]):interpolate(explode,[0,1],[sx,cx]);const y=organize?interpolate(organize,[0,1],[cy,item.end[1]]):interpolate(explode,[0,1],[sy,cy]);return <div key={item.key} style={{position:'absolute',left:x,top:y,zIndex:Math.round(scale*10),opacity:pop*(1-dim),transform:`translate(-50%,-50%) rotate(${rot*(explode-organize)}deg) scale(${interpolate(organize,[0,1],[interpolate(explode,[0,1],[1,scale]),.78])})`,filter:`drop-shadow(0 24px 28px #0009)`}}><FabricIconCard {...icon}/></div>})}
   {explode>.25&&['Python','SQL','PySpark','R'].map((label,i)=><Owned key={label} label={label} color={theme.neutral} style={{position:'absolute',left:[118,1710,280,1570][i],top:[500,670,900,210][i],opacity:clamp(frame,[175+i*12,220+i*12,300,325],[0,1,1,0]),transform:`rotate(${[-5,5,3,-4][i]}deg)`}}/>)}
   <Workspace kind="Governance" opacity={workspaces}/><Workspace kind="Engineering" opacity={workspaces}/>
   {workspaces>.1&&<div style={{position:'absolute',left:1165,top:530,color:'#9fcfff',fontSize:13,letterSpacing:1}}>FABRIC OBJECTS · BUILD · VALIDATE</div>}
   <svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:contract}}><path d="M 870 650 C 900 650 905 600 935 600" stroke={theme.governance} strokeWidth="3" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-contract}/><path d="M 1050 700 C 1020 700 1015 675 985 675" stroke={theme.engineering} strokeWidth="3" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-active}/></svg>
   <div style={{position:'absolute',left:841,top:545,opacity:contract,transform:`scale(${.72+.28*contract})`,zIndex:20}}><DataContract active={active>.7}/></div>
   <div style={{position:'absolute',left:910,top:735,opacity:active,zIndex:21}}><StatusBadge label="CONTRACT ACTIVE"/></div>
  </div>
  <div style={{position:'absolute',inset:0,display:'grid',placeItems:'center',opacity:question,background:`rgba(4,9,18,${dim*.78})`,zIndex:50}}><div style={{fontSize:interpolate(question,[0,1],[72,142]),fontWeight:790,letterSpacing:-6,color:theme.text,transform:`scale(${.72+.28*question})`,textShadow:'0 20px 80px #000'}}>Where do I start?</div></div>
  <div style={{position:'absolute',inset:0,display:'grid',placeItems:'center',opacity:logoReveal,zIndex:51,transform:`scale(${.82+.18*logoReveal})`}}><div style={{textAlign:'center'}}><div style={{fontSize:120,fontWeight:800,letterSpacing:-7}}>Fabric<span style={{color:theme.production}}>Ops</span></div><div style={{marginTop:12,color:'#a8b8cb',fontSize:22,letterSpacing:4}}>FABRIC OPERATIONS</div><div style={{width:360,height:2,margin:'30px auto 0',background:`linear-gradient(90deg,transparent,${theme.production},transparent)`,boxShadow:`0 0 24px ${theme.production}`}}/></div></div>
  <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',opacity:cta,zIndex:60}}>
   <div style={{fontSize:98,fontWeight:800,letterSpacing:-6}}>Fabric<span style={{color:theme.production}}>Ops</span></div><div style={{marginTop:19,color:theme.muted,fontSize:19}}>Lightweight. &nbsp; Self-contained. &nbsp; <span style={{color:'#dce8f5'}}>Built for Microsoft Fabric.</span></div>
   <div style={{display:'flex',gap:22,marginTop:58}}>{['How FabricOps works','Guided demo'].map((label,i)=>{const emphasis=i===0?clamp(frame,[812,830,850,864],[0,1,1,0]):clamp(frame,[852,870,890,899],[0,1,1,0]);return <div key={label} style={{padding:'17px 27px',borderRadius:99,border:`1px solid ${i?theme.production:'#71859f'}aa`,background:i?`${theme.production}13`:'#101d30',color:i?theme.production:'#e1e9f3',fontSize:18,transform:`scale(${1+emphasis*.13}) translateZ(${emphasis*20}px)`,boxShadow:`0 ${14+emphasis*8}px ${34+emphasis*22}px #0008,0 0 ${emphasis*28}px ${i?theme.production:'#7bb8ff'}55`}}>{label}&nbsp; →</div>})}</div>
  </div>
 </div>;
};
