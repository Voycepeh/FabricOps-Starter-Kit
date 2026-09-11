import type {ComponentType, SVGProps} from 'react';
import * as FabricIconLibrary from '@fabric-msft/svg-icons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';

export type FabricIconComponent = ComponentType<SVGProps<SVGSVGElement>>;

const icons = FabricIconLibrary as unknown as Record<string, FabricIconComponent | undefined>;

const preferredArtifacts = [
  {names: ['Notebook48Item'], label: 'Notebook', scale: 2.2},
  {names: ['Lakehouse48Item'], label: 'Lakehouse', scale: 2.2},
  {names: ['DataWarehouse48Item', 'DataWarehouse48Color'], label: 'Warehouse', scale: 2.2},
  {names: ['Environment48Item'], label: 'Environment', scale: 2.2},
  {names: ['Pipeline48Item', 'DataFactory48Color'], label: 'Data Pipeline', scale: 2.2},
  {names: ['DataflowGen248Item'], label: 'Dataflow Gen2', scale: 2.2},
  {names: ['DataEngineering48Color'], label: 'Data Engineering', scale: 2.3},
  {names: ['DataScience48Color'], label: 'Data Science', scale: 2.3},
  {names: ['Databases48Color', 'SQLDatabase48Item', 'SqlDatabase48Item'], label: 'SQL Database', scale: 2.2},
  {names: ['Eventstream48Item'], label: 'Eventstream', scale: 2.2},
  {names: ['Eventhouse48Item', 'KQLDatabase48Item'], label: 'Eventhouse', scale: 2.2},
  {names: ['SemanticModel48Item'], label: 'Semantic Model', scale: 2.25},
  {names: ['Report48Item'], label: 'Report', scale: 2.2},
  {names: ['Dashboard48Item'], label: 'Dashboard', scale: 2.2},
  {names: ['MirroredDatabase48Item'], label: 'Mirrored Database', scale: 2.2},
  {names: ['MLModel48Item', 'MlModel48Item'], label: 'ML Model', scale: 2.2},
  {names: ['OneLake48Color', 'OneLake48Item'], label: 'OneLake', scale: 2.25},
  {names: ['GraphIntelligence48Color'], label: 'Graph Intelligence', scale: 2.25},
] as const;

const artifactPositions = [
  {x: 45, y: 28},
  {x: 363, y: 28},
  {x: 681, y: 28},
  {x: 999, y: 28},
  {x: 1317, y: 28},
  {x: 1635, y: 28},
  {x: 45, y: 260},
  {x: 45, y: 464},
  {x: 45, y: 668},
  {x: 1635, y: 260},
  {x: 1635, y: 464},
  {x: 1635, y: 668},
  {x: 45, y: 868},
  {x: 363, y: 868},
  {x: 681, y: 868},
  {x: 999, y: 868},
  {x: 1317, y: 868},
  {x: 1635, y: 868},
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

const artifactTypes = preferredArtifacts.map(({names, label, scale}) => {
  const preferredName = names.find((name) => icons[name] && !usedIconNames.has(name));
  const resolvedName = preferredName ?? fallbackIconNames.find((name) => !usedIconNames.has(name));

  if (!resolvedName || !icons[resolvedName]) {
    throw new Error('Unable to resolve 18 distinct Fabric icons for the Remotion opening scene.');
  }

  usedIconNames.add(resolvedName);
  return {
    icon: icons[resolvedName] as FabricIconComponent,
    label: preferredName ? label : humanizeIconName(resolvedName),
    iconScale: scale,
  };
});

export const OPENING_ARTIFACTS = artifactPositions.map((position, index) => ({
  ...artifactTypes[index],
  ...position,
}));

export const Artifact = ({icon: Icon, label, iconScale}: {icon: FabricIconComponent; label: string; iconScale: number}) => {
  const {sizes, text} = VIDEO_CONFIG;

  return (
    <div
      style={{
        width: sizes.openingArtifactWidth,
        height: sizes.openingArtifactHeight,
        boxSizing: 'border-box',
        borderRadius: 30,
        padding: '10px 14px 12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
        background: 'linear-gradient(180deg, #102746f2 0%, #0c1d35f2 100%)',
        border: '1px solid #3a8ee866',
        boxShadow: '0 18px 38px #0008, inset 0 1px #ffffff12, 0 0 28px #1479cf16',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: 112,
          height: 112,
          flex: '0 0 112px',
          display: 'grid',
          placeItems: 'center',
          overflow: 'visible',
        }}
      >
        <div
          style={{
            width: 48,
            height: 48,
            display: 'grid',
            placeItems: 'center',
            transform: `scale(${iconScale})`,
            transformOrigin: '50% 50%',
          }}
        >
          <Icon aria-hidden="true" width={48} height={48} />
        </div>
      </div>
      <div
        style={{
          width: '100%',
          minHeight: 30,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: text.artifactLabel,
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
