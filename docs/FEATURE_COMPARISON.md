# Feature comparison

Sources: public READMEs of TC120 (TicNet) and TC142 (NetEasy), and the code in this repository. Competitor source was not copied.

| Capability | TC411 before | TC120 | TC142 | This desktop branch |
|---|---|---|---|---|
| Four-check evidence rules | Yes, web + agent | Their own rules | Simpler checks | Same TC411 engine, not a second copy |
| Inconclusive when evidence conflicts | Yes | Not the same contract | Partial | Kept |
| Resolved only after a clean retest | Yes | Not the same contract | No live repair | Kept |
| DNS save / rollback / allowlist | Yes, Python agent | Not described as this loop | No | Desktop calls the same controller, off by default |
| PySide6 desktop shell | No | Yes | Tkinter | Yes |
| SQLite history and incidents | No | Yes | No | Yes |
| Scheduled monitoring | No | Yes | No | Yes, off by default; skips the download |
| Simulation lab | 12 stored scenarios | Their lab | Demo scenarios | Same 12 scenarios, cannot touch the machine |
| TCP targets 1.1.1.1 / 8.8.8.8 / 9.9.9.9 | No | Yes | Independent TCP | Yes, shown beside the verdict, not a new cause by itself |
| PDF / CSV / JSON / Markdown | JSON and text on the website | Markdown, JSON, CSV | PDF | All four plus PDF |
| Privacy masking on export | No | Yes | No | Yes |
| Live NIC graph and upload speed | No | Yes | No | Not implemented. Not faked |
| Verified Windows exe | No | They publish one | Prototype | Spec and script only. Not built on Windows here |
