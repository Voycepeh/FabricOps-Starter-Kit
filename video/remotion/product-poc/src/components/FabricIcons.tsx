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

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

export const FABRIC_ICON = Fabric48Color;

export const OPENING_ARTIFACTS: Array<{icon: FabricIconComponent; label: string; x: number; y: number}> = [
  {icon: Notebook48Item, label: 'Notebook', x: 300, y: 170},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 870, y: 90},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 1440, y: 170},
  {icon: Environment48Item, label: 'Environment', x: 300, y: 720},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 870, y: 820},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1440, y: 720},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: 180, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
    <div style={{width: 104, height: 104, borderRadius: 28, display: 'grid', placeItems: 'center', background: '#142641', border: '1px solid #7da4cf42', boxShadow: '0 18px 35px #0008'}}>
      <Icon width={72} height={72} aria-hidden="true" />
    </div>
    <div style={{fontSize: 24, lineHeight: 1, fontWeight: 650, color: theme.text, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);
