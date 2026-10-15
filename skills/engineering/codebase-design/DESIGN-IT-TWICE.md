# Design it twice

Use this pattern for a consequential module interface with materially different viable shapes. In an existing `/pstack-architect` or `/pstack-arena` run, contribute the vocabulary and constraints to that run rather than launching a second competition.

1. Frame caller needs, invariants, accepted domain language, and dependency categories from [DEEPENING.md](DEEPENING.md). Include realistic usage and the complexity an interface must hide. Complete when each candidate can answer the same design question.
2. Invoke /pstack-arena once with candidate constraints such as the smallest interface, the common caller's simplest path, or justified adapter flexibility. Scale candidate count and concurrency to the decision. Supply the resolved vocabulary, project artifacts, exact scope, and expected interface/usage/hidden-complexity/adapter/tradeoff report. Complete when useful independent candidates have evidence or the loss of independence is disclosed.
3. Compare depth, locality, seam placement, and caller burden. Recommend one or a concrete synthesis, preserve any requested interface gate, and invoke /domain-modeling for accepted domain changes and qualifying decisions. Complete when the chosen interface and its durable rationale agree.
