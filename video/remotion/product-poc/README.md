# FabricOps Remotion compositions

`FabricOpsHero` is the 30-second product proof of concept. `FabricOpsOverview` is the separate 6:59 scene-driven overview.

The overview is timed for the existing narration, but this repository does not currently contain that audio. Place the approved recording at `public/audio/fabricops-overview-narration.mp3`, then set the composition's `narration` input prop to `true`. The audio switch is deliberately isolated so previewing the complete visual timeline does not require a placeholder or synthesized voiceover.

```bash
npm run studio
npm run render:overview
```
