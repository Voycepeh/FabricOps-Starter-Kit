import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {LongFormStory} from './scenes/LongFormStory';
import {font, theme} from './theme';

export const FabricOpsHero = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: theme.background, fontFamily: font, overflow: 'hidden'}}>
    <div style={{position:'absolute',inset:-180,background:`radial-gradient(circle at ${34+interpolate(frame,[0,900],[0,22])}% 35%,#17406b70,transparent 34%),radial-gradient(circle at 68% 70%,#55287a48,transparent 32%),linear-gradient(145deg,#050c18,#09162a 58%,#07101d)`}}/>
    <div style={{position:'absolute',inset:0,opacity:.11,backgroundImage:'linear-gradient(#91a7c310 1px,transparent 1px),linear-gradient(90deg,#91a7c310 1px,transparent 1px)',backgroundSize:'72px 72px',transform:`translate(${frame%72}px,${frame%72}px)`}}/>
    <LongFormStory/>
    <div style={{position:'absolute',left:48,bottom:34,color:'#607089',fontSize:14,letterSpacing:2.2}}>FABRICOPS STARTER KIT</div>
  </AbsoluteFill>;
};
