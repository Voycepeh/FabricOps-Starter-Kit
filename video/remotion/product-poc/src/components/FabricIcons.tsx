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
  {icon: Notebook48Item, label: 'Notebook', x: 230, y: 190},
  {icon: Lakehouse48Item, label: 'Lakehouse', x: 855, y: 75},
  {icon: DataWarehouse48Item, label: 'Warehouse', x: 1480, y: 190},
  {icon: Environment48Item, label: 'Environment', x: 230, y: 700},
  {icon: Pipeline48Item, label: 'Data Pipeline', x: 855, y: 820},
  {icon: DataflowGen248Item, label: 'Dataflow Gen2', x: 1480, y: 700},
];

export const Artifact = ({icon: Icon, label}: {icon: FabricIconComponent; label: string}) => (
  <div style={{width: 210, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16}}>
    <div style={{width: 136, height: 136, borderRadius: 34, display: 'grid', placeItems: 'center', background: '#142641', border: '2px solid #7da4cf55', boxShadow: '0 18px 35px #0008'}}>
      <Icon width={96} height={96} aria-hidden="true" />
    </div>
    <div style={{fontSize: 29, lineHeight: 1, fontWeight: 700, color: theme.text, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);
