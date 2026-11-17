"""Write the GitHub-readiness files from the templates in site/repo_files/.

The group name, repository URL, goal and conduct contact come from the config block at the top of
site/build.py, so a rename is one edit there followed by:

    .venv/bin/python -I site/build.py && .venv/bin/python -I site/make_repo_files.py

Placeholders in the templates: {{NAME}}, {{REPO}}, {{GOAL}}, {{GOAL_LC}}, {{CONDUCT_CONTACT}}.
Only the files listed in OUTPUTS are written; nothing else in the repository is touched.
README_PUBLIC_DRAFT.md is a draft: the current README.md is left as it is."""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
SRC = SITE / "repo_files"

OUTPUTS = [
    "README_PUBLIC_DRAFT.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSING.md",
    "PUBLISHING_CHECKLIST.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/submit-reading.yml",
    ".github/ISSUE_TEMPLATE/propose-test.yml",
    ".github/ISSUE_TEMPLATE/report-error.yml",
    ".github/ISSUE_TEMPLATE/offer-data.yml",
]


def config():
    """Read the constants from site/build.py without importing it (it needs Pillow and the board)."""
    text = (SITE / "build.py").read_text()
    out = {}
    for key in ("NAME", "REPO_URL", "GOAL", "CONDUCT_CONTACT"):
        m = re.search(rf'^{key}\s*=\s*"([^"]*)"', text, re.M)
        if not m:
            sys.exit(f"{key} not found in site/build.py")
        out[key] = m.group(1)
    return out


def main():
    c = config()
    goal = c["GOAL"].rstrip(".")
    fill = {
        "NAME": c["NAME"],
        "REPO": c["REPO_URL"].rstrip("/"),
        "GOAL": goal,
        "GOAL_LC": goal[0].lower() + goal[1:],
        "CONDUCT_CONTACT": c["CONDUCT_CONTACT"] or
            "[NOT SET: a private address for conduct reports must be chosen before publishing; "
            "see PUBLISHING_CHECKLIST.md]",
    }
    for rel in OUTPUTS:
        src = (SRC / rel).read_text()
        out = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: fill[m.group(1)], src)
        left = re.findall(r"\{\{[A-Z_]+\}\}", out)
        assert not left, f"{rel}: unfilled {left}"
        if rel != "PUBLISHING_CHECKLIST.md":  # the checklist lists where the old word still appears
            assert not re.search(r"\bcrack", out, re.I), f"{rel}: uses the word 'crack'"
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out)
        print("wrote", rel, f"{len(out.encode()) // 1024 + 1} KB")


if __name__ == "__main__":
    main()
