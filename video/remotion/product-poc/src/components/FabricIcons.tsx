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
  {icon: Notebook48Item, label: 'Notebook', x: 175, y: 170},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 455, y: 118},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 770, y: 145},
  {icon: Environment48Item, label: 'Environment', x: 1080, y: 115},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 1395, y: 170},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1520, y: 410},
  {icon: Notebook48Item, label: 'Notebook', x: 1320, y: 680},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 1015, y: 745},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 685, y: 735},
  {icon: Environment48Item, label: 'Environment', x: 350, y: 685},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 160, y: 445},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 565, y: 410},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: 180, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
    <div style={{width: 104, height: 104, borderRadius: 28, display: 'grid', placeItems: 'center', background: '#142641', border: '1px solid #7da4cf42', boxShadow: '0 18px 35px #0008'}}>
      <Icon width={72} height={72} aria-hidden="true" />
    </div>
    <div style={{fontSize: 24, lineHeight: 1, fontWeight: 650, color: theme.text, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);
