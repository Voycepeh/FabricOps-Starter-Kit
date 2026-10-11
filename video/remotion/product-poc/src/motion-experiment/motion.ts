import {Easing, interpolate, spring, type SpringConfig} from 'remotion';
import timeline from './timeline.json';

export const EXPERIMENT_TIMELINE = timeline;
export const EXPERIMENT_DURATION = Math.round(timeline.durationSeconds * timeline.fps);
export const SOURCE_START_FRAME = Math.round(timeline.sourceSegmentStartSeconds * timeline.fps);
export const LIFECYCLE_START_FRAME = Math.round((556 + 1069 + 1851) / 30 * timeline.fps);
export const SOURCE_LOCAL_START_FRAME = SOURCE_START_FRAME - LIFECYCLE_START_FRAME;

export const palette = {
  background: '#050b16',
  backgroundRaised: '#0a1424',
  surface: '#101d31',
  surfaceHigh: '#162944',
  text: '#f7f9fd',
  muted: '#92a4ba',
  faint: 'rgba(196, 215, 238, 0.12)',
  line: 'rgba(168, 194, 226, 0.23)',
  governance: '#a879ff',
  engineering: '#4ea1ff',
  production: '#38d991',
  consumer: '#ffad55',
} as const;

export const fonts = {
  display: 'Inter, ui-sans-serif, system-ui, sans-serif',
  mono: 'ui-monospace, SFMono-Regular, Consolas, monospace',
} as const;

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeIn = Easing.bezier(0.6, 0, 0.9, 0.35);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

export const progress = (
  seconds: number,
  start: number,
  end: number,
  easing: (value: number) => number = easeInOut,
) =>
  interpolate(seconds, [start, end], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing,
  });

export const settle = (
  frame: number,
  startSeconds: number,
  fps: number,
  config: Partial<SpringConfig> = {},
) =>
  spring({
    frame: frame - startSeconds * fps,
    fps,
    config: {damping: 18, stiffness: 150, mass: 0.8, ...config},
  });

export const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
export const mix = (from: number, to: number, amount: number) => from + (to - from) * amount;
