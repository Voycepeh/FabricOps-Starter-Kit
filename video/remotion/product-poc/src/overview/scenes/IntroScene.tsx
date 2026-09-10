import type {ComponentType, SVGProps} from 'react';
import {
  DataWarehouse48Item,
  DataflowGen248Item,
  Environment48Item,
  Fabric48Color,
  Lakehouse48Item,
  Notebook48Item,
  Pipeline48Item,
} from '@fabric-msft/svg-icons';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../../theme';
import {Enter, FabricOpsLogo, NotebookNode, Rail, TableNode, clamp} from '../components/OverviewPrimitives';

type Icon = ComponentType<SVGProps<SVGSVGElement>>;
const assets: Array<{Icon: Icon; x: number; y: number; size: number; depth: number}> = [
  {Icon: Fabric48Color, x: 130, y: 120, size: 210, depth: 1},
  {Icon: Notebook48Item, x: 505, y: 90, size: 180, depth: .82},
  {Icon: Lakehouse48Item, x: 910, y: 105, size: 205, depth: .96},
  {Icon: DataWarehouse48Item, x: 1390, y: 130, size: 185, depth: .78},
  {Icon: Pipeline48Item, x: 235, y: 545, size: 195, depth: .88},
  {Icon: Environment48Item, x: 735, y: 600, size: 165, depth: .7},
  {Icon: DataflowGen248Item, x: 1250, y: 565, size: 210, depth: .9},
];

export const IntroScene = () => {
  const frame = useCurrentFrame();
  const recede = clamp(frame, 690, 850);
  const logo = clamp(frame, 760, 930);
  const path = clamp(frame, 930, 1480);
  const nodes = [['00', 'Environment'], ['01', 'Governance'], ['02', 'Engineering'], ['03', 'Data Contract'], ['04', 'Validate'], ['99', 'Explore']];
  return <div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', inset: 0, opacity: 1 - recede, transform: `perspective(1200px) translateZ(${-recede * 300}px) scale(${1 - recede * .16})`}}>
      {assets.map(({Icon, x, y, size, depth}, index) => <Enter key={index} delay={index * 12} style={{position: 'absolute', left: x, top: y, filter: `drop-shadow(0 28px 38px #0009)`, opacity: .65 + depth * .35, transform: `scale(${depth})`}}><Icon width={size} height={size} /></Enter>)}
      <Enter delay={84} style={{position: 'absolute', left: 1530, top: 600, transform: 'rotate(-4deg)'}}><TableNode label="" style={{width: 230, height: 190}} /></Enter>
    </div>
    <FabricOpsLogo size={112} style={{position: 'absolute', left: '50%', top: 190, transform: `translateX(-50%) scale(${.8 + .2 * logo})`, opacity: logo}} />
    <div style={{position: 'absolute', left: 130, right: 130, top: 565, display: 'flex', justifyContent: 'space-between', opacity: path}}>{nodes.map(([number, label], index) => <NotebookNode key={number} number={number} label={label} color={index === 1 ? theme.governance : index === 5 ? theme.consumer : index === 4 ? theme.production : theme.engineering} style={{width: 240, transform: `translateY(${interpolate(path, [0, 1], [55, 0])}px)`, opacity: clamp(path, index / 7, (index + 2) / 7)}} />)}</div>
    <Rail progress={path} style={{position: 'absolute', left: 250, right: 250, top: 790}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 850, textAlign: 'center', fontSize: 34, fontWeight: 650, opacity: path}}>An opinionated operating path through Microsoft Fabric</div>
  </div>;
};
