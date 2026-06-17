from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from html import escape
from pathlib import Path
from typing import Iterable

SKILL_DISPLAY = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "sql": "SQL",
    "aws": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "leadership": "Leadership",
    "communication": "Communication",
}


@dataclass
class Resume:
    name: str
    contact: str
    summary: str = ""
    experience: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)


def create_resume(name: str, contact: str, **sections: object) -> Resume:
    return Resume(
        name=name,
        contact=contact,
        summary=str(sections.get("summary", "")),
        experience=list(sections.get("experience", [])),
        education=list(sections.get("education", [])),
        skills=list(sections.get("skills", [])),
    )


def edit_resume(resume: Resume, **updates: object) -> Resume:
    for field_name, value in updates.items():
        if not hasattr(resume, field_name):
            raise ValueError(f"Unknown resume field: {field_name}")
        setattr(resume, field_name, value)
    return resume


def _as_list(items: Iterable[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def resume_to_html(resume: Resume) -> str:
    return (
        "<html><head><meta charset='utf-8'><title>Resume</title></head><body>"
        f"<h1>{escape(resume.name)}</h1>"
        f"<p><strong>Contact:</strong> {escape(resume.contact)}</p>"
        f"<h2>Summary</h2><p>{escape(resume.summary)}</p>"
        f"<h2>Experience</h2><ul>{_as_list(resume.experience)}</ul>"
        f"<h2>Education</h2><ul>{_as_list(resume.education)}</ul>"
        f"<h2>Skills</h2><ul>{_as_list(resume.skills)}</ul>"
        "</body></html>"
    )


def export_resume_html(resume: Resume, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.write_text(resume_to_html(resume), encoding="utf-8")
    return output


def export_resume_link(resume: Resume) -> str:
    return "data:text/html;charset=utf-8," + urllib.parse.quote(resume_to_html(resume))


def _fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def update_resume_from_job_posting(
    resume: Resume,
    job_text: str | None = None,
    job_url: str | None = None,
) -> Resume:
    if not job_text and not job_url:
        raise ValueError("Provide job_text or job_url")

    posting = job_text or _fetch_text(job_url or "")
    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}", posting)
    }

    suggested = sorted(skill for skill in SKILL_DISPLAY if skill in words)

    existing = {skill.lower(): skill for skill in resume.skills}
    for skill in suggested:
        if skill not in existing:
            resume.skills.append(SKILL_DISPLAY[skill])

    if suggested:
        resume.summary = (
            (resume.summary + " ").strip()
            + "Tailored for role emphasizing "
            + ", ".join(SKILL_DISPLAY[skill] for skill in suggested)
            + "."
        ).strip()

    return resume


def _load_resume(path: str | Path) -> Resume:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Resume(**data)


def _save_resume(resume: Resume, path: str | Path) -> None:
    Path(path).write_text(json.dumps(asdict(resume), indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create, edit, export, and tailor resumes")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--contact", required=True)
    create.add_argument("--summary", default="")
    create.add_argument("--output", required=True)

    edit = sub.add_parser("edit")
    edit.add_argument("--resume", required=True)
    edit.add_argument("--summary")

    export = sub.add_parser("export")
    export.add_argument("--resume", required=True)
    export.add_argument("--html")
    export.add_argument("--print-link", action="store_true")

    tailor = sub.add_parser("tailor")
    tailor.add_argument("--resume", required=True)
    tailor.add_argument("--job-text")
    tailor.add_argument("--job-url")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "create":
        resume = create_resume(args.name, args.contact, summary=args.summary)
        _save_resume(resume, args.output)
        return 0

    if args.command == "edit":
        resume = _load_resume(args.resume)
        updates = {"summary": args.summary} if args.summary is not None else {}
        edit_resume(resume, **updates)
        _save_resume(resume, args.resume)
        return 0

    if args.command == "export":
        resume = _load_resume(args.resume)
        if args.html:
            export_resume_html(resume, args.html)
        if args.print_link:
            print(export_resume_link(resume))
        if not args.html and not args.print_link:
            raise ValueError("Specify --html and/or --print-link")
        return 0

    if args.command == "tailor":
        resume = _load_resume(args.resume)
        update_resume_from_job_posting(resume, job_text=args.job_text, job_url=args.job_url)
        _save_resume(resume, args.resume)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
