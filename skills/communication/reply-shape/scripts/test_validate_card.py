"""Run: python3 -m unittest discover -s reply-shape/scripts"""
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE.parent / "ui"
SCRIPT = HERE / "validate-card.py"
spec = importlib.util.spec_from_file_location("validate_card", SCRIPT)
card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(card)


def problems(*blocks):
    return card.check({"ui": list(blocks)})


class Examples(unittest.TestCase):
    def test_examples_are_valid(self):
        for path in sorted((UI / "examples").glob("*.json")):
            with self.subTest(path.name):
                self.assertEqual(card.check(json.loads(path.read_text())), [])

    def test_catalog_example_holds_every_block_type(self):
        schema = json.loads((UI / "catalog.schema.json").read_text())
        types = {schema["$defs"][b["$ref"].rsplit("/", 1)[1]]["required"][0] for b in schema["$defs"]["block"]["oneOf"]}
        shown = {next(iter(b)) for b in json.loads((UI / "examples" / "catalog.json").read_text())["ui"]}
        self.assertEqual(shown, types)

    def test_renderer_draws_and_checks_every_block_type(self):
        schema = json.loads((UI / "catalog.schema.json").read_text())
        types = [schema["$defs"][b["$ref"].rsplit("/", 1)[1]]["required"][0] for b in schema["$defs"]["block"]["oneOf"]]
        js = (UI / "reply.js").read_text()
        draw = js[js.index("const DRAW"):]
        for name in types:
            with self.subTest(name):
                self.assertRegex(draw, rf"\n    {name}(\(b\)|: \(b\))")
                self.assertTrue(name == "checks" or re.search(rf"\n    {name}: \{{", js), f"SPEC lacks {name}")


class Problems(unittest.TestCase):
    def test_reports_each_field_problem_with_its_path(self):
        self.assertEqual(problems({"outcome": {"status": "ok", "text": "x"}}),
                         ['$.ui[0].outcome.status: "ok" is not one of done, risk, blocked, working'])
        self.assertEqual(problems({"change": {"pr": "7", "state": "merged"}}),
                         ['$.ui[0].change.pr: expected integer, got "7"'])
        self.assertEqual(problems({"delta": {"label": "a", "now": "1", "was": "2", "bars": [["x", True]]}}),
                         ["$.ui[0].delta.bars[0][1]: expected number, got true"])

    def test_unknown_block_and_unknown_field(self):
        self.assertIn("unknown block 'bogus'", problems({"bogus": {}})[0])
        self.assertEqual(problems({"flow": {"steps": ["a", "b"], "color": "red"}}), ["$.ui[0].flow: unknown field 'color'"])

    def test_two_keys_is_not_a_block(self):
        self.assertEqual(problems({"outcome": {"status": "done", "text": "x"}, "flow": {"steps": ["a", "b"]}}),
                         ["$.ui[0]: unknown field 'flow'"])

    def test_limits(self):
        self.assertEqual(card.check({"ui": []}), ["$.ui: fewer than 1 items"])
        rows = [["r"]] * 7
        self.assertEqual(problems({"table": {"columns": ["c"], "rows": rows}}), ["$.ui[0].table.rows: more than 6 items"])
        self.assertEqual(problems({"decision": {"options": [{"key": "A", "text": "x"}]}}),
                         ['$.ui[0].decision.options[0].key: "A" doesn\'t match ^[a-z]$'])

    def test_indexes_keys_and_picks_must_fit_their_lists(self):
        self.assertEqual(problems({"table": {"columns": ["N"], "rows": [["A"]], "pick": 1}}),
                         ["$.ui[0].table.pick: no row 1; rows count from 0"])
        self.assertEqual(problems({"flow": {"steps": ["a", "b"], "mark": 2}}),
                         ["$.ui[0].flow.mark: no step 2; steps count from 0"])
        options = [{"key": "a", "text": "x", "rec": True}, {"key": "a", "text": "y", "rec": True}]
        self.assertEqual(problems({"decision": {"options": options}}),
                         ["$.ui[0].decision.options: each key once, got a, a", "$.ui[0].decision.options: at most one rec"])

    def test_a_pattern_end_anchor_ends_the_string_as_in_javascript(self):
        self.assertEqual(problems({"change": {"pr": 1, "state": "open", "sha": "3fa9c01\n"}}),
                         ['$.ui[0].change.sha: "3fa9c01\\n" doesn\'t match ^[0-9a-f]{7,40}$'])
        self.assertEqual(len(problems({"decision": {"options": [{"key": "a\n", "text": "x"}]}})), 1)
        self.assertEqual(problems({"change": {"pr": 1, "state": "open", "sha": "3fa9c01"}},
                                  {"decision": {"options": [{"key": "a", "text": "x"}]}}), [])

    def test_a_ui_that_isnt_a_list_is_named(self):
        for value, shown in ((None, "null"), (3, "3"), (True, "true")):
            with self.subTest(value):
                self.assertEqual(card.check({"ui": value}), [f"$.ui: expected array, got {shown}"])

    def test_reference_problems_show_beside_schema_problems(self):
        found = problems({"outcome": {"status": "meh", "text": "x"}},
                         {"table": {"columns": ["N"], "rows": [["A"]], "pick": 1}})
        self.assertEqual(found, ['$.ui[0].outcome.status: "meh" is not one of done, risk, blocked, working',
                                 "$.ui[1].table.pick: no row 1; rows count from 0"])

    def test_an_unsupported_schema_keyword_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "unsupported schema keyword 'format'"):
            card.check("x", {"type": "string", "format": "uri"})


class Cli(unittest.TestCase):
    def run_cli(self, text):
        return subprocess.run([sys.executable, str(SCRIPT), "-"], input=text, capture_output=True, text=True)

    def test_reads_the_payload_out_of_an_html_page(self):
        page = '<script src="x.js"></script><script type="application/json" id="ui">{"ui":[{"flow":{"steps":["a","b"]}}]}</script>'
        done = self.run_cli(page)
        self.assertEqual((done.returncode, done.stdout), (0, "ok: 1 blocks\n"))

    def test_skips_the_tag_an_inlined_renderer_names_in_its_comment(self):
        page = f"<script>{(UI / 'reply.js').read_text()}</script>" \
               '<script type="application/json" id="ui">{"ui":[{"flow":{"steps":["a","b"]}}]}</script>'
        self.assertEqual(self.run_cli(page).stdout, "ok: 1 blocks\n")

    def test_exits_1_on_a_problem_or_bad_json(self):
        self.assertEqual(self.run_cli('{"ui":[{"x":1}]}').returncode, 1)
        bad = self.run_cli("{nope")
        self.assertEqual(bad.returncode, 1)
        self.assertTrue(bad.stdout.startswith("$: not JSON"))


if __name__ == "__main__":
    unittest.main()
