---
name: paper-to-dsr
description: Create or revise Design Science Research methodology diagrams from research papers using the dsrm LaTeX package, including evidence-based phase summaries, iterations, compiled PDFs, and source mappings.
license: "MIT for the skill; bundled dsrm.sty retains its LPPL license"
metadata:
  version: "0.1.0"
---

# Paper to DSR

Turn a paper's account of its research process into a DSR diagram. Use the
paper as evidence, and the bundled `dsrm.sty` as the rendering interface.

## Extract the research process

Read the supplied paper, preferably its LaTeX sources or a searchable PDF.
If the paper is unavailable or essential pages are unreadable, request the
missing material; do not reconstruct its research process from its title alone.

Read [phase-mapping.md](references/phase-mapping.md) when assigning activities
to phases or deciding whether the paper supports iterations. Reconstruct the
sequence of research activities rather than treating section order as chronology.

Keep an evidence mapping with the iteration, phase, proposed diagram text,
source section/page or source-file location, and whether support is explicit or
inferred. Use short excerpts only when needed to resolve an ambiguity. Record
missing phases and uncertain sequencing; do not fill them with typical DSR
activities. Distinguish completed activities from proposed future work.

When uncertainty materially changes the diagram, ask a focused question. Continue
with supported content and label any unresolved interpretation in the evidence
mapping. Do not require approval of an unambiguous extraction before rendering.

## Generate the diagram

Choose the matching template:

- [single-pass.tex](assets/single-pass.tex): one research sequence, using `\DSR`.
- [iterations.tex](assets/iterations.tex): repeated cycles supported by the paper,
  using `\DSRIterations` and `\Iteration` rows.

Copy the template and [dsrm.sty](assets/dsrm.sty) into the output directory.
Keep [LICENSE-LPPL](assets/LICENSE-LPPL) with the package when distributing it.
Use an existing project copy of the package if the user has selected it; check
that it supports the commands needed rather than silently replacing it.

Replace example content with concise summaries of the paper. Escape LaTeX
special characters in extracted prose; preserve deliberate LaTeX formatting.
Omit unsupported phases and explain omissions in the evidence mapping. A diagram
does not establish that the authors followed DSR unless the paper supports that.

The rendering API has these constraints:

- Use `\DSR`, not `\SDR`. All six phase commands accept a required body.
- The first four phases accept an optional input: `[Entry-point text]`.
  Supply it only when supported. Empty inputs are hidden by default;
  `\usepackage[showemptyinputs]{dsrm}` shows gray placeholders and dashed arrows.
- In iterations, list phases in methodology order, at most once per row. Each
  row requires at least one phase before communication. Omit phases that are not
  repeated; their columns remain empty.
- Include communication at most once in an iterative diagram. The final
  iteration connects to it even when it is displayed on an earlier row.
- Heights are automatic. Phase bodies are typeset twice for measurement and
  drawing, so avoid counter increments, labels, or other side effects in them.

## Render and deliver

Compile in the output directory with:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape diagram.tex
```

The templates need `pdflatex`, TikZ, and the `standalone` class. If required
tools are unavailable, report that rendering is incomplete and deliver the
source and evidence mapping; do not claim a verified PDF.

Inspect the rendered page when a PDF viewer or rasterizer is available. Check
text containment, legibility at the intended paper width, arrow routing, row
clearance, and whether the depicted sequence agrees with the extraction. Adjust
wording without changing the evidence. If visual inspection is unavailable,
state that limitation separately from successful compilation.

Deliver `diagram.tex`, the accompanying package, the rendered PDF when available,
and the evidence mapping with omissions and unresolved questions. When revising
an existing diagram, preserve the user's terminology and requested scope.

## Licensing

The skill instructions, references, agent metadata, and LaTeX templates are
licensed under [MIT](LICENSE). The bundled `assets/dsrm.sty` retains its existing
LPPL terms, provided in [assets/LICENSE-LPPL](assets/LICENSE-LPPL) and its header.
The repository's asset-sync helper is also MIT-licensed. The skill's MIT license
does not replace the package's license.
