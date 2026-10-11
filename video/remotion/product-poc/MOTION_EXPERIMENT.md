# FabricOps Part 1 motion upgrade

This composition is a full-length, motion-enhanced treatment of FabricOps Part 1. The original `FabricOpsHero` remains available and unchanged as the content authority. `FabricOpsPart1Motion` preserves its 202.9-second narration, five-scene structure, terminology, seven-step lifecycle and hand-off to Part 2 while adding restrained camera direction, lighting, depth and sound cues.

## Timing model

`src/motion-experiment/timeline.json` is the centralized edit map. For every scene it records start and end timestamps, message, focus, visible text, narration alignment, camera keyframes, element windows, animation beats and text holds. It also owns sound cues and significant review timestamps.

Human-readable timestamps and scene-by-scene review notes are generated in `MOTION_REVIEW_GUIDE.md`.

## Reproduce

From `video/remotion/product-poc`:

```bash
npm install
npm run typecheck
npm run motion:sfx
npm run motion:guide
npm run motion:render
npm run motion:sheets
```

The final video is `out/motion-experiment/FabricOps-Part1-Motion-Full.mp4`. Contact sheets are grouped by scene and include an additional significant-beats sheet. Outputs are intentionally ignored by Git. The existing narration and generated sound layer are staged locally under ignored `public/` paths; no audio samples are downloaded.

The render workflow asks Remotion for deterministic JPEG sequences, then assembles them with the pinned `ffmpeg-static` development dependency. This avoids a Windows crash in Remotion 4.0.479's bundled compositor while preserving Remotion as the rendering framework.

## Targeted timestamp review

Render any synchronized range:

```bash
npm run motion:preview -- --from 01:24 --to 01:32
```

Export the exact global frame nearest a timestamp:

```bash
npm run motion:frame -- --at 01:26.5
```

Both commands use global Part 1 timestamps. Partial videos trim narration and sound design from the same global point, so visual and audio timing remain synchronized.

## Design decisions

The enhanced composition reuses the original scene components rather than introducing a second set of explanations. Camera movement follows the current narrated subject while leaving surrounding context visible. Lighting and sound remain secondary to the existing content, and no new product claims are introduced.

The earlier original-versus-enhanced sample, 3840 x 1080 comparison composition and comparison render outputs have been removed. The published video under `docs/assets/` is not changed by this workflow.

## Review result

The full composition was rendered and reviewed twice. The first review found an empty frame at `00:00`; the final pass adds a restrained opening anchor and confirms the correction in the regular and significant-beat contact sheets. The significant-beat sheet samples 0.5 seconds before, at and after every scene boundary so transition pacing is visible alongside the narration-aligned beats.
