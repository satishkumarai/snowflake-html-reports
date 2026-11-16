# Limitations (Public Preview, as documented Nov 2026)
- Snapshot only, with no automatic or scheduled refresh.
- No scheduled delivery to Slack, Teams or email.
- Strict CSP: no external scripts, APIs, fonts or remote images. Only vendored libraries load (Chart.js, Plotly cartesian, D3, Vega/Vega-Lite/Vega-Embed, Mermaid, Three.js, Marked, highlight.js, KaTeX).
- Inline event handlers are blocked.
- Per-account artifact file-size limit (the value isn't documented here, so check your account).
- No per-viewer row/column security on embedded data.
- Recipients must be in the same Snowflake account.
