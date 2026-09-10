import type {ReactNode} from 'react';
import {Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type Highlight = {x:number;y:number;width:number;height:number;label?:string};
type ProductCaptureFrameProps = {title:string;placeholder:string;mediaSrc?:string;mediaType?:'image'|'video';zoom?:number;panX?:number;panY?:number;highlight?:Highlight;accent?:string;children?:ReactNode};

export const ProductCaptureFrame=({title,placeholder,mediaSrc,mediaType='image',zoom=1,panX=0,panY=0,highlight,accent=theme.engineering,children}:ProductCaptureFrameProps)=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),enter=spring({frame,fps,config:{damping:24,stiffness:75}}),drift=interpolate(frame,[0,900],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),source=mediaSrc?staticFile(mediaSrc):null;
 return <div style={{position:'absolute',left:190,top:150,width:1540,height:780,borderRadius:28,overflow:'hidden',border:`1px solid ${accent}66`,background:'#091426',boxShadow:'0 45px 120px #000b',opacity:enter,transform:`translateY(${(1-enter)*50}px) scale(${.96+enter*.04})`}}>
  <div style={{height:54,display:'flex',alignItems:'center',gap:9,padding:'0 20px',background:'#101d31',borderBottom:'1px solid #ffffff12'}}><span style={{width:11,height:11,borderRadius:99,background:'#ff746c'}}/><span style={{width:11,height:11,borderRadius:99,background:'#f7c55c'}}/><span style={{width:11,height:11,borderRadius:99,background:'#55d38b'}}/><span style={{marginLeft:17,color:'#bac8da',fontSize:15}}>{title}</span></div>
  <div style={{position:'absolute',left:0,right:0,top:54,bottom:0,overflow:'hidden'}}>
   {source?(mediaType==='video'?<OffthreadVideo src={source} muted style={{width:'100%',height:'100%',objectFit:'cover',transform:`translate(${panX*drift}px,${panY*drift}px) scale(${zoom})`}}/>:<Img src={source} style={{width:'100%',height:'100%',objectFit:'cover',transform:`translate(${panX*drift}px,${panY*drift}px) scale(${zoom})`}}/>):<div style={{position:'absolute',inset:0,display:'grid',placeItems:'center',background:'radial-gradient(circle at 50% 42%,#183253,#0a1526 62%)'}}><div style={{width:860,padding:'48px 56px',border:`1px dashed ${accent}99`,borderRadius:22,textAlign:'center',color:'#d9e5f3'}}><div style={{fontSize:14,letterSpacing:2,color:accent,marginBottom:18}}>REAL MICROSOFT FABRIC CAPTURE SLOT</div><div style={{fontSize:27,fontWeight:700,lineHeight:1.35}}>{placeholder}</div><div style={{fontSize:15,color:theme.muted,marginTop:18}}>Replace with image or screen recording using the mediaSrc prop.</div></div></div>}
   {highlight&&<div style={{position:'absolute',left:highlight.x,top:highlight.y,width:highlight.width,height:highlight.height,border:`3px solid ${accent}`,borderRadius:12,boxShadow:`0 0 0 9999px #03071199,0 0 30px ${accent}77`,transform:`scale(${.98+Math.sin(frame/10)*.02})`}}>{highlight.label&&<span style={{position:'absolute',left:0,bottom:-36,padding:'7px 11px',borderRadius:8,background:accent,color:'#07101f',fontSize:13,fontWeight:800}}>{highlight.label}</span>}</div>}{children}
  </div>
 </div>;
};
export const NotebookCapture=ProductCaptureFrame;
export const WidgetCapture=ProductCaptureFrame;
export const CodeCapture=ProductCaptureFrame;
