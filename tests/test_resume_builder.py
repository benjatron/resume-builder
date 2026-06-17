import tempfile
import unittest
from pathlib import Path

from resume_builder import (
    create_resume,
    edit_resume,
    export_resume_html,
    export_resume_link,
    main,
    update_resume_from_job_posting,
)


class ResumeBuilderTests(unittest.TestCase):
    def test_create_edit_and_export(self):
        resume = create_resume("Ada", "ada@example.com", summary="Engineer")
        resume = edit_resume(resume, skills=["Python"])

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "resume.html"
            export_resume_html(resume, out)
            html = out.read_text(encoding="utf-8")

        self.assertIn("Ada", html)
        self.assertIn("Python", html)

    def test_export_link(self):
        resume = create_resume("Ada", "ada@example.com")
        link = export_resume_link(resume)
        self.assertTrue(link.startswith("data:text/html;charset=utf-8,"))

    def test_tailor_from_text(self):
        resume = create_resume("Ada", "ada@example.com", skills=["Git"])
        updated = update_resume_from_job_posting(
            resume,
            job_text="Looking for Python and SQL skills with strong communication",
        )

        self.assertIn("Python", updated.skills)
        self.assertIn("SQL", updated.skills)
        self.assertIn("Communication", updated.skills)
        self.assertIn("Tailored for role", updated.summary)

    def test_cli_create_and_export(self):
        with tempfile.TemporaryDirectory() as td:
            resume_path = Path(td) / "resume.json"
            html_path = Path(td) / "resume.html"

            self.assertEqual(
                0,
                main([
                    "create",
                    "--name",
                    "Ada",
                    "--contact",
                    "ada@example.com",
                    "--output",
                    str(resume_path),
                ]),
            )
            self.assertEqual(
                0,
                main([
                    "export",
                    "--resume",
                    str(resume_path),
                    "--html",
                    str(html_path),
                ]),
            )

            self.assertTrue(html_path.exists())


if __name__ == "__main__":
    unittest.main()
