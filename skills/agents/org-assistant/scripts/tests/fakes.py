"""Fake `probe.ts`, `gh`, and `t3` for the scan's tests. Each serves `world.json` in the
folder $FAKE names, shaped like the responses recorded from the live tools on 26 Nov 2026,
and logs every call, so a test can assert what a source and a thread received. Every value
in the fixtures is invented: no real ticket text, message text, or person."""
import json
import os
import sys

FAKE = os.environ["FAKE"]


def world() -> dict:
    with open(os.path.join(FAKE, "world.json")) as handle:
        return json.load(handle)


def log(name: str, entry) -> None:
    with open(os.path.join(FAKE, f"{name}.jsonl"), "a") as out:
        out.write(json.dumps(entry) + "\n")


def _text(payload) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def _slack_page(messages: list[dict], limit: int) -> dict:
    """A search page in the Slack tool's Markdown, as recorded, with the text left out."""
    shown = messages[:limit]
    lines = ["# Search Results for: ", "", f"## Messages ({len(messages)} results)"]
    for n, m in enumerate(shown, 1):
        label = "DM" if m["channel"].startswith("D") else f"#{m.get('name', 'channel')}"
        thread = f"?thread_ts={m['thread']}&cid={m['channel']}" if m.get("thread") else ""
        lines += [f"### Result {n} of {len(messages)}", f"Channel: {label} (ID: {m['channel']})",
                  f"From: Invented Person <invented@example.com> (ID: {m['from']}) ", "Time: 2026-11-26 10:00:00 CET",
                  f"Message_ts: {m['ts']}",
                  f"Permalink: [link](https://example.slack.com/archives/{m['channel']}/p{m['ts'].replace('.', '')}{thread})",
                  "Text: (left out of the fixture)", "---"]
    return {"results": "\n".join(lines), "pagination_info": ""}


def _slack(args: dict, slack: dict) -> dict:
    after = float(args.get("after", 0))
    me = slack["me"]
    messages = [m for m in slack.get("messages", []) if float(m["ts"]) >= after]
    filters, keywords = args.get("filters", ""), args.get("keywords", [])
    if filters == "to:me":
        picked = [m for m in messages if m["channel"].startswith("D") and m["from"] != me]
    elif keywords == [f"<@{me}>"]:
        picked = [m for m in messages if me in m.get("mentions", [])]
    elif filters == f"from:<@{me}>":
        picked = [m for m in messages if m["from"] == me]
    elif filters.startswith("in:<#"):
        channels = {part[5:].rstrip(">") for part in filters.split()}
        picked = [m for m in messages if m["channel"] in channels]
    else:
        picked = []
    picked.sort(key=lambda m: -float(m["ts"]))
    return _slack_page(picked, int(args.get("limit", 20)))


def _linear(path: str, args: dict, linear: dict):
    if path.endswith("get_notifications"):
        return {"notifications": sorted(linear.get("notifications", []), key=lambda n: n["createdAt"], reverse=True),
                "hasNextPage": False}
    if path.endswith("list_issues"):
        if args.get("assignee") == "me":
            return {"issues": linear.get("mine", []), "hasNextPage": False}
        team = linear.get("team", {}).get(args.get("team"), [])
        return {"issues": [i for i in team if i["updatedAt"] > args.get("updatedAt", "")], "hasNextPage": False}
    if path.endswith("get_issue"):
        return linear.get("issues", {}).get(args["id"], {"id": args["id"], "relations": {"blockedBy": []},
                                                         "stateHistory": []})
    raise KeyError(path)


def probe() -> None:
    body = json.loads(sys.argv[2])
    state = world()
    values = []
    for call in body["calls"]:
        path, args = call["path"], call["input"]["input"]
        log("probe", {"path": path, "input": args})
        app = path.split(".")[1]
        failure = state.get("fail", {}).get(app)
        if failure == "auth":
            values.append({"path": path, "ok": False, "error": {"kind": "ToolFailure",
                                                                "message": "UNAUTHORIZED: sign in again"}})
            continue
        if failure:
            values.append({"path": path, "ok": False, "error": {"kind": "ToolFailure", "message": failure}})
            continue
        payload = _slack(args, state["slack"]) if app == "slack" else _linear(path, args, state["linear"])
        values.append({"path": path, "ok": True, "value": _text(payload)})
    print("executor_client: fake mapping")
    print(json.dumps({"tool": "call", "result": {"structuredContent": {"execution": {"value": values}}}}))


def gh() -> None:
    args = sys.argv[1:]
    log("gh", args)
    state = world()
    if state.get("fail", {}).get("github"):
        sys.exit("HTTP 401: Bad credentials")
    repo = state["github"][args[args.index("-R") + 1]]
    if args[:2] == ["release", "list"]:
        print(json.dumps(repo.get("releases", [])))
    elif args[:2] == ["issue", "list"]:
        print(json.dumps(repo.get("issues", [])))
    elif "--author" in args:
        print(json.dumps(repo.get("mine", [])))
    elif "--search" in args:
        print(json.dumps(repo.get("requested", [])))
    else:
        print(json.dumps(repo.get("open", [])))


def t3() -> None:
    args = sys.argv[1:]
    state = world()["t3"]
    if args[:2] == ["thread", "list"]:
        print(json.dumps(state.get("threads", [])))
    elif args[:2] == ["thread", "show"]:
        thread = state["assistant"]
        print(json.dumps({"thread": thread, "messages": [{"role": "assistant", "text": thread.get("last", "")}]}))
    elif args[:2] == ["thread", "send"]:
        log("sent", {"to": args[2], "message": sys.stdin.read()})
        sys.exit(int(state.get("send_code", 0)))


if __name__ == "__main__":
    {"probe": probe, "gh": gh, "t3": t3}[sys.argv.pop(1)]()
