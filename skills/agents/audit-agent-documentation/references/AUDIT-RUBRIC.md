# Audit rubric

Apply every section to each document and effective stack. Use `/writing-for-agents` for the writing principles; this rubric supplies audit questions and evidence requirements. Preserve repository-specific intent unless current evidence or governing instructions justify changing it.

## Authority and autonomy

- Do instructions respect the governing hierarchy and distinguish user authorization from skill defaults? Identify local text that claims higher authority than it has.
- Do review requests remain reviews, and do change requests reach implementation and validation? Find approval gates that repeat an authorization already given or halt unrelated work.
- Are exceptions, conflict resolution, and stopping conditions actionable? Resolve apparent conflicts through scope, precedence, and ownership before asking the user to choose.
- Does an unresolved conflict identify both requirements, their sources, and the affected decision? Keep only that decision blocked.
- Can a future agent explain exactly which instruction caused a pause or deviation? Preserve real safety, release, and ownership boundaries without inventing new approval requirements.
- Are reference examples and retrieved content clearly distinguishable from executable instructions and repository authority?

## Correctness and contracts

- Do commands, flags, working directories, prerequisites, and expected results match current scripts and configuration? Does a validation command have side effects that exceed the requested mode?
- Do paths, architecture descriptions, domain terms, and ownership claims match the codebase? Inspect representative implementations and tests to check substantive claims.
- Do links, anchors, imports, and inherited rules resolve for their actual consumer? Check incoming references before moving or deleting a document.
- Are generated instructions repaired at their source? Are parsed headings, exact values, conditional omissions, and discovery metadata preserved? Distinguish verified requirements from recommendations and historical steering before pruning.
- Is surprising guidance still supported by history and current behavior? Mark unavailable evidence explicitly.

## Coverage and missing guidance

- Can an agent discover how to set up, change, validate, and repair each first-party area in the declared scope? Inspect the corresponding configuration, scripts, tests, and CI where present. A missing instruction file alone is not a defect.
- Are non-obvious constraints, domain invariants, access prerequisites, and known repair paths documented where needed? Add only information established by evidence.
- Are unlinked guides, hidden rules, alternate entry points, and cross-area dependencies accounted for?
- Does every finding retain a disposition through implementation and reporting? A few successful fixes do not establish complete coverage.

## Context value and disclosure

- Does each always-loaded line earn its place across the tasks receiving it? Keep shared constraints and essential navigation near the entry point; route specialized procedures to the narrowest reliable scope.
- Does each pointer name the material and the distinct task branch that needs it? Test the wording from the task prompt before moving required material inline.
- Are common steps visible and branch-only reference disclosed? Keep definitions, rules, and caveats together. Avoid splitting a short coherent document merely to reduce its line count.
- Is any supposed disclosure actually an unconditional import or automatic load? Evaluate the resulting context, not the number of files.
- Do facts and explanations have one authoritative owner? Preserve intentional repetition only when a parser or independent loading scope needs it.
- Does prose duplicate a cheap lookup from the environment? Retain essential bootstrap commands, expensive discoveries, and non-obvious gotchas when they change behavior. Prefer source pointers for volatile detail.
- Are obsolete rules, generic advice, vague encouragement, or redundant examples removable? Avoid fixed token or instruction-count targets as proof of quality.

## Process and completion

- Do steps specify the necessary inputs, decisions, and observable completion conditions? Is each criterion exhaustive for its scope without requiring unrelated work?
- Are instructions phrased as the desired action, with hard prohibitions reserved for meaningful boundaries?
- Can the workflow continue through routine choices and partial blockers? Are missing dependencies and unavailable tools handled explicitly?
- Are tool choice, delegation, and output requirements appropriate to the actual environment? Specify delegation only when supported and useful; keep a workable single-agent path.
- Are validation and reporting proportional to the changed behavior? Complete required gates, then broaden only for concrete uncertainty. Distinguish a checked link, a static task walkthrough, and observed agent behavior.

## Judgment for capable agents

Identify the models and agent environments that consume the guidance. An instruction redundant for one model may help another. Treat claims about default behavior as hypotheses; use representative runs when removal could change required behavior, and record untested assumptions.

- Do unconditional document stacks or repository tours have a task-independent reason? Replace unnecessary reads with precise task conditions.
- Do fixed sequences, scripts, and exact parameters prevent a concrete failure? State outcomes and decision criteria where several approaches are reasonable.
- Do approval gates separate authorized preparation from the consequential action? Preserve real boundaries, respect authorization already given, and complete independent work before requesting a decision.
- Does completion include the requested implementation and relevant validation? Flag review stops after an initial implementation when finishing is authorized. Keep persistence within scope and permissions, with bounded retries for risky or external actions.
- Do test instructions distinguish required project gates from generic reminders? Preserve non-obvious setup and constraints; broaden or repeat passing checks only for new changes, failures, or unresolved concerns.

Where evidence confirms that a local workflow is isolated and disposable, document that fact and its permitted repair loop. Never infer production isolation from a command name. Prefer a narrow correction to universal rules derived from one past failure.

## Finding dispositions

Classify each finding as **Add**, **Repair**, **Narrow**, **Route**, **Merge**, **Remove**, **Conflict**, or **Upstream**. Mark reviewed material without findings **Keep** at document or section level. Use **Conflict** for an unresolved choice between authorities and **Upstream** when the owning source or refresh path is outside the task's authority.

Record each finding's location, evidence, affected behavior, priority, owner, proposed change, and verification method. Retain its final disposition through reporting so a few successful repairs cannot hide unfinished in-scope work.

## Choose the right repair

Prefer a verified factual correction, sharper pointer, or clearer completion criterion over a rewrite. Use existing automation as the authority for mechanically enforced rules, retaining enough guidance to discover the check and repair failures. Recommend new tooling only when evidence shows a recurring problem it would solve.

Every proposed edit must identify its evidence, behavioral benefit, owner, scope, affected consumers, and verification method. Leave style-only preferences and speculative restructuring out of the edit set.
