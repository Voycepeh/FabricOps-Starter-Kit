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
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

export const FABRIC_ICON = Fabric48Color;

export const OPENING_ARTIFACTS: Array<{icon: FabricIconComponent; label: string; x: number; y: number}> = [
  {icon: Notebook48Item, label: 'Notebook', x: 230, y: 190},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 855, y: 20},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 1480, y: 190},
  {icon: Environment48Item, label: 'Environment', x: 230, y: 700},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 855, y: 855},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1480, y: 700},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: VIDEO_CONFIG.sizes.openingArtifactCard + 70, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16}}>
    <div style={{width: VIDEO_CONFIG.sizes.openingArtifactCard, height: VIDEO_CONFIG.sizes.openingArtifactCard, borderRadius: 38, display: 'grid', placeItems: 'center', background: '#142641', border: '2px solid #7da4cf55', boxShadow: '0 18px 35px #0008'}}>
      <Icon width={VIDEO_CONFIG.sizes.openingArtifactIcon} height={VIDEO_CONFIG.sizes.openingArtifactIcon} aria-hidden="true" />
    </div>
    <div style={{fontSize: VIDEO_CONFIG.text.artifactLabel, lineHeight: 1, fontWeight: 700, color: theme.text, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);
