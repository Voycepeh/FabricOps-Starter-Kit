# FabricOps Part 1 motion experiment

This experiment compares the original Part 1 lifecycle animation with a motion-designed version of the same 29.5-second segment. It starts at the original 02:33.5 mark and preserves the original timings and technical meaning for Step 5, Step 6, and Step 7.

## Compositions

- `FabricOpsPart1OriginalSample` — unchanged `LifecycleScene` visuals and timing, framed as a standalone sample.
- `FabricOpsPart1MotionExperiment` — enhanced 1920×1080 sample at 30 fps.
- `FabricOpsPart1MotionComparison` — 3840×1080 side-by-side comparison at 30 fps.

The shared timing source is `src/motion-experiment/timeline.json`. It drives visual beats and the procedural sound-design script.

## Reproduce

From `video/remotion/product-poc`:

```bash
npm install
npm run typecheck
npm run motion:sfx
npm run motion:render
npm run motion:sheets
```

Outputs are written to `out/motion-experiment/` and intentionally ignored by Git. The existing narration and generated sound layer are staged locally under ignored `public/` paths; no audio samples are downloaded.

The render script asks Remotion for deterministic JPEG frame sequences, then assembles them with the pinned `ffmpeg-static` development dependency. This avoids a Windows crash in Remotion 4.0.479's bundled compositor while preserving Remotion as the rendering framework.

## Comparison notes

The enhanced version replaces the static overview-board treatment with a guided camera journey. It keeps the lifecycle wording intact while introducing a clear visual hierarchy, persistent promotion token, layered workspace depth, state-driven lighting, flowing data packets, and a single payoff as approved Production data reaches the Consumer workspace. Motion uses deliberate bezier curves and restrained springs; exits are faster than entrances, and readable states receive dedicated holds.

The experiment is deliberately scoped to Steps 5–7. A full-video rollout would still need scene-by-scene storyboarding, narration-aware retiming, and a consistent sound mix across the complete Part 1 composition.

## Review result

The first contact-sheet pass exposed an empty opening frame and residual Production labels behind the Step 7 hold. The final pass keeps Step 5 readable from frame zero, clears each departing workspace before the next settles, and holds the Consumer destination cleanly through the ending. The final review samples every 2.5 seconds across all three outputs.

The experiment demonstrates a stronger visual hierarchy and more legible hand-offs without changing the source narration or lifecycle meaning. Remaining work for a production rollout is deliberately outside this experiment: extend the visual language across the full story, tune the procedural sound layer against the complete narration mix, and replace system-font assumptions if a locked cross-platform typeface is required.
