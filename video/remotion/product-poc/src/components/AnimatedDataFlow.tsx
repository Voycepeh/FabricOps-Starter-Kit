import {memo, type CSSProperties, type ReactNode} from 'react';

const clamp = (value: number) => Math.max(0, Math.min(1, value));

type AnimatedDataFlowProps = {
  children: ReactNode;
  style?: CSSProperties;
};

export const AnimatedDataFlow = ({children, style}: AnimatedDataFlowProps) => <svg
  aria-hidden="true"
  viewBox="0 0 1920 1080"
  style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none', ...style}}
>
  {children}
</svg>;

type FlowPulseProps = {
  d: string;
  progress: number;
  color: string;
  radius?: number;
};

export const FlowPulse = memo(({d, progress, color, radius = 8}: FlowPulseProps) => {
  const bounded = clamp(progress);
  if (bounded <= 0.02 || bounded >= 0.99) return null;

  return <circle
    cx={0}
    cy={0}
    r={radius}
    fill="#f7fbff"
    stroke={color}
    strokeWidth={4}
    style={{
      offsetPath: `path('${d}')`,
      offsetDistance: `${bounded * 100}%`,
      offsetRotate: '0deg',
      filter: `drop-shadow(0 0 5px #ffffff) drop-shadow(0 0 13px ${color})`,
    } as CSSProperties}
  />;
});

type AnimatedFlowPathProps = {
  id: string;
  d: string;
  progress: number;
  color: string;
  baseColor?: string;
  strokeWidth?: number;
  arrow?: boolean;
  pulse?: boolean;
  opacity?: number;
  dashed?: boolean;
};

export const AnimatedFlowPath = memo(({
  id,
  d,
  progress,
  color,
  baseColor = '#29415d',
  strokeWidth = 6,
  arrow = true,
  pulse = true,
  opacity = 1,
  dashed = false,
}: AnimatedFlowPathProps) => {
  const bounded = clamp(progress);
  const markerId = `flow-arrow-${id}`;
  if (opacity <= 0) return null;

  return <g opacity={opacity}>
    <defs>
      <marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto">
        <path d="M0 0 L10 5 L0 10z" fill={color} />
      </marker>
    </defs>
    <path
      d={d}
      fill="none"
      stroke={baseColor}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray={dashed ? '10 12' : undefined}
    />
    <path
      d={d}
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth + 9}
      strokeLinecap="round"
      strokeLinejoin="round"
      pathLength={1}
      strokeDasharray="1"
      strokeDashoffset={1 - bounded}
      opacity={0.13}
      style={{filter: `drop-shadow(0 0 13px ${color})`}}
    />
    <path
      d={d}
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      pathLength={1}
      strokeDasharray="1"
      strokeDashoffset={1 - bounded}
      markerEnd={arrow && bounded > 0.97 ? `url(#${markerId})` : undefined}
      style={{filter: `drop-shadow(0 0 7px ${color})`}}
    />
    {pulse ? <FlowPulse d={d} progress={bounded} color={color} radius={strokeWidth + 2} /> : null}
  </g>;
});

type FlowErrorProps = {
  id: string;
  d: string;
  progress: number;
  endX: number;
  endY: number;
};

export const FlowError = ({id, d, progress, endX, endY}: FlowErrorProps) => <>
  <AnimatedFlowPath id={id} d={d} progress={progress} color="#ff756d" baseColor="#4d2b38" strokeWidth={5} arrow={false} />
  <g opacity={clamp((progress - 0.78) / 0.22)}>
    <circle cx={endX} cy={endY} r={15} fill="#311823" stroke="#ff756d" strokeWidth={4} />
    <path d={`M${endX - 6} ${endY - 6} L${endX + 6} ${endY + 6} M${endX + 6} ${endY - 6} L${endX - 6} ${endY + 6}`} stroke="#ffcbc7" strokeWidth={4} strokeLinecap="round" />
  </g>
</>;
