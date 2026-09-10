import type {ReactNode} from 'react';
import {AbsoluteFill,Easing,Sequence,interpolate,spring,useCurrentFrame,useVideoConfig} from 'remotion';
import {CodeStory} from '../components/CodeStory';
import {DataContract,StatusBadge} from '../components/Primitives';
import {ProductStory} from './ProductStory';
import {theme} from '../theme';

const TRANSITION_FRAMES=8;
const fade=(frame:number,duration:number)=>interpolate(frame,[0,10,duration-10,duration],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const Scene=({from,duration,children}:{from:number;duration:number;children:ReactNode})=><Sequence from={from} durationInFrames={duration}><SceneSurface duration={duration}>{children}</SceneSurface></Sequence>;
const SceneSurface=({duration,children}:{duration:number;children:ReactNode})=>{const frame=useCurrentFrame();return <AbsoluteFill style={{opacity:fade(frame,duration),background:'#07101ff8',zIndex:2}}>{children}</AbsoluteFill>;};
const next=(start:number,duration:number)=>start+duration-TRANSITION_FRAMES;

export const PRODUCT_STORY_FRAMES=900;
export const ENV_CONFIG_FRAMES=330;
export const GOVERNANCE_FRAMES=390;
export const PIPELINE_FRAMES=510;
export const OUTCOME_FRAMES=360;
export const CTA_FRAMES=240;
const productStory=0,envConfig=next(productStory,PRODUCT_STORY_FRAMES),governance=next(envConfig,ENV_CONFIG_FRAMES),pipeline=next(governance,GOVERNANCE_FRAMES),outcome=next(pipeline,PIPELINE_FRAMES),cta=next(outcome,OUTCOME_FRAMES);
export const TIMELINE={productStory,envConfig,governance,pipeline,outcome,cta} as const;
export const LONG_FORM_STORY_FRAMES=cta+CTA_FRAMES;

const EnvConfig=()=> <CodeStory duration={ENV_CONFIG_FRAMES} eyebrow="00 · OPERATING FOUNDATION" title="Set once. Reuse everywhere." accent={theme.neutral} lines={[
 {code:'ENVIRONMENT = "Development"',label:'Choose the operating environment.'},
 {code:'WORKSPACE = config.workspace(environment)',label:'Resolve the Fabric workspace.'},
 {code:'LAKEHOUSE = config.lakehouse("metadata")',label:'Define governed object targets.'},
 {code:'PATHS = config.paths(environment)',label:'Reuse the workflow across environments.'},
]}/>;
const Governance=()=> <CodeStory duration={GOVERNANCE_FRAMES} eyebrow="01 · GOVERNANCE" title="Intent becomes a Data Contract." accent={theme.governance} lines={[
 {code:'contract.schema("orders")',label:'Governance defines the expected schema.'},
 {code:'contract.freshness(max_hours=24)',label:'Freshness becomes explicit.'},
 {code:'contract.quality("not_null", "order_id")',label:'Quality expectations become executable.'},
 {code:'contract.sensitivity("customer_email")',label:'Sensitivity travels with the contract.'},
]}/>;
const Pipeline=()=> <CodeStory duration={PIPELINE_FRAMES} eyebrow="02 · PIPELINE" title="Normal ETL. Governed execution." accent={theme.engineering} lines={[
 {code:'orders = read_and_profile(source)',label:'Read and profile.'},
 {code:'orders = transform(orders)',label:'Transform the data.'},
 {code:'result = validate(orders, contract)',label:'Validate schema, freshness, quality, and Guardrails.'},
 {code:'write(orders, target, result)',label:'Write only after governed validation.'},
]}/>;
const Outcome=()=>{const frame=useCurrentFrame(),{fps}=useVideoConfig(),flow=interpolate(frame,[35,235],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});const states=[['00','Configure',theme.neutral],['01','Govern',theme.governance],['02','Engineer',theme.engineering]];return <AbsoluteFill><div style={{position:'absolute',left:210,right:210,top:240,display:'flex',alignItems:'center',justifyContent:'space-between'}}>{states.map(([n,label,color],i)=>{const p=spring({frame:frame-25-i*38,fps,config:{damping:20,stiffness:95}});return <div key={n} style={{position:'relative',width:300,height:190,border:`1px solid ${color}88`,borderRadius:24,background:`${color}16`,display:'grid',placeItems:'center',opacity:p,transform:`translateY(${(1-p)*28}px)`}}><div style={{textAlign:'center'}}><div style={{color,fontSize:42,fontWeight:820}}>{n}</div><div style={{color:'#e5edf7',fontSize:22,marginTop:12}}>{label}</div></div>{i<2&&<span style={{position:'absolute',right:-190,color:'#8193aa',fontSize:38}}>→</span>}</div>})}</div><div style={{position:'absolute',left:841,top:500,transform:`scale(${.8+flow*.2})`,opacity:flow}}><DataContract active={flow>.68}/></div><div style={{position:'absolute',left:350,right:350,bottom:155,display:'flex',justifyContent:'space-between'}}>{['VALIDATED','GOVERNED','REPEATABLE','PRODUCTION-READY'].map((x,i)=><div key={x} style={{color:i===3?theme.production:'#dbe6f3',fontSize:18,fontWeight:780,letterSpacing:1,opacity:interpolate(flow,[i*.18,Math.min(1,i*.18+.22)],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>{x}</div>)}</div><div style={{position:'absolute',left:895,top:700,opacity:interpolate(flow,[.72,1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><StatusBadge label="READY"/></div></AbsoluteFill>;};
const CTA=()=>{const frame=useCurrentFrame(),first=interpolate(frame,[35,65,100,125],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),second=interpolate(frame,[115,145,185,215],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});return <AbsoluteFill style={{display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column'}}><div style={{fontSize:102,fontWeight:820,color:'#f7f9fd'}}>Fabric<span style={{color:theme.production}}>Ops</span></div><div style={{fontSize:23,color:'#bdcada',marginTop:20}}>Lightweight. Self-contained. Built for Microsoft Fabric.</div><div style={{display:'flex',gap:32,marginTop:64}}>{[['How FabricOps works',first],['Guided Demo',second]].map(([label,p],i)=><div key={String(label)} style={{padding:'19px 34px',borderRadius:99,border:`1px solid ${i?theme.production:'#8298b3'}`,background:i?`${theme.production}14`:'#101d30',color:i?'#78efb8':'#f4f8fd',fontSize:21,fontWeight:750,transform:`scale(${1+Number(p)*.13})`,boxShadow:`0 0 ${Number(p)*34}px ${i?theme.production:'#68aaff'}55`}}>{label} →</div>)}</div></AbsoluteFill>;};

export const LongFormStory=()=> <AbsoluteFill>
 <Scene from={TIMELINE.productStory} duration={PRODUCT_STORY_FRAMES}><ProductStory openingOnly/></Scene>
 <Scene from={TIMELINE.envConfig} duration={ENV_CONFIG_FRAMES}><EnvConfig/></Scene>
 <Scene from={TIMELINE.governance} duration={GOVERNANCE_FRAMES}><Governance/></Scene>
 <Scene from={TIMELINE.pipeline} duration={PIPELINE_FRAMES}><Pipeline/></Scene>
 <Scene from={TIMELINE.outcome} duration={OUTCOME_FRAMES}><Outcome/></Scene>
 <Scene from={TIMELINE.cta} duration={CTA_FRAMES}><CTA/></Scene>
 </AbsoluteFill>;
