import type {ComponentType, SVGProps} from 'react';
import * as FabricIconLibrary from '@fabric-msft/svg-icons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

const icons = FabricIconLibrary as unknown as Record<string, FabricIconComponent | undefined>;

const DEFAULT_ICON_SCALE = 1.34;

const artifactDefinitions = [
  {names: ['Notebook48Item'], label: 'Notebook', x: 45, y: 28, scale: 1.42},
  {names: ['Lakehouse48Item'], label: 'Lakehouse', x: 363, y: 28, scale: DEFAULT_ICON_SCALE},
  {names: ['DataWarehouse48Item', 'DataWarehouse48Color'], label: 'Warehouse', x: 681, y: 28, scale: 1.4},
  {names: ['Environment48Item'], label: 'Environment', x: 999, y: 28, scale: 1.45},
  {names: ['Pipeline48Item', 'DataFactory48Color'], label: 'Data Pipeline', x: 1317, y: 28, scale: 1.38},
  {names: ['DataflowGen248Item'], label: 'Dataflow Gen2', x: 1635, y: 28, scale: 1.42},
  {names: ['DataEngineering48Color'], label: 'Data Engineering', x: 45, y: 270, scale: 1.28},
  {names: ['DataScience48Color'], label: 'Data Science', x: 45, y: 480, scale: 1.3},
  {names: ['Databases48Color', 'SQLDatabase48Item', 'SqlDatabase48Item'], label: 'SQL Database', x: 45, y: 690, scale: 1.3},
  {names: ['Eventstream48Item'], label: 'Eventstream', x: 1635, y: 270, scale: 1.44},
  {names: ['Eventhouse48Item', 'KQLDatabase48Item'], label: 'Eventhouse', x: 1635, y: 480, scale: 1.42},
  {names: ['SemanticModel48Item'], label: 'Semantic Model', x: 1635, y: 690, scale: 1.42},
  {names: ['Report48Item'], label: 'Report', x: 45, y: 868, scale: 1.42},
  {names: ['Dashboard48Item'], label: 'Dashboard', x: 363, y: 868, scale: 1.44},
  {names: ['MirroredDatabase48Item'], label: 'Mirrored Database', x: 681, y: 868, scale: 1.42},
  {names: ['MLModel48Item', 'MlModel48Item'], label: 'ML Model', x: 999, y: 868, scale: 1.45},
  {names: ['OneLake48Color', 'OneLake48Item'], label: 'OneLake', x: 1317, y: 868, scale: 1.28},
  {names: ['GraphIntelligence48Color'], label: 'Graph Intelligence', x: 1635, y: 868, scale: 1.28},
] as const;

const humanizeIconName = (name: string) =>
  name
    .replace(/48(Item|Color)$/, '')
    .replace(/Gen2/g, ' Gen2')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .trim();

const fallbackIconNames = Object.keys(icons).filter(
  (name) =>
    /48(Item|Color)$/.test(name) &&
    !name.includes('Logo') &&
    !name.includes('Status') &&
    !name.startsWith('Fabric')
);

const usedIconNames = new Set<string>();

export const OPENING_ARTIFACTS = artifactDefinitions.map(({names, label, x, y, scale}) => {
  const preferredName = names.find((name) => icons[name] && !usedIconNames.has(name));
  const resolvedName = preferredName ?? fallbackIconNames.find((name) => !usedIconNames.has(name));

  if (!resolvedName || !icons[resolvedName]) {
    throw new Error('Unable to resolve 18 distinct Fabric icons for the Remotion opening scene.');
  }

  usedIconNames.add(resolvedName);
  return {
    icon: icons[resolvedName] as FabricIconComponent,
    label: preferredName ? label : humanizeIconName(resolvedName),
    x,
    y,
    scale,
  };
});

export const Artifact = ({icon: Icon, label, scale = DEFAULT_ICON_SCALE}: {icon: FabricIconComponent; label: string; scale?: number}) => {
  const {sizes, text} = VIDEO_CONFIG;

  return (
    <div
      style={{
        width: sizes.openingArtifactWidth,
        height: sizes.openingArtifactHeight,
        boxSizing: 'border-box',
        borderRadius: 30,
        padding: '8px 12px 9px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        background: 'linear-gradient(180deg, #102746f2 0%, #0c1d35f2 100%)',
        border: '1px solid #3a8ee866',
        boxShadow: '0 18px 38px #0008, inset 0 1px #ffffff12, 0 0 28px #1479cf16',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: sizes.openingArtifactIcon,
          height: sizes.openingArtifactIcon,
          flex: '0 0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'visible',
        }}
      >
        <Icon
          aria-hidden="true"
          style={{
            display: 'block',
            width: `${sizes.openingArtifactIcon}px`,
            height: `${sizes.openingArtifactIcon}px`,
            minWidth: `${sizes.openingArtifactIcon}px`,
            minHeight: `${sizes.openingArtifactIcon}px`,
            maxWidth: 'none',
            maxHeight: 'none',
            flex: '0 0 auto',
            transform: `scale(${scale})`,
            transformOrigin: 'center center',
          }}
        />
      </div>
      <div
        style={{
          width: '100%',
          minHeight: 26,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: text.artifactLabel - 2,
          lineHeight: 1.05,
          fontWeight: 760,
          color: theme.text,
          textAlign: 'center',
          whiteSpace: 'normal',
        }}
      >
        {label}
      </div>
    </div>
  );
};
