# Mapping paper evidence to the package

Use these distinctions to interpret the paper. They are extraction guidance,
not a requirement that every paper contain every phase.

| Phase command | Evidence to look for |
| --- | --- |
| `\ProblemIdentification{...}` | The practical or research problem, affected stakeholders, and why solving it matters. |
| `\ObjectivesOfTheSolution{...}` | Desired capabilities, requirements, success criteria, or constraints derived for the solution. |
| `\DesignAndDevelopment{...}` | Construction or refinement of an artifact: a model, method, framework, prototype, system, or tool. |
| `\Demonstration{...}` | Application of the artifact to a case, scenario, workload, or example showing how it is used. |
| `\Evaluation{...}` | Assessment against objectives, using measurements, experiments, comparisons, workshops, or justified qualitative findings. |
| `\Communication{...}` | Reported dissemination of the contribution: publication, documentation, released code, or other sharing supported by the paper. |

## Demonstration versus evaluation

Applying a prototype to a workload demonstrates its use. Measuring whether that
application meets performance or usability objectives evaluates it. The same
study can support both phases; summarize the different roles rather than
duplicating the same text or inventing a second study. An implementation alone
does not establish evaluation, and calling an activity a workshop does not by
itself establish what was assessed.

## Iterations and chronology

Evidence for an iteration includes a reported redesign after evaluation,
successive prototype versions with distinct research activities, or an explicit
sequence of cycles. Multiple workloads, experiments, paper sections, or future
improvement proposals do not alone demonstrate separate iterations.

Record what changes between cycles and what caused the return to development,
objectives, or another phase. Repeat only the phases supported for that cycle.
The package joins each row's last non-communication phase to the next row's
first phase. If that arrow would assert a chronology the paper does not support,
describe the ambiguity and resolve it before representing it as established.

Within a row the package connects present phases in methodology order. More
complex parallel or branching activity may require multiple diagrams or an
explicitly requested extension; do not silently force it into a false sequence.

## Entry points

The optional input denotes the starting approach, not generic supplementary text:

- Problem-centered: a motivating problem starts the research.
- Objective-centered: solution objectives initiate the work.
- Design/development-centered: an existing artifact or development effort is the starting point.
- Observing a solution: observation of a solution initiates the investigation.

Use the optional argument on the corresponding phase only when the paper
supports that interpretation. Distinguish an explicit entry point from an
inference in the evidence mapping. Gray empty-input placeholders are visual
scaffolding, not evidence that the paper reports those approaches.

## Evidence mapping

A useful mapping has these columns:

| Iteration | Phase | Diagram summary | Paper location | Support / uncertainty |
| --- | --- | --- | --- | --- |
| 1 | Evaluation | Compare prototype latency with the baseline | Section 5.2, p. 8 | Explicit; quantitative comparison |

This row illustrates the format; it is not evidence to reuse. For a missing
phase, record “Not described” and omit its activity from the diagram. For
inferences, explain the inference and its supporting location. Never fabricate
page numbers, quotations, results, or artifacts.
