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
  grid-template-columns: 1fr;
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
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--md-primary-fg-color) 10%, transparent);
  color: var(--md-primary-fg-color);
}

.fabricops-home-action__icon svg {
  width: 1.25rem;
  height: 1.25rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 0.85rem 0 1.5rem;
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
  margin: -0.2rem 0 1rem;
  color: var(--md-default-fg-color--light);
}

.fabricops-feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin: 1rem 0 1.7rem;
}

.fabricops-feature-card {
  overflow: hidden;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.6rem;
  background: var(--md-default-bg-color);
  box-shadow: 0 0.12rem 0.45rem rgba(0, 0, 0, 0.04);
}

.fabricops-feature-card__media {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 16 / 9;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--md-primary-fg-color) 7%, var(--md-default-bg-color)), var(--md-default-bg-color));
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
}

.fabricops-feature-card__play {
  display: grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border: 1px solid color-mix(in srgb, var(--md-primary-fg-color) 35%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--md-primary-fg-color) 9%, var(--md-default-bg-color));
  color: var(--md-primary-fg-color);
  font-size: 1rem;
}

.fabricops-feature-card__status {
  position: absolute;
  left: 0.8rem;
  bottom: 0.7rem;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--md-default-bg-color) 88%, transparent);
  color: var(--md-default-fg-color--light);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.fabricops-feature-card__body {
  padding: 0.9rem 1rem 1rem;
}

.fabricops-feature-card__title {
  margin: 0 0 0.35rem;
  color: var(--md-default-fg-color);
  font-size: 0.98rem;
  font-weight: 800;
  line-height: 1.3;
}

.fabricops-feature-card__copy {
  margin: 0;
  color: var(--md-default-fg-color--light);
  font-size: 0.76rem;
  line-height: 1.45;
}

@media screen and (max-width: 760px) {
  .fabricops-feature-grid {
    grid-template-columns: 1fr;
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
    width: 2.35rem;
    height: 2.35rem;
  }

  .fabricops-home-quicklinks {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="fabricops-landing" markdown="1">

# FabricOps documentation

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

Plug-and-play Data Engineering and Data Governance foundations for Microsoft Fabric.

<video class="fabricops-home-video" controls preload="metadata" playsinline aria-label="FabricOps overview video">
  <source src="assets/FabricOps_Overview_Video_web.mp4" type="video/mp4">
  Your browser does not support embedded video. <a href="assets/FabricOps_Overview_Video_web.mp4">Open the FabricOps overview video</a>.
</video>

<div class="fabricops-home-primary">
  <a class="fabricops-home-action" href="how-fabricops-works/">
    <span class="fabricops-home-action__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M6 3.5h8l4 4v13H6z"></path><path d="M14 3.5v4h4M9 12h6M9 15.5h6"></path></svg>
    </span>
    <span class="fabricops-home-action__copy">
      <span class="fabricops-home-action__label">How FabricOps works</span>
      <span class="fabricops-home-action__body">See the operating model, Governance ↔ Engineering loop, Data Contracts, and Production path.</span>
    </span>
    <span class="fabricops-home-action__arrow" aria-hidden="true">→</span>
  </a>

  <a class="fabricops-home-action" href="guided-demo/">
    <span class="fabricops-home-action__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><circle cx="5" cy="18" r="2"></circle><circle cx="12" cy="11" r="2"></circle><circle cx="19" cy="5" r="2"></circle><path d="M6.5 16.7 10.5 12.5M13.5 9.7 17.5 6.3"></path></svg>
    </span>
    <span class="fabricops-home-action__copy">
      <span class="fabricops-home-action__label">Step-by-step Guided Demo</span>
      <span class="fabricops-home-action__body">Run the workflow yourself with practical actions, screenshots, and expected results.</span>
    </span>
    <span class="fabricops-home-action__arrow" aria-hidden="true">→</span>
  </a>
</div>


## See FabricOps in action

<p class="fabricops-feature-intro">
Short feature walkthroughs will show how FabricOps works in real Microsoft Fabric workflows. These recordings are coming next.
</p>

<div class="fabricops-feature-grid">
  <article class="fabricops-feature-card">
    <div class="fabricops-feature-card__media" aria-label="AI-assisted Data Contracting video placeholder">
      <span class="fabricops-feature-card__play" aria-hidden="true">▶</span>
      <span class="fabricops-feature-card__status">Screen recording coming soon</span>
    </div>
    <div class="fabricops-feature-card__body">
      <h3 class="fabricops-feature-card__title">AI-assisted Data Contracting</h3>
      <p class="fabricops-feature-card__copy">Turn plain-language business requirements into reviewable, deterministic Data Quality rules, then save and freeze them into a governed Data Contract.</p>
    </div>
  </article>

  <article class="fabricops-feature-card">
    <div class="fabricops-feature-card__media" aria-label="Clonable pipeline building blocks video placeholder">
      <span class="fabricops-feature-card__play" aria-hidden="true">▶</span>
      <span class="fabricops-feature-card__status">Screen recording coming soon</span>
    </div>
    <div class="fabricops-feature-card__body">
      <h3 class="fabricops-feature-card__title">Clonable Pipeline Building Blocks</h3>
      <p class="fabricops-feature-card__copy">Reuse standard Read and Write blocks in <code>02_pipeline</code>, change only the small configuration surface, and keep project transformation logic as normal PySpark.</p>
    </div>
  </article>

  <article class="fabricops-feature-card">
    <div class="fabricops-feature-card__media" aria-label="Composite access rights scanner video placeholder">
      <span class="fabricops-feature-card__play" aria-hidden="true">▶</span>
      <span class="fabricops-feature-card__status">Screen recording coming soon</span>
    </div>
    <div class="fabricops-feature-card__body">
      <h3 class="fabricops-feature-card__title">Composite Access Rights Scanner</h3>
      <p class="fabricops-feature-card__copy">Inspect effective access across combined grants and governed security relationships instead of relying on a single simplistic permission view.</p>
    </div>
  </article>

  <article class="fabricops-feature-card">
    <div class="fabricops-feature-card__media" aria-label="Environment-aware deployment video placeholder">
      <span class="fabricops-feature-card__play" aria-hidden="true">▶</span>
      <span class="fabricops-feature-card__status">Screen recording coming soon</span>
    </div>
    <div class="fabricops-feature-card__body">
      <h3 class="fabricops-feature-card__title">Environment-aware Deployment</h3>
      <p class="fabricops-feature-card__copy">Promote the same config-driven notebooks through Fabric deployment pipelines while logical store names resolve the correct Development, Test, and Production resources.</p>
    </div>
  </article>
</div>

## Explore FabricOps

<div class="fabricops-home-quicklinks">
  <a class="fabricops-home-quicklink" href="notebook-templates/">Notebook Templates</a>
  <a class="fabricops-home-quicklink" href="reference/engineering-cheat-sheet/">FabricOps Engineering</a>
  <a class="fabricops-home-quicklink" href="glossary/">Glossary</a>
  <a class="fabricops-home-quicklink" href="reference/metadata/">Metadata Tables</a>
  <a class="fabricops-home-quicklink" href="reference/">Function Reference</a>
  <a class="fabricops-home-quicklink" href="function-call-graph/">Call Flow</a>
  <a class="fabricops-home-quicklink" href="reference/dq-rules/">DQ Rules</a>
  <a class="fabricops-home-quicklink" href="releases/">Releases</a>
</div>

</div>
