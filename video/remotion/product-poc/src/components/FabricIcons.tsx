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
  {icon: Notebook48Item, label: 'Notebook', x: 180, y: 165},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 805, y: 35},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 1430, y: 165},
  {icon: Environment48Item, label: 'Environment', x: 180, y: 765},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 805, y: 895},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1430, y: 765},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: VIDEO_CONFIG.sizes.openingArtifactCardWidth, height: VIDEO_CONFIG.sizes.openingArtifactCardHeight, boxSizing: 'border-box', padding: '0 30px', borderRadius: 34, display: 'flex', alignItems: 'center', justifyContent: 'flex-start', gap: 22, background: '#142641', border: '2px solid #7da4cf55', boxShadow: '0 18px 35px #0008'}}>
    <div style={{width: VIDEO_CONFIG.sizes.openingArtifactIcon, height: VIDEO_CONFIG.sizes.openingArtifactIcon, flex: '0 0 auto', display: 'grid', placeItems: 'center'}}>
      <Icon width={VIDEO_CONFIG.sizes.openingArtifactIcon} height={VIDEO_CONFIG.sizes.openingArtifactIcon} aria-hidden="true" />
    </div>
    <div style={{flex: 1, fontSize: VIDEO_CONFIG.text.artifactLabel, lineHeight: 1.1, fontWeight: 760, color: theme.text, textAlign: 'center'}}>{label}</div>
  </div>
);
