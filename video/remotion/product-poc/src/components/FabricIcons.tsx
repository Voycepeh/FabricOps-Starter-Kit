import type {ComponentType, SVGProps} from 'react';
import {
  DataWarehouse48Item,
  DataflowGen248Item,
  Environment48Item,
  Lakehouse48Item,
  Notebook48Item,
  Pipeline48Item,
} from '@fabric-msft/svg-icons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

export const OPENING_ARTIFACTS: Array<{icon: FabricIconComponent; label: string; x: number; y: number}> = [
  {icon: Notebook48Item, label: 'Notebook', x: 140, y: 190},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 850, y: 45},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 1560, y: 180},
  {icon: Environment48Item, label: 'Environment', x: 140, y: 720},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 850, y: 875},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1560, y: 705},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: VIDEO_CONFIG.sizes.openingArtifactFootprint, height: 155, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12}}>
    <div style={{width: VIDEO_CONFIG.sizes.openingArtifactIcon, height: VIDEO_CONFIG.sizes.openingArtifactIcon, display: 'grid', placeItems: 'center', filter: 'drop-shadow(0 18px 22px #0009)'}}>
      <Icon width={VIDEO_CONFIG.sizes.openingArtifactIcon} height={VIDEO_CONFIG.sizes.openingArtifactIcon} aria-hidden="true" />
    </div>
    <div style={{fontSize: VIDEO_CONFIG.text.artifactLabel, lineHeight: 1, fontWeight: 760, color: theme.text, textAlign: 'center', whiteSpace: 'nowrap', textShadow: '0 4px 14px #000'}}>{label}</div>
  </div>
);
