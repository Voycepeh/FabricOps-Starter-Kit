import {interpolate,useCurrentFrame} from 'remotion';
import {SELECTED_FABRIC_ICONS,FabricIconCard} from '../../components/FabricIcons';
import {theme} from '../../theme';
import {Enter,FabricOpsLogo,NotebookNode,Rail,clamp} from '../components/OverviewPrimitives';
const items=[...Object.values(SELECTED_FABRIC_ICONS),...Object.values(SELECTED_FABRIC_ICONS),...Object.values(SELECTED_FABRIC_ICONS).slice(0,4)];
export const IntroScene=()=>{const frame=useCurrentFrame();const recede=clamp(frame,690,850);const logo=clamp(frame,760,930);const path=clamp(frame,930,1480);const nodes=[['00','Environment'],['01','Governance'],['02','Engineering'],['03','Data Contract'],['04','Validate'],['99','Explore']];return <div style={{position:'absolute',inset:0}}>
 <div style={{position:'absolute',inset:70,display:'grid',gridTemplateColumns:'repeat(6,1fr)',gap:'30px 38px',opacity:1-recede,transform:`perspective(1200px) translateZ(${-recede*260}px) scale(${1-recede*.18})`}}>{items.map((item,i)=><Enter key={i} delay={i*8} style={{display:'grid',placeItems:'center',minHeight:210}}><FabricIconCard {...item} style={{transform:`scale(${1.45+(i%3)*.08})`}}/></Enter>)}</div>
 <FabricOpsLogo size={112} style={{position:'absolute',left:'50%',top:190,transform:`translateX(-50%) scale(${.8+.2*logo})`,opacity:logo}}/>
 <div style={{position:'absolute',left:130,right:130,top:565,display:'flex',justifyContent:'space-between',opacity:path}}>{nodes.map(([n,l],i)=><NotebookNode key={n} number={n} label={l} color={i===1?theme.governance:i===5?theme.consumer:i===4?theme.production:theme.engineering} style={{width:240,transform:`translateY(${interpolate(path,[0,1],[55,0])}px)`,opacity:clamp(path,i/7,(i+2)/7)}}/>)}</div>
 <Rail progress={path} style={{position:'absolute',left:250,right:250,top:790}}/><div style={{position:'absolute',left:0,right:0,top:850,textAlign:'center',fontSize:34,fontWeight:650,opacity:path}}>An opinionated operating path through Microsoft Fabric</div>
 </div>};
