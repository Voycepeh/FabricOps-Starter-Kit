<style>
.fabricops-home-video {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  margin: 1.4rem 0 1rem;
  border-radius: 0.45rem;
  background: #050505;
}

.fabricops-home-primary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  margin: 0.2rem 0 1.6rem;
}

.fabricops-home-action {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 0.9rem;
  align-items: center;
  min-height: 6.3rem;
  padding: 1rem 1.05rem;
  border: 1px solid color-mix(in srgb, var(--md-primary-fg-color) 20%, var(--md-default-fg-color--lightest));
  border-radius: 0.7rem;
  background: linear-gradient(135deg, color-mix(in srgb, var(--md-primary-fg-color) 4%, var(--md-default-bg-color)), var(--md-default-bg-color) 68%);
  box-shadow: 0 0.12rem 0.45rem rgba(0, 0, 0, 0.04);
  color: var(--md-default-fg-color) !important;
  text-decoration: none;
  transition: border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease, background 150ms ease;
}

.fabricops-home-action:hover,
.fabricops-home-action:focus {
  border-color: var(--md-primary-fg-color);
  background: linear-gradient(135deg, color-mix(in srgb, var(--md-primary-fg-color) 8%, var(--md-default-bg-color)), var(--md-default-bg-color) 72%);
  box-shadow: 0 0.3rem 0.9rem rgba(15, 143, 131, 0.12);
  transform: translateY(-0.08rem);
}

.fabricops-home-action:focus-visible {
  outline: 0.12rem solid var(--md-primary-fg-color);
  outline-offset: 0.12rem;
}

.fabricops-home-action__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3.5rem;
  height: 4rem;
}

.md-typeset .fabricops-home-action__icon img {
  display: block;
  width: 100%;
  height: 100%;
  margin: 0;
  border: 0;
  border-radius: 0;
  object-fit: contain;
}

.fabricops-home-action__copy {
  min-width: 0;
}

.fabricops-home-action__label {
  display: block;
  margin-bottom: 0.18rem;
  color: var(--md-primary-fg-color);
  font-size: 0.96rem;
  font-weight: 800;
  line-height: 1.25;
}

.fabricops-home-action__body {
  display: block;
  color: var(--md-default-fg-color--light);
  font-size: 0.78rem;
  line-height: 1.4;
}

.fabricops-home-action__arrow {
  color: var(--md-primary-fg-color);
  font-size: 1.1rem;
  line-height: 1;
  transition: transform 150ms ease;
}

.fabricops-home-action:hover .fabricops-home-action__arrow,
.fabricops-home-action:focus .fabricops-home-action__arrow {
  transform: translateX(0.12rem);
}

.fabricops-home-quicklinks {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 0.85rem 0 1.5rem;
}

.fabricops-home-quicklinks--assets {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.fabricops-home-quicklink {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 3rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.35rem;
  background: var(--md-default-bg-color);
  box-shadow: 0 0.08rem 0.3rem rgba(0, 0, 0, 0.035);
  color: var(--md-default-fg-color) !important;
  font-weight: 700;
  line-height: 1.25;
}

.fabricops-home-quicklink::after {
  content: "→";
  margin-left: 0.6rem;
  color: var(--md-primary-fg-color);
}

.fabricops-home-quicklink:hover,
.fabricops-home-quicklink:focus {
  border-color: var(--md-primary-fg-color);
  background: var(--md-accent-fg-color--transparent);
}


.fabricops-feature-intro {
  max-width: 48rem;
  margin: -0.2rem 0 0.9rem;
  color: var(--md-default-fg-color--light);
}

.fabricops-feature-grid {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: clamp(20rem, 36vw, 23rem);
  gap: 0.75rem;
  margin: 0.9rem 0 1.7rem;
  padding: 0 0 0.45rem;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scroll-snap-type: inline mandatory;
  scrollbar-width: thin;
  scrollbar-color: var(--md-primary-fg-color) transparent;
}

.fabricops-feature-grid::-webkit-scrollbar {
  height: 0.35rem;
}

.fabricops-feature-grid::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: var(--md-primary-fg-color);
}

.fabricops-feature-grid::-webkit-scrollbar-track {
  background: transparent;
}

.fabricops-feature-card {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.7rem;
  background: var(--md-default-bg-color);
  box-shadow: 0 0.12rem 0.45rem rgba(0, 0, 0, 0.045);
  color: var(--md-default-fg-color) !important;
  text-decoration: none;
  scroll-snap-align: start;
  transition: border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
}

.fabricops-feature-card:hover,
.fabricops-feature-card:focus {
  border-color: var(--md-primary-fg-color);
  box-shadow: 0 0.35rem 1rem rgba(15, 143, 131, 0.12);
  transform: translateY(-0.08rem);
}

.fabricops-feature-card__media {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 13rem;
  padding: 0.45rem;
  background: color-mix(in srgb, var(--md-primary-fg-color) 4%, var(--md-default-bg-color));
}

.fabricops-feature-card__media img {
  display: block;
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 0.4rem;
}

.fabricops-feature-card__content {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0.9rem 0.95rem 0.95rem;
}

.fabricops-feature-card__title {
  margin: 0.35rem 0 0.35rem;
  color: var(--md-default-fg-color);
  font-size: 0.92rem;
  font-weight: 800;
  line-height: 1.3;
}

.fabricops-feature-card__copy {
  margin: 0 0 0.8rem;
  color: var(--md-default-fg-color--light);
  font-size: 0.72rem;
  line-height: 1.45;
}

.fabricops-feature-card__cta {
  margin-top: auto;
  color: var(--md-primary-fg-color);
  font-size: 0.7rem;
  font-weight: 800;
}

.fabricops-feature-card__cta::after {
  content: " →";
}

@media screen and (max-width: 900px) {
  .fabricops-feature-grid {
    grid-auto-columns: min(23rem, 82vw);
  }
}

@media screen and (max-width: 720px) {
  .fabricops-home-primary {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 560px) {
  .fabricops-feature-grid {
    grid-auto-columns: 86vw;
    gap: 0.65rem;
  }

  .fabricops-feature-card__media {
    height: 11.5rem;
  }
}

@media screen and (max-width: 900px) {
  .fabricops-home-quicklinks {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media screen and (max-width: 520px) {
  .fabricops-home-action {
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 0.75rem;
    min-height: 5.8rem;
    padding: 0.9rem;
  }

  .fabricops-home-action__icon {
    width: 3rem;
    height: 3.5rem;
  }

  .fabricops-home-quicklinks {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="fabricops-landing" markdown="1">

# Microsoft Fabric gives you the platform.
### FabricOps gives you the Plug-and-play Data Engineering and Data Governance foundations.

## Start here

<div class="fabricops-home-primary">
  <a class="fabricops-home-action" href="how-fabricops-works/">
    <span class="fabricops-home-action__icon" aria-hidden="true">
      <img src="assets/mascots/robot-neutral.png" alt="" width="1254" height="1254">
    </span>
    <span class="fabricops-home-action__copy">
      <span class="fabricops-home-action__label">How FabricOps works</span>
      <span class="fabricops-home-action__body">See how Governance and Engineering work together across the FabricOps lifecycle.</span>
    </span>
    <span class="fabricops-home-action__arrow" aria-hidden="true">→</span>
  </a>

  <a class="fabricops-home-action" href="guided-demo/">
    <span class="fabricops-home-action__icon" aria-hidden="true">
      <img src="assets/mascots/robot-pointing.png" alt="" width="1254" height="1254">
    </span>
    <span class="fabricops-home-action__copy">
      <span class="fabricops-home-action__label">Step-by-step Guided Demo</span>
      <span class="fabricops-home-action__body">Follow practical steps, screenshots, and expected results. Microsoft Fabric access is required.</span>
    </span>
    <span class="fabricops-home-action__arrow" aria-hidden="true">→</span>
  </a>
</div>

<a class="fabricops-metadata-preview" href="reference/metadata/" aria-label="Explore the interactive FabricOps metadata relationship map">
  <span class="fabricops-metadata-preview__body">
    <span class="fabricops-metadata-preview__eyebrow">Interactive reference</span>
    <strong class="fabricops-metadata-preview__title">Explore the Metadata Tables map</strong>
    <span class="fabricops-metadata-preview__description">See how Governance and Engineering tables connect, then inspect their keys, relationships and schemas.</span>
    <span class="fabricops-metadata-preview__action">Open interactive map <span aria-hidden="true">→</span></span>
  </span>
  <span class="fabricops-metadata-preview__image" aria-hidden="true">
    <img src="assets/fabricops-metadata-approved.svg" alt="" loading="lazy" decoding="async">
  </span>
</a>

<video class="fabricops-home-video" controls preload="metadata" playsinline aria-label="FabricOps overview video">
  <source src="assets/FabricOps_Overview_Video_web.mp4" type="video/mp4">
  Your browser does not support embedded video. <a href="assets/FabricOps_Overview_Video_web.mp4">Open the FabricOps overview video</a>.
</video>


## Featured Solutions

<p class="fabricops-feature-intro">
Explore the key capabilities FabricOps provides within that operating model. Each solution includes a walkthrough and implementation context. Live solutions are ready to use; Preview capabilities are still being developed.
</p>

<div class="fabricops-feature-grid">
  <a class="fabricops-feature-card" href="solutions/plug-and-play-data-pipelines/"><span class="fabricops-feature-card__media"><img src="assets/05/PipelinesDeploymentOverview.png" alt="Same FabricOps pipeline promoted from Development to Production"></span><span class="fabricops-feature-card__content"><span><span class="fabricops-release-status fabricops-release-status--live">Live</span></span><span class="fabricops-feature-card__title">Plug-and-Play Data Pipelines with Data Contract Enforcement</span><span class="fabricops-feature-card__copy">Promote the same pipeline from Development to Production while configuration resolves environment-specific Fabric resources.</span><span class="fabricops-feature-card__cta">Explore solution</span></span></a>
  <a class="fabricops-feature-card" href="solutions/ai-assisted-data-contract-authoring/"><span class="fabricops-feature-card__media"><img src="assets/AiDatacontract.png" alt="Direct & Indirect PII Discovery & Treatment with Built-in AI Suggestions"></span><span class="fabricops-feature-card__content"><span><span class="fabricops-release-status fabricops-release-status--preview">Preview</span></span><span class="fabricops-feature-card__title">Direct & Indirect PII Discovery & Treatment with Built-in AI Suggestions</span><span class="fabricops-feature-card__copy">Identify Direct and Indirect PII, review the suggested classification, and apply governed Mask, Bucket, Tokenize, or Remove treatments. Built-in AI suggestions accelerate authoring while Governance remains in control.</span><span class="fabricops-feature-card__cta">Explore solution</span></span></a>
  <a class="fabricops-feature-card" href="solutions/business-rules-to-data-quality/"><span class="fabricops-feature-card__media"><img src="assets/BusinessRuletoDQ.png" alt="Business rules converted into enforceable Data Quality rules"></span><span class="fabricops-feature-card__content"><span><span class="fabricops-release-status fabricops-release-status--preview">Preview</span></span><span class="fabricops-feature-card__title">Data Quality Rules from Natural Language</span><span class="fabricops-feature-card__copy">Describe what clean data means in natural language and turn one nuanced business requirement into multiple reviewable, deterministic Data Quality rules.</span><span class="fabricops-feature-card__cta">Explore solution</span></span></a>
</div>

## Download FabricOps

<p>Get the Python package, reusable notebook templates, and demo assets to start building. Follow the <a href="guided-demo/">Guided Demo</a> to put them to work.</p>

<div class="fabricops-home-quicklinks fabricops-home-quicklinks--assets">
  <a class="fabricops-home-quicklink" href="releases/">Releases (Python package)</a>
  <a class="fabricops-home-quicklink" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks">Notebook Templates</a>
  <a class="fabricops-home-quicklink" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData">Demo Assets</a>
</div>

## Reference Documentation

<p>Explore FabricOps functions, Data Quality rules, metadata structures, and implementation guidance.</p>

<div class="fabricops-home-quicklinks">
  <a class="fabricops-home-quicklink" href="reference/">Function Reference</a>
  <a class="fabricops-home-quicklink" href="reference/dq-rules/">Data Quality Rules</a>
  <a class="fabricops-home-quicklink" href="reference/metadata/">Metadata Tables</a>
  <a class="fabricops-home-quicklink" href="reference/pyspark-transformation/">PySpark Transformation</a>
  <a class="fabricops-home-quicklink" href="glossary/">Glossary</a>
</div>

</div>
