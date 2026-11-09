# UI cards

In T3 Code, a final reply's glance can be drawn as one `html_render` card: a small JSON payload that this skill's renderer, `ui/reply.js`, draws in the thread's theme. The user reads the card; the text under it keeps the headline, what the card can't hold, and the ending.

## When

Draw a card only on a final reply the user reads in a T3 Code thread that has `html_render`, when the glance fits the blocks below. Write plain Markdown for everything else:

- a progress line during the turn, or a ⏳ waiting reply;
- a delegated task's report to its coordinator;
- a host without `html_render`;
- a one-sentence answer; and
- a shape no block draws, such as code, a diff, or an interface with its call site.

The card is the turn's one picture. When the reply needs a screenshot, a chart, or a UI mockup, that is the picture instead, and the glance stays Markdown.

## Split

- **Card**: the headline as an `outcome` block, the shape when a block draws it, each note that belongs to a block, such as a PR's risk as that `change` block's `note` or a check as a `checks` item, and the ending's options as a `decision` block, `a` marked `rec`, in the ending's words.
- **Text under the card**, in this order: the headline line unchanged, since it is all the user sees when the card doesn't load; each note no block holds; the fold; then the `---` line and the /next-options ending unchanged, which other skills and the user's letter answers read from the text. Repeat nothing else the card says.

The card's words count toward the 60-word budget with the notes under it.

## Blocks

`ui/catalog.schema.json` defines the payload: `{"ui": [blocks]}`, at most 12 blocks, each an object with one key naming its type. Text fields hold at most 240 characters, and short fields, such as labels, values, and chips, at most 60. `ui/examples/catalog.json` shows every block, and `ui/examples/reference.json` a whole reply.

| Block      | Draws                                                    | Fields                                                                                                                               |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `outcome`  | the headline; each one opens a card for the blocks after | `status`: `done`, `risk`, `blocked`, or `working`, matching ✅ 🟡 🔴 ⏳; `text`                                                      |
| `delta`    | a measured before and after                              | `label`, `now`, `was`; optional `bars` of `[label, number]`                                                                          |
| `change`   | one PR                                                   | `pr`, `state`: `draft`, `open`, `fixing`, `blocked`, `merged`, or `closed`; optional `title`, `sha`, `checks`, `diff`, `note`, `url` |
| `decision` | options, the pick marked                                 | `options` of `{key, text, rec}`; optional `question`                                                                                 |
| `table`    | items compared on the same points, at most six rows      | `columns`, `rows`; optional `pick`, the index of the chosen row                                                                      |
| `checks`   | check results, worst first                               | items of `{status, text}`, `status` one of `fail`, `warn`, `wait`, `skip`, or `pass`                                                 |
| `flow`     | steps in order                                           | `steps`; optional `label` and `mark`, the index of the end state, by default the last step                                           |

## Call

Pass `html_render` exactly these two lines as its `html`, with the payload on one line:

```html
<script src="https://cdn.jsdelivr.net/gh/christofferbergj/agent-skills@be1999ffa11ba665be039b36befaf5cef5fdd044/skills/communication/reply-shape/ui/reply.js"></script>
<script type="application/json" id="ui">
  {
    "ui": [
      { "outcome": { "status": "done", "text": "Exports no longer time out" } },
      { "change": { "pr": 212, "state": "merged", "checks": ["typecheck", "unit 48/48"] } }
    ]
  }
</script>
```

Copy the URL as written: it pins the renderer to a commit of this library, so a card drawn today looks the same later. Give the call a short `title` and `height: 2000`, the tool's maximum; T3 Code fits the frame to the card, and a smaller height cuts it off on phones. A card taller than that holds too much: move detail to the fold.

No validator ships with the card, so check the payload against the schema before the call. A block the renderer can't read shows as plain text and logs a `reply.js:` console error; when `html_preview` is available, preview the card first and fix any such error.
