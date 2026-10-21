#!/usr/bin/env python
"""Build a Microsoft Forms survey from a JSON spec through an existing CDP browser.

  python build_form.py spec.json --account you@example.com [--port 9340] [--share anyone] [--dry-run]
  python build_form.py spec.json --only-share <form id>    # apply sharing to an existing form

`--share anyone` makes the form answerable by anonymous external users. Use it only after the user
approved external respondents. Without it the tenant default (organisation only) is kept.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

KINDS = {"text", "choice"}


def validate(spec):
    errors = []
    if not spec.get("title"):
        errors.append("title is required")
    qs = spec.get("questions") or []
    if not qs:
        errors.append("questions is empty")
    for i, q in enumerate(qs, 1):
        if q.get("type") not in KINDS:
            errors.append(f"Q{i}: type must be one of {sorted(KINDS)}")
        if not q.get("title"):
            errors.append(f"Q{i}: title is required")
        if q.get("type") == "choice" and len(q.get("options") or []) < 2:
            errors.append(f"Q{i}: a choice question needs at least 2 options")
        if q.get("other") and q.get("type") != "choice":
            errors.append(f"Q{i}: 'other' applies to choice questions only")
        if any(o.strip() == "その他" for o in q.get("options") or []) and q.get("other"):
            errors.append(f"Q{i}: do not list 'その他' in options when other=true")
    if not any(q.get("type") == "text" and q.get("long") and not q.get("required") for q in qs):
        errors.append("add an optional long free-text question (the survey must always allow free comments)")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", type=Path)
    ap.add_argument("--port", type=int, default=9340)
    ap.add_argument("--account", help="Windows-connected work account shown on the account picker")
    ap.add_argument("--share", choices=["keep", "anyone"], default="keep")
    ap.add_argument("--dry-run", action="store_true", help="validate the spec only")
    ap.add_argument("--only-share", metavar="FORM_ID", help="skip creation; set sharing, short URL and the anonymous check")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    errors = validate(spec)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"spec ok: {len(spec['questions'])} questions")
        return 0

    from playwright.sync_api import sync_playwright
    import forms_lib as F

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{args.port}")
        ctx = browser.contexts[0]
        page = ctx.pages[0]
        if args.account:
            F.sign_in(page, args.account)
        if args.only_share:
            F.set_share_anyone(page, args.only_share)
            short = F.short_url(page, args.only_share)
            ok = F.anonymous_check(browser, short or F.RESPONSE + args.only_share, spec["title"], len(spec["questions"]))
            print(json.dumps({"id": args.only_share, "short": short, "anonymousOk": ok}, ensure_ascii=False))
            return 0
        editor = F.create_form(ctx, page)
        fid = F.form_id(editor)
        print("created form id:", fid, flush=True)
        F.close_copilot_draft_panel(editor)
        F.set_title_desc(editor, spec["title"], spec.get("description") or [])
        for n, q in enumerate(spec["questions"], 1):
            F.add_spec_question(editor, n, q)
            print(f"Q{n} ok", flush=True)
        F.wait_saved(editor)
        problems = F.verify_questions(editor, fid, spec)
        if problems:
            print("verify failed:", problems, file=sys.stderr)
            return 3
        result = {"id": fid, "design": F.DESIGN + fid, "response": F.RESPONSE + fid}
        if args.share == "anyone":
            F.set_share_anyone(editor, fid)
            result["short"] = F.short_url(editor, fid)
            target = result["short"] or result["response"]
            result["anonymousOk"] = F.anonymous_check(browser, target, spec["title"], len(spec["questions"]))
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
