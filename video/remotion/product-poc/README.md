# FabricOps Remotion product-video POC

A 25-second native Remotion motion-graphics prototype for a more polished FabricOps product-video direction.

This prototype intentionally does not animate or crop the existing slide artwork. Core visuals are built as React/CSS components so workspaces, pipelines, contracts, connectors, Production, and consumers can be redesigned and animated independently.

## Creative sequence

1. Fragmented Fabric setup
2. FabricOps becomes the operating layer
3. Governance and Engineering collaborate through the Data Contract
4. The validated pipeline and activated contract move into Production
5. Seven consumer workspaces connect only to Production

## Run in Codex Cloud or locally

From this directory:

```bash
npm install
npm run studio
```

Open the `FabricOpsHero` composition in Remotion Studio.

## Render

```bash
npm run render
```

Output:

```text
out/FabricOpsHero.mp4
```

## Scope

This is a visual-direction prototype only. It does not change FabricOps runtime behaviour, package APIs, documentation navigation, or the current published homepage video.

The next iteration should improve visual polish before expanding duration: typography, spatial composition, micro-motion, connector animation, validation states, and FabricOps hero identity.
