<style>
.fabricops-home-video {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 16 / 9;
  margin: 1.4rem 0 1rem;
  border-radius: 0.45rem;
  background: #050505;
  color: #ffffff;
  font-size: clamp(1.05rem, 2.2vw, 1.55rem);
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.fabricops-home-primary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin: 0 0 1.5rem;
}

.fabricops-home-primary .fabricops-landing-card {
  min-height: 7rem;
}

.fabricops-home-summary {
  margin: 1.25rem 0 1.5rem;
  text-align: center;
}

.fabricops-home-summary img {
  display: inline-block;
  width: 100%;
  max-width: 42rem;
  height: auto;
}

.fabricops-home-summary figcaption {
  margin-top: 0.5rem;
  color: var(--md-default-fg-color--light);
  font-size: 0.82rem;
}

.fabricops-home-quicklinks {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 0.85rem 0 1.5rem;
}

.fabricops-home-quicklink {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 3.3rem;
  padding: 0.75rem 0.9rem;
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

@media screen and (max-width: 768px) {
  .fabricops-home-primary,
  .fabricops-home-quicklinks {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="fabricops-landing" markdown="1">

# FabricOps documentation

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

FabricOps is a plug-and-play Data Engineering and Data Governance practice for Microsoft Fabric, packaging repeatable operating foundations so teams can focus on project-specific engineering and analytics.

<div class="fabricops-home-video" role="img" aria-label="FabricOps overview video coming soon">
  Video coming soon
</div>

<div class="fabricops-home-primary">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps works</span>
    <span class="fabricops-landing-card__body">Understand the operating model, Governance ↔ Engineering loop, Data Contract lifecycle, and Production path.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Step-by-step Guided Demo</span>
    <span class="fabricops-landing-card__body">Run the complete FabricOps workflow with practical actions, screenshots, expected results, and deeper links.</span>
  </a>
</div>

<figure class="fabricops-home-summary">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
  <figcaption>One shared operating foundation connecting Governance, Data Engineering, and downstream AI and BI analytics.</figcaption>
</figure>

## Explore FabricOps

<div class="fabricops-home-quicklinks">
  <a class="fabricops-home-quicklink" href="notebook-templates/">Notebook Templates</a>
  <a class="fabricops-home-quicklink" href="reference/engineering-cheat-sheet/">FabricOps Engineering Guide</a>
  <a class="fabricops-home-quicklink" href="glossary/">Glossary</a>
  <a class="fabricops-home-quicklink" href="reference/metadata/">Metadata Tables</a>
  <a class="fabricops-home-quicklink" href="reference/">Functions</a>
  <a class="fabricops-home-quicklink" href="reference/dq-rules/">DQ Rules</a>
  <a class="fabricops-home-quicklink" href="releases/">Releases</a>
</div>

</div>
