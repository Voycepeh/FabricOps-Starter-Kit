import type {ReactNode} from 'react';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Easing, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CTA} from '../scenes/CTA';
import {FabricOpsReveal} from '../scenes/FabricOpsReveal';
import {LifecycleScene} from '../scenes/LifecycleScene';
import {NotebookJourney} from '../scenes/NotebookJourney';
import {OpeningPlatform} from '../scenes/OpeningPlatform';
import {font, theme} from '../theme';
import {SCENE_STARTS, VIDEO_CONFIG} from '../videoConfig';
import {cameraAt, palette, sceneById, type MotionScene} from './motion';

const narration = staticFile('audio/FabricOps_narration_master_numbered.m4a');
const soundDesign = staticFile('generated/fabricops-part1-motion-sfx.wav');

const sceneAccents: Record<string, string> = {
  opening: palette.engineering,
  fabricOps: palette.production,
  notebooks: palette.engineering,
  lifecycle: palette.governance,
  cta: palette.production,
};

const CameraScene = ({scene, children}: {scene: MotionScene; children: ReactNode}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const globalSeconds = scene.start + frame / fps;
  const camera = cameraAt(scene, globalSeconds);
  const left = width / 2 - camera.x * camera.scale;
  const top = height / 2 - camera.y * camera.scale;
  const accent = sceneAccents[scene.id] ?? palette.engineering;

  return (
    <AbsoluteFill style={{overflow: 'hidden', background: palette.background}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 48%, ${accent}18 0%, #0b1830 38%, #060d19 78%)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left,
          top,
          width,
          height,
          scale: camera.scale,
          transformOrigin: 'top left',
          willChange: 'left, top, scale',
        }}
      >
        {children}
      </div>
      <AbsoluteFill
        style={{
          pointerEvents: 'none',
          background: 'radial-gradient(ellipse at center, transparent 58%, rgba(2,7,15,0.36) 100%)',
          boxShadow: `inset 0 0 140px ${accent}0a`,
        }}
      />
      <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.055, mixBlendMode: 'soft-light'}}>
        <svg width="100%" height="100%">
          <filter id={`motion-grain-${scene.id}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.68" numOctaves={2} seed={Math.floor(globalSeconds * 6) % 97} stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#motion-grain-${scene.id})`} />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const OpeningFrameAnchor = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: 360,
        display: 'flex',
        justifyContent: 'center',
        opacity: interpolate(frame, [0, 0.8 * fps], [1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        }),
        translate: '0 -50%',
        fontSize: VIDEO_CONFIG.text.fabricHero,
        lineHeight: 1,
        fontWeight: 840,
        letterSpacing: -7,
        textShadow: '0 24px 80px #000',
        pointerEvents: 'none',
      }}
    >
      <span style={{color: '#fff'}}>Microsoft&nbsp;</span>
      <span style={{color: theme.production}}>Fabric</span>
    </div>
  );
};

export const FabricOpsPart1Motion = () => {
  const {fps} = useVideoConfig();
  const opening = sceneById('opening');
  const fabricOps = sceneById('fabricOps');
  const notebooks = sceneById('notebooks');
  const lifecycle = sceneById('lifecycle');
  const cta = sceneById('cta');

  return (
    <AbsoluteFill style={{background: theme.background, color: theme.text, fontFamily: font, overflow: 'hidden'}}>
      <Sequence name="Opening — Microsoft Fabric" from={SCENE_STARTS.opening} durationInFrames={VIDEO_CONFIG.scenes.opening} premountFor={fps}>
        <CameraScene scene={opening}><OpeningPlatform /></CameraScene>
        <OpeningFrameAnchor />
      </Sequence>
      <Sequence name="Why FabricOps" from={SCENE_STARTS.fabricOps} durationInFrames={VIDEO_CONFIG.scenes.fabricOps} premountFor={fps}>
        <CameraScene scene={fabricOps}><FabricOpsReveal /></CameraScene>
      </Sequence>
      <Sequence name="Notebook foundation" from={SCENE_STARTS.notebooks} durationInFrames={VIDEO_CONFIG.scenes.notebooks} premountFor={fps}>
        <CameraScene scene={notebooks}><NotebookJourney /></CameraScene>
      </Sequence>
      <Sequence name="Seven-step lifecycle" from={SCENE_STARTS.workflow} durationInFrames={VIDEO_CONFIG.scenes.workflow} premountFor={fps}>
        <CameraScene scene={lifecycle}><LifecycleScene /></CameraScene>
      </Sequence>
      <Sequence name="Continue to Guided Demo" from={SCENE_STARTS.cta} durationInFrames={VIDEO_CONFIG.scenes.cta} premountFor={fps}>
        <CameraScene scene={cta}><CTA /></CameraScene>
      </Sequence>
      <Audio name="Original narration" src={narration} />
      <Audio name="Restrained motion sound design" src={soundDesign} volume={0.36} />
    </AbsoluteFill>
  );
};
