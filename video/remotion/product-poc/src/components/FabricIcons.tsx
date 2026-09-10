import type {CSSProperties, ComponentType, SVGProps} from 'react';
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

type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

type FabricIconCardProps = {
  icon: FabricIconComponent;
  label: string;
  style?: CSSProperties;
};

export const SELECTED_FABRIC_ICONS = {
  fabric: {icon: Fabric48Color, label: 'Microsoft Fabric'},
  notebook: {icon: Notebook48Item, label: 'Notebook'},
  lakehouse: {icon: Lakehouse48Item, label: 'Lakehouse'},
  warehouse: {icon: DataWarehouse48Item, label: 'Warehouse'},
  environment: {icon: Environment48Item, label: 'Environment'},
  dataPipeline: {icon: Pipeline48Item, label: 'Data Pipeline'},
  dataflowGen2: {icon: DataflowGen248Item, label: 'Dataflow Gen2'},
} as const;

export const FabricIconCard = ({icon: Icon, label, style}: FabricIconCardProps) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 10,
      minWidth: 112,
      ...style,
    }}
  >
    <Icon width={52} height={52} aria-hidden="true" />
    <div
      style={{
        color: theme.text,
        fontSize: 14,
        lineHeight: 1.2,
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </div>
  </div>
);
