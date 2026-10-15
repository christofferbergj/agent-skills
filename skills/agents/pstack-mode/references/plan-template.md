# Multi-PR plan template

Fill the template from repository evidence. Choose the number of live lanes from required surfaces and risks, not a fixed fan-out. Name a concrete reason when a check is not applicable. The checker validates structure and evidence contracts; it cannot establish that a chosen scenario is sufficient.

```markdown
# <Program> plan

<The behavior that changes, for whom, and the intended end state.>

## How to read this

One box is one unit of work and names the evidence. Check a box only when its evidence exists. Execution follows the matching playbooks/ owner in the installed Pstack mode skill.

Verification covers applicable unit, live, and performance checks; every omitted check names a reason.

## Program checklist

### Arm the program

- [ ] Base ref. <Resolve the actual target branch and record its revision.>
- [ ] Audit cadence. <Use an available native wake mechanism if authorized, or record session-bound checkpoints and a durable handoff.>
- [ ] Record the done predicate, budget, scope, and user gates.

### Spawn owners

- [ ] <Each PR owner, dependency, isolated output, and permitted lifecycle.>

### PR mechanics

- [ ] Use repository branch and commit conventions and draft PRs by default.
- [ ] Run relevant checks and inspect the final diff before pushing.

### Verdict and merge

- [ ] Obtain independent verdicts on actual heads. Merge only under existing explicit authority.

### Boot recipe

- [ ] <Launch, ready check, controlled input, evidence location, and cleanup for the scoped surfaces.>

## <Task> (<PR id>)

**Depends on.** <PR ids, or None.>

**Files.**

- [ ] <Concrete file boundary.>

**Build.**

- [ ] <One verifiable behavior change.>

**You see.**

- [ ] <Observable end state.>

**Verify, unit.** Verification covers applicable unit, live, and performance checks; every omitted check names a reason.

- [ ] <Test and command, or Not applicable. followed by its concrete reason.>

**Verify, live.** Verification covers applicable unit, live, and performance checks; every omitted check names a reason. <N> lanes at the PR head.

- [ ] Lane 1. <Scenario, including baseline comparison when meaningful.> Save `<evidence-path>`. Pass when <predicate>.

**Verify, perf.** Verification covers applicable unit, live, and performance checks; every omitted check names a reason.

- [ ] Metric. <Comparable work and user-visible completion state.>
- [ ] Probe. <Method and equivalent workloads.>
- [ ] Baseline. <Reference measurement taken before the change.>
- [ ] Rule. <Threshold that fails, or an absolute budget when a ratio is invalid.>

**Review gate.** <Requested review, or None. followed by the reason.>

- [ ] <When gated, show screenshots, video where useful, or equivalent artifacts to the operator.>

**Merge.**

- [ ] <Explicit authority and independent verdict, or stop at merge-ready.>

## Close the program

- [ ] Reconcile all units, evidence, worker states, and outstanding gates.

## Appendix Prototype evidence

<Questions settled by experiments, artifacts, alternatives, risks, and unresolved gaps.>
```

For a genuinely inapplicable live check, replace its lane sentence and boxes with `Not applicable. <concrete reason>`. For inapplicable performance checks, replace the four performance boxes with one `Not applicable. <concrete reason>` box. A missing required environment is a blocked check, not an inapplicable one.
