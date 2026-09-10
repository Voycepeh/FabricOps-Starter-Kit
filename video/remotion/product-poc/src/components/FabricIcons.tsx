import type {ComponentType, SVGProps} from 'react';
import {DataWarehouse48Item, DataflowGen248Item, Environment48Item, Lakehouse48Item, Notebook48Item, Pipeline48Item} from '@fabric-msft/svg-icons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

const artifactTypes = [
  {icon: Notebook48Item, label: 'Notebook'},
  {icon: Lakehouse48Item, label: 'Lakehouse'},
  {icon: DataWarehouse48Item, label: 'Warehouse'},
  {icon: Environment48Item, label: 'Environment'},
  {icon: Pipeline48Item, label: 'Data Pipeline'},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2'},
] as const;

const artifactPositions = [
  {x: 80, y: 35}, {x: 1620, y: 35}, {x: 80, y: 875}, {x: 1620, y: 875}, {x: 80, y: 455}, {x: 1620, y: 455},
  {x: 390, y: 35}, {x: 1310, y: 35}, {x: 390, y: 875}, {x: 1310, y: 875}, {x: 80, y: 260}, {x: 1620, y: 260},
  {x: 700, y: 35}, {x: 1000, y: 35}, {x: 700, y: 875}, {x: 1000, y: 875}, {x: 80, y: 650}, {x: 1620, y: 650},
] as const;

export const OPENING_ARTIFACTS = artifactPositions.map((position, index) => ({...artifactTypes[index % artifactTypes.length], ...position}));

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => {
  const {sizes, text} = VIDEO_CONFIG;
  return <div style={{width: sizes.openingArtifactWidth, height: sizes.openingArtifactHeight, boxSizing: 'border-box', borderRadius: 32, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, background: '#101f37d9', border: '1px solid #8aa6c84d', boxShadow: '0 18px 38px #0008, inset 0 1px #ffffff10'}}>
    <Icon width={sizes.openingArtifactIcon} height={sizes.openingArtifactIcon} aria-hidden="true" />
    <div style={{fontSize: text.artifactLabel, lineHeight: 1, fontWeight: 750, color: theme.text, textAlign: 'center', whiteSpace: 'nowrap'}}>{label}</div>
  </div>;
};
