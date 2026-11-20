import {
  DataAgent48Item,
  DataWarehouse64Item,
  Lakehouse64Item,
  Notebook48Item,
} from '@fabric-msft/svg-icons';
import {Audio} from '@remotion/media';
import type {ReactNode} from 'react';
import {AbsoluteFill, Easing, interpolate, interpolateColors, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {WORKSPACE_ARCHITECTURE_DURATION_SECONDS} from '../videoConfig';

const palette = {
  blue: '#2563EB',
  blueDeep: '#1D4ED8',
  purple: '#7C3AED',
  purpleDeep: '#6D28D9',
  ink: '#19243A',
  muted: '#52627A',
  canvas: '#FFFFFF',
  surface: '#F6F8FF',
  border: '#DDE3F3',
} as const;

const FONT = 'Segoe UI, Arial, sans-serif';

const fade = (frame: number, fps: number, startSeconds: number, durationSeconds = 0.7) =>
  interpolate(
    frame,
    [startSeconds * fps, (startSeconds + durationSeconds) * fps],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    },
  );

const panelReveal = (frame: number, fps: number, startSeconds: number) =>
  spring({
    frame: frame - startSeconds * fps,
    fps,
    config: {damping: 200, stiffness: 120},
  });

type WorkspacePanelProps = {
  readonly title: string;
  readonly color: string;
  readonly position: {left: number; top: number; width: number; height: number};
  readonly opacity: number;
  readonly translateY: number;
  readonly children: ReactNode;
};

const WorkspacePanel = ({title, color, position, opacity, translateY, children}: WorkspacePanelProps) => (
  <section
    aria-label={title}
    style={{
      position: 'absolute',
      ...position,
      boxSizing: 'border-box',
      border: `3px solid ${color}`,
      borderRadius: 10,
      background: palette.canvas,
      opacity,
      translate: `0 ${translateY}px`,
      overflow: 'hidden',
    }}
  >
    <div
      style={{
        height: 62,
        display: 'flex',
        alignItems: 'center',
        padding: '0 28px',
        boxSizing: 'border-box',
        borderBottom: `2px solid ${color}33`,
        background: `${color}0D`,
        color,
        fontSize: 38,
        lineHeight: 1,
        fontWeight: 760,
      }}
    >
      {title}
    </div>
    {children}
  </section>
);

type StageCardProps = {
  readonly title: string;
  readonly subtitle: string;
  readonly icon: ReactNode;
  readonly opacity: number;
  readonly translateX: number;
  readonly flash: number;
  readonly accent?: boolean;
};

const StageCard = ({title, subtitle, icon, opacity, translateX, flash, accent = false}: StageCardProps) => (
  <div
    style={{
      flex: 1,
      minWidth: 0,
      height: 184,
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 8,
      padding: 16,
      border: `2px solid ${interpolateColors(flash, [0, 1], [accent ? palette.blueDeep : palette.border, palette.blue])}`,
      borderRadius: 10,
      background: interpolateColors(flash, [0, 1], [accent ? '#EFF6FF' : palette.surface, '#DBEAFE']),
      opacity,
      translate: `${translateX}px 0`,
    }}
  >
    <div aria-hidden="true" style={{width: 60, height: 60}}>{icon}</div>
    <div style={{fontSize: 25, lineHeight: 1.05, fontWeight: 740, color: palette.ink, textAlign: 'center'}}>{title}</div>
    <div style={{fontSize: 20, lineHeight: 1.1, fontWeight: 600, color: palette.muted, textAlign: 'center'}}>{subtitle}</div>
  </div>
);

type ExternalPanelProps = {
  readonly title: string;
  readonly position: {left: number; top: number; width: number; height: number};
  readonly opacity: number;
  readonly translateX: number;
  readonly side: 'source' | 'application';
};

const ExternalPanel = ({title, position, opacity, translateX, side}: ExternalPanelProps) => {
  const bands = side === 'source'
    ? ['Enterprise Systems', 'Cloud Platforms', 'Files / Other Sources']
    : ['Dashboards', 'Applications', 'AI Agents'];

  return (
    <aside
      aria-label={title}
      style={{
        position: 'absolute',
        ...position,
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        border: `2px solid ${palette.border}`,
        borderRadius: 10,
        background: palette.canvas,
        opacity,
        translate: `${translateX}px 0`,
        overflow: 'hidden',
      }}
    >
      <div style={{padding: '18px 14px 12px', color: palette.ink, fontSize: 28, lineHeight: 1.05, fontWeight: 740, textAlign: 'center'}}>{title}</div>
      <div style={{height: 2, margin: '0 16px', background: palette.border}} />
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 8, padding: '10px 16px 14px'}}>
        {bands.map((label) => (
          <div
            key={label}
            style={{
              minHeight: 40,
              display: 'grid',
              placeItems: 'center',
              boxSizing: 'border-box',
              padding: '5px 10px',
              border: `1px solid ${palette.border}`,
              borderRadius: 7,
              background: palette.surface,
              color: palette.ink,
              fontSize: side === 'source' ? 17 : 18,
              lineHeight: 1.1,
              fontWeight: 650,
              textAlign: 'center',
            }}
          >
            {label}
          </div>
        ))}
      </div>
    </aside>
  );
};

export const WorkspaceArchitecture = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const engineeringReveal = panelReveal(frame, fps, 1.1);
  const sourceReveal = interpolate(
    frame,
    [645, 655],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const sourceConnection = fade(frame, fps, 33.5, 1.0);
  const applicationReveal = interpolate(
    frame,
    [1030, 1040],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const applicationConnection = fade(frame, fps, 48, 1.0);
  const externalExit = interpolate(
    frame,
    [1430, 1450],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)},
  );
  const governanceReveal = interpolate(
    frame,
    [1460, 1470],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const consumptionReveal = interpolate(
    frame,
    [1525, 1535],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const governanceConnection = interpolate(
    frame,
    [1946, 1956],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const consumptionConnection = interpolate(
    frame,
    [2420, 2430],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const exit = interpolate(
    frame,
    [94.2 * fps, WORKSPACE_ARCHITECTURE_DURATION_SECONDS * fps],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)},
  );

  const sourceFocus = interpolate(
    frame,
    [685, 695],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const releaseFocus = interpolate(
    frame,
    [840, 850],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)},
  );
  const activeSourceFocus = sourceFocus * (1 - releaseFocus);
  const activeReleaseFocus = releaseFocus * (1 - governanceReveal);
  const engineeringAssetFocus = Math.max(activeSourceFocus, activeReleaseFocus);

  const sourceOpacity = sourceReveal * externalExit;
  const applicationOpacity = applicationReveal * externalExit;

  return (
    <AbsoluteFill
      style={{
    background: 'radial-gradient(circle at 50% 35%, #18365d 0%, #0b1830 34%, #060d19 74%)',
        color: palette.ink,
        fontFamily: FONT,
        overflow: 'hidden',
        opacity: exit,
      }}
    >
      <Audio
        name="Workspace architecture narration"
        src={staticFile('audio/workspace-architecture-narration.m4a')}
      />
      <svg
        role="img"
        aria-labelledby="workspace-architecture-title workspace-architecture-desc"
        width="1920"
        height="1080"
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', inset: 0}}
      >
        <title id="workspace-architecture-title">FabricOps workspace architecture</title>
        <desc id="workspace-architecture-desc">Governance, Engineering and Consumption workspaces form a vertical operating model, while Engineering receives external data and publishes outputs to external applications.</desc>
        <defs>
          <marker id="workspace-arrow-blue" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto">
            <path d="M0 0 L18 9 L0 18 Z" fill={palette.blue} />
          </marker>
          <marker id="workspace-arrow-purple" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto">
            <path d="M0 0 L18 9 L0 18 Z" fill={palette.purple} />
          </marker>
          <marker id="workspace-arrow-muted" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto">
            <path d="M0 0 L18 9 L0 18 Z" fill={palette.muted} />
          </marker>
        </defs>

        <g fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path
            d="M950 378 V302"
            stroke={palette.purple}
            strokeWidth="6"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={1 - governanceConnection}
            opacity={governanceConnection}
            markerEnd="url(#workspace-arrow-purple)"
          />
          <path
            d="M970 302 V378"
            stroke={palette.purple}
            strokeWidth="6"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={1 - governanceConnection}
            opacity={governanceConnection}
            markerEnd="url(#workspace-arrow-purple)"
          />
          <path
            d="M960 710 V786"
            stroke={palette.blue}
            strokeWidth="6"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={1 - consumptionConnection}
            opacity={consumptionConnection}
            markerEnd="url(#workspace-arrow-blue)"
          />
          <path
            d="M324 550 H360"
            stroke={palette.muted}
            strokeWidth="6"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={1 - sourceConnection}
            opacity={sourceConnection * externalExit}
            markerEnd="url(#workspace-arrow-muted)"
          />
          <path
            d="M1560 550 H1596"
            stroke={palette.blue}
            strokeWidth="6"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={1 - applicationConnection}
            opacity={applicationConnection * externalExit}
            markerEnd="url(#workspace-arrow-blue)"
          />
        </g>

        <g opacity={governanceConnection}>
          <rect x="986" y="316" width="310" height="42" rx="6" fill={palette.canvas} />
          <text x="1002" y="344" fill={palette.purpleDeep} fontFamily={FONT} fontSize="22" fontWeight="700">READ / WRITE METADATA</text>
        </g>
        <g opacity={consumptionConnection}>
          <rect x="986" y="734" width="160" height="42" rx="6" fill={palette.canvas} />
          <text x="1002" y="762" fill={palette.blueDeep} fontFamily={FONT} fontSize="22" fontWeight="700">READ ONLY</text>
        </g>
      </svg>

      <WorkspacePanel
        title="Governance Workspace"
        color={palette.purple}
        position={{left: 560, top: 80, width: 800, height: 210}}
        opacity={governanceReveal}
        translateY={(1 - governanceReveal) * -18}
      >
        <div style={{height: 148, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 28, padding: '0 34px'}}>
          <Lakehouse64Item aria-hidden="true" width={82} height={82} />
          <div>
            <div style={{fontSize: 34, lineHeight: 1.1, fontWeight: 760, color: palette.ink}}>Metadata Lakehouse</div>
            <div style={{marginTop: 10, fontSize: 23, lineHeight: 1.2, fontWeight: 620, color: palette.muted}}>Pipelines · Contracts · Runs · Profile · Lineage</div>
          </div>
        </div>
      </WorkspacePanel>

      <WorkspacePanel
        title="Engineering Workspace"
        color={palette.blue}
        position={{left: 360, top: 390, width: 1200, height: 320}}
        opacity={engineeringReveal}
        translateY={(1 - engineeringReveal) * 18}
      >
        <div style={{height: 258, display: 'flex', alignItems: 'center', gap: 18, padding: '18px 28px 24px'}}>
          <StageCard
            title="Source Lakehouse"
            subtitle="Staging · Source"
            icon={<Lakehouse64Item aria-hidden="true" width={60} height={60} />}
            opacity={1 - activeReleaseFocus * 0.48}
            translateX={0}
            flash={activeSourceFocus}
          />
          <StageCard
            title="Operations Lakehouse"
            subtitle="Bronze"
            icon={<Lakehouse64Item aria-hidden="true" width={60} height={60} />}
            opacity={1 - engineeringAssetFocus * 0.48}
            translateX={0}
            flash={0}
          />
          <StageCard
            title="Analytics Lakehouse"
            subtitle="Silver"
            icon={<Lakehouse64Item aria-hidden="true" width={60} height={60} />}
            opacity={1 - engineeringAssetFocus * 0.48}
            translateX={0}
            flash={0}
          />
          <StageCard
            title="Release Warehouse"
            subtitle="Gold"
            icon={<DataWarehouse64Item aria-hidden="true" width={60} height={60} />}
            opacity={1 - activeSourceFocus * 0.48}
            translateX={0}
            flash={activeReleaseFocus}
          />
        </div>
      </WorkspacePanel>

      <WorkspacePanel
        title="Consumption Workspace"
        color={palette.ink}
        position={{left: 560, top: 800, width: 800, height: 200}}
        opacity={consumptionReveal}
        translateY={(1 - consumptionReveal) * 18}
      >
        <div style={{height: 138, display: 'flex', alignItems: 'center', justifyContent: 'space-evenly', padding: '0 28px'}}>
          <div style={{display: 'grid', placeItems: 'center', gap: 8}}>
            <Notebook48Item aria-hidden="true" width={54} height={54} />
            <span style={{fontSize: 21, fontWeight: 650, color: palette.muted}}>Notebooks</span>
          </div>
          <div style={{display: 'grid', placeItems: 'center', gap: 8}}>
            <Lakehouse64Item aria-hidden="true" width={54} height={54} />
            <span style={{fontSize: 21, fontWeight: 650, color: palette.muted}}>Tables &amp; Files</span>
          </div>
          <div style={{display: 'grid', placeItems: 'center', gap: 8}}>
            <DataAgent48Item aria-hidden="true" width={54} height={54} />
            <span style={{fontSize: 21, fontWeight: 650, color: palette.muted}}>Data Agent</span>
          </div>
        </div>
      </WorkspacePanel>

      <ExternalPanel
        title="External Sources"
        position={{left: 64, top: 420, width: 260, height: 260}}
        opacity={sourceOpacity}
        translateX={(1 - sourceReveal) * -22}
        side="source"
      />
      <ExternalPanel
        title="External Applications"
        position={{left: 1596, top: 420, width: 260, height: 260}}
        opacity={applicationOpacity}
        translateX={(1 - applicationReveal) * 22}
        side="application"
      />
    </AbsoluteFill>
  );
};
