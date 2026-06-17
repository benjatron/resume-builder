# resume-builder
An application to create, edit, and export professional resumes (in a desktop application or via an HTML link) as well as to update an existing resume based on a job posting's URL or supplied text

## CLI usage

Create a resume JSON file:

```bash
python resume_builder.py create --name "Ada Lovelace" --contact "ada@example.com" --summary "Software Engineer" --output resume.json
```

Edit a resume:

```bash
python resume_builder.py edit --resume resume.json --summary "Senior Software Engineer"
```

Tailor a resume from a job description text or URL:

```bash
python resume_builder.py tailor --resume resume.json --job-text "Looking for Python and SQL skills"
# or
python resume_builder.py tailor --resume resume.json --job-url "https://example.com/job-posting"
```

Export as a desktop-openable HTML file and/or a shareable HTML data link:

```bash
python resume_builder.py export --resume resume.json --html resume.html
python resume_builder.py export --resume resume.json --print-link
```
