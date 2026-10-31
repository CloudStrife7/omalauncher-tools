#!/usr/bin/env python
"""bake_milestones.py - write a project site's data/milestones.json from GitHub.

The master copy lives in `!index/shared/templates/project-site/`. Each project
site gets a copy (install.py); edit the master, then re-install. Stdlib + `gh`.

Why baked: most project repos are private, so the browser cannot read their
issues. The numbers are computed at publish time, never typed by hand.

What it reads, per open milestone of the repo:
  - open/closed issue counts (the bar = closed / all),
  - the milestone's `Proof: ...` issue (closed = PROVEN),
  - issues whose body has a `## Status` block (the item rows on the page),
  - WORTH.md (the worth line) and the last commit date (tool day counter).

    python scripts/bake_milestones.py --repo CloudStrife7/RetroRoads --out site/data
"""
import argparse
import base64
import datetime
import json
import re
import subprocess
import sys

ROW_RE = re.compile(r"^-\s+\[([ xX])\]\s+(.*)$")
OWNER_RE = re.compile(r"\(([^)]+)\)\s*$")
PART_RE = re.compile(r"[-–—]\s*PART\b|\bPART\b", re.I)
VERDICT_RE = re.compile(r"\*\*Verdict:\s*([^*.]+)", re.I)
YOU_LABEL = re.compile(r"\byou\b", re.I)
TOP_ITEMS = 5


def parse_status(body):
    """Rows of the `## Status` block. Same rules as !index/brain/gates.py parse_gate:
    `- [x]` YES, `- [ ] ... PART` PART (counts half), `- [ ]` NO, `(owner)` at the end."""
    rows, note, inside = [], "", False
    for line in (body or "").splitlines():
        if re.match(r"^##\s+Status\s*$", line, re.I):
            inside = True
            continue
        if not inside:
            continue
        if line.startswith("## ") or line.startswith("---") or line.startswith("<details"):
            break
        if line.startswith(">") and not note:
            note = line.lstrip("> ").strip()
        m = ROW_RE.match(line)
        if not m:
            continue
        raw = m.group(2)
        om = OWNER_RE.search(raw)
        owner = om.group(1) if om else "me"
        part = bool(PART_RE.search(raw))
        name = PART_RE.sub("", OWNER_RE.sub("", raw)).replace("**", "").strip(" —–-").strip()
        state = "YES" if m.group(1).lower() == "x" else ("PART" if part else "NO")
        rows.append({"name": name, "state": state, "owner": owner})
    done = sum(1 if r["state"] == "YES" else 0.5 if r["state"] == "PART" else 0 for r in rows)
    return {"rows": rows, "done": done, "total": len(rows), "note": note}


def milestone_order(title):
    """M1 < M2 < ... < anything else < LATER."""
    m = re.match(r"M(\d+)", title or "")
    if m:
        return (0, int(m.group(1)), title)
    return (2, 0, title) if (title or "").upper().startswith("LATER") else (1, 0, title)


def parse_worth(text):
    """'2.8 GO' style line from a WORTH.md, or '' when it has no number."""
    if not text:
        return ""
    line = next((l for l in text.splitlines() if re.search(r"Worth\s*=", l, re.I)), "")
    nums = sorted({float(n) for n in re.findall(r"\d+\.\d+", line)})
    score = "" if not nums else f"{nums[0]:g}" if len(nums) == 1 else f"{nums[0]:g}–{nums[-1]:g}"
    verdict = VERDICT_RE.search(text)
    parts = [score, verdict.group(1).split()[0] if verdict else ""]
    return " ".join(p for p in parts if p)


def is_you(issue):
    return any(YOU_LABEL.search(l.get("name", "")) for l in issue.get("labels", []))


def build(repo, milestones, issues, worth_text, last_commit, today):
    """Pure: GitHub data in, the page's JSON out."""
    out_ms, current = [], None
    for m in sorted((m for m in milestones if m.get("state") == "open"), key=lambda m: milestone_order(m["title"])):
        mine = [i for i in issues if (i.get("milestone") or {}).get("number") == m["number"]]
        proof = next((i for i in mine if i["title"].lower().startswith("proof:")), None)
        items = []
        for i in mine:
            if i is proof or i.get("state") != "open":
                continue
            s = parse_status(i.get("body"))
            if s["total"]:
                items.append({"number": i["number"], "title": i["title"], "url": i.get("html_url", ""),
                              "done": s["done"], "total": s["total"], "rows": s["rows"], "note": s["note"]})
        items.sort(key=lambda x: x["number"])
        later = m["title"].upper().startswith("LATER")
        open_n, closed_n = m.get("open_issues", 0), m.get("closed_issues", 0)
        if proof:  # the Proof issue is the badge, not a work item: keep it out of the bar
            if proof.get("state") == "closed":
                closed_n = max(0, closed_n - 1)
            else:
                open_n = max(0, open_n - 1)
        entry = {
            "title": m["title"], "number": m["number"], "url": m.get("html_url", ""),
            "description": re.split(r"\n-{3,}\n", m.get("description") or "")[0].strip(), "later": later,
            "open": open_n, "closed": closed_n,
            "proof": ({"title": proof["title"], "number": proof["number"], "url": proof.get("html_url", ""),
                       "proven": proof.get("state") == "closed"} if proof else None),
            "items": items[:TOP_ITEMS], "more_items": max(0, len(items) - TOP_ITEMS),
            "you": sum(1 for i in mine if i.get("state") == "open" and is_you(i)),
        }
        out_ms.append(entry)
        if current is None and not later and not (entry["proof"] and entry["proof"]["proven"]):
            current = entry["title"]
    cur = next((m for m in out_ms if m["title"] == current), None)
    nxt = ""
    if cur:
        open_in = sorted((i for i in issues if (i.get("milestone") or {}).get("number") == cur["number"]
                          and i.get("state") == "open" and not i["title"].lower().startswith("proof:")),
                         key=lambda i: (not is_you(i), i["number"]))
        if open_in:
            nxt = f"#{open_in[0]['number']} {open_in[0]['title']}"
    days = (today - last_commit).days if last_commit else None
    return {"repo": repo, "current": current, "next": nxt, "worth": parse_worth(worth_text),
            "days_since_commit": days, "milestones": out_ms}


def gh_json(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()[:300]}")
    return json.loads(r.stdout or "null")


def gh_paged(path):
    out, page = [], 1
    while True:
        chunk = gh_json("api", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        out += chunk
        if len(chunk) < 100:
            return out
        page += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", default="site/data")
    a = ap.parse_args()
    ms = gh_paged(f"repos/{a.repo}/milestones?state=all")
    issues = [i for i in gh_paged(f"repos/{a.repo}/issues?state=all&milestone=*") if "pull_request" not in i]
    r = subprocess.run(["gh", "api", f"repos/{a.repo}/contents/WORTH.md"], capture_output=True, text=True, encoding="utf-8")
    worth = base64.b64decode(json.loads(r.stdout)["content"]).decode("utf-8") if r.returncode == 0 else ""
    c = gh_json("api", f"repos/{a.repo}/commits?per_page=1")
    last = datetime.date.fromisoformat(c[0]["commit"]["committer"]["date"][:10]) if c else None
    today = datetime.date.today()
    data = build(a.repo, ms, issues, worth, last, today)
    data["generated"] = today.strftime("%m-%d-%Y")
    import pathlib
    p = pathlib.Path(a.out)
    p.mkdir(parents=True, exist_ok=True)
    (p / "milestones.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.repo}: {len(data['milestones'])} milestones, current {data['current']!r} -> {p / 'milestones.json'}")


if __name__ == "__main__":
    main()
