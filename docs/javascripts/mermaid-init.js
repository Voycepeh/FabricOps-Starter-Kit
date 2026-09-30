document$.subscribe(function () {
  if (typeof mermaid !== 'undefined') {
    document.querySelectorAll('.mermaid').forEach(function (diagram) {
      diagram.textContent = diagram.textContent
        .replace(/\b(flowchart|graph)\s+LR\b/g, '$1 TD')
        .replace(/\bdirection\s+LR\b/g, 'direction TD');
    });

    mermaid.initialize({ startOnLoad: false });
    mermaid.run();
  }
});
