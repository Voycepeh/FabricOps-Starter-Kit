import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {IntroScene} from './overview/scenes/IntroScene';
import {WhyFabricOpsScene} from './overview/scenes/WhyFabricOpsScene';
import {EngineeringChoicesScene} from './overview/scenes/EngineeringChoicesScene';
import {ConnectedWorkflowScene} from './overview/scenes/ConnectedWorkflowScene';
import {GovernanceEngineeringScene} from './overview/scenes/GovernanceEngineeringScene';
import {ProductionScene} from './overview/scenes/ProductionScene';
import {ContinueScene} from './overview/scenes/ContinueScene';
import {OVERVIEW_SCENES, OVERVIEW_DURATION_IN_FRAMES} from './overview/OverviewTimeline';
import {font, theme} from './theme';

export {OVERVIEW_DURATION_IN_FRAMES};
export const OVERVIEW_NARRATION_PATH = 'audio/fabricops-overview-narration.mp3';
const scenes = [IntroScene, WhyFabricOpsScene, EngineeringChoicesScene, ConnectedWorkflowScene, GovernanceEngineeringScene, ProductionScene, ContinueScene];

export const FabricOpsOverview = ({narration=false}:{narration?:boolean}) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, OVERVIEW_DURATION_IN_FRAMES], [0, 180]);
  return <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
    <div style={{position:'absolute', inset:-220, background:`radial-gradient(circle at ${34 + drift / 30}% 38%,#15365b88,transparent 34%),radial-gradient(circle at 76% 72%,#4a237150,transparent 31%),linear-gradient(145deg,#07101f,#091427 62%,#07111d)`}} />
    <div style={{position:'absolute',inset:0,opacity:.1,backgroundImage:'linear-gradient(#91a7c30c 1px,transparent 1px),linear-gradient(90deg,#91a7c30c 1px,transparent 1px)',backgroundSize:'80px 80px',transform:`translateX(${drift % 80}px)`}} />
    {OVERVIEW_SCENES.map((scene, index) => { const Component=scenes[index]; return <Sequence key={scene.name} from={scene.from} durationInFrames={scene.duration}><Component /></Sequence>; })}
    {narration ? <Audio src={staticFile(OVERVIEW_NARRATION_PATH)} /> : null}
  </AbsoluteFill>;
};
