/* Mermaid: dark theme (kitsune palette) + Material instant navigation. */
if (window.mermaid) {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "dark",
    themeVariables: {
      background: "hsl(220, 13%, 7%)",
      mainBkg: "hsl(220, 13%, 10%)",
      lineColor: "hsl(20, 95%, 55%)",
      textColor: "hsl(220, 9%, 96%)",
      primaryColor: "hsl(160, 84%, 50%)",
    },
  });
}

function runMermaid() {
  if (window.mermaid) {
    mermaid.run({ querySelector: ".mermaid" });
  }
}

if (typeof document$ !== "undefined" && document$.subscribe) {
  document$.subscribe(runMermaid);
} else {
  document.addEventListener("DOMContentLoaded", runMermaid);
}
