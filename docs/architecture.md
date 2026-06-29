# Architecture Document — Resume Tailor

**Version:** 1.0  
**Date:** 2026-06-29  
**Status:** Approved — ready for implementation

---

## 1. System Overview

Resume Tailor is a Claude Code skill. It has no standalone runtime — Claude Code IS the intelligence layer. Python scripts handle the mechanical work (PDF rendering, file extraction, URL fetching) that Claude cannot do natively. Everything personal stays local; everything reusable is in the public repo.

```
Claude Code session
    │
    ├── reads SKILL.md (routing + instructions)
    ├── reads ~/.claude/resume/master.md (local, personal)
    ├── calls scripts/ for mechanical tasks
    │       ├── fetch_jd.py        (URL fetch)
    │       ├── extract_text.py    (PDF/DOCX → plain text)
    │       └── render_pdf.py      (Markdown → PDF via WeasyPrint)
    └── writes ~/.claude/resume/tailored/[company]-[date]/
            ├── research.md
            ├── resume.md
            ├── resume.pdf
            ├── cover-letter.md    (if requested)
            └── cover-letter.pdf   (if requested)
```

---

## 2. Directory Structure

```
~/.agents/skills/resume-tailor/        ← PUBLIC REPO (G-Eskayo/resume-tailor)
├── SKILL.md                           ← skill definition + command routing
├── README.md                          ← public-facing setup guide
├── scripts/
│   ├── fetch_jd.py                    ← URL fetch, returns plain text or error
│   ├── extract_text.py                ← PDF/DOCX/MD → plain text
│   └── render_pdf.py                  ← Markdown → PDF via WeasyPrint
├── template/
│   └── resume.css                     ← PDF stylesheet (WeasyPrint)
└── docs/
    ├── requirements.md
    ├── design.md
    └── architecture.md  ← this file

~/.claude/resume/                      ← LOCAL ONLY — never in git
├── master.md                          ← master resume (all experience)
└── tailored/
    └── [company]-[YYYY-MM-DD]/
        ├── research.md
        ├── resume.md
        ├── resume.pdf
        ├── cover-letter.md
        └── cover-letter.pdf
```

---

## 3. Component Breakdown

### 3.1 SKILL.md
The entry point. Defines:
- Skill metadata (name, description, tags)
- Command routing table (`/tailor`, `/add-to-master`, `/merge-resume`, `/parse-transcript`)
- Per-command instruction blocks (what Claude does for each command)
- Master resume path constant: `~/.claude/resume/master.md`
- Output path pattern: `~/.claude/resume/tailored/[company]-[date]/`

### 3.2 `scripts/fetch_jd.py`
**Input:** URL string  
**Output:** Plain text of job description, or structured error  
**Behaviour:**
- HTTP GET with browser-like User-Agent header (reduces bot blocking)
- Strips HTML tags, navigation, footer boilerplate via BeautifulSoup
- Returns clean body text
- On any failure: prints clear error message, exits with non-zero code so Claude knows to request paste

### 3.3 `scripts/extract_text.py`
**Input:** File path (`.pdf`, `.docx`, `.md`, `.txt`)  
**Output:** Plain text  
**Behaviour:**
- `.pdf` → pdfminer.six
- `.docx` → python-docx
- `.md` / `.txt` → read directly
- Preserves section structure where detectable

### 3.4 `scripts/render_pdf.py`
**Input:** Path to `.md` file, path to output `.pdf`  
**Output:** PDF file written to disk  
**Behaviour:**
- Converts Markdown → HTML via markdown-it-py
- Applies `template/resume.css` via WeasyPrint
- Single-page enforcement: CSS uses `@page { size: letter; }` with calibrated font/margin sizes
- Exits with error if WeasyPrint not installed, with install instruction

### 3.5 `template/resume.css`
WeasyPrint stylesheet. Defines all visual properties per the PDF Visual Spec in `design.md §7`. Key rules:
- `@page { size: letter; margin: 0.6in 0.65in; }`
- Name: 22pt bold all-caps
- Section headers: 9pt bold all-caps, 1.5px letter-spacing
- Body: 10.5pt, line-height 1.35
- Dividers: `border-top: 0.5pt solid #222`
- Black text only (ATS safe)
- Font: Inter via `@font-face` with system sans-serif fallback

---

## 4. Data Flow

### Tailor command

```
/tailor [url] [--cover-letter]
    │
    ├─ [if URL] fetch_jd.py → JD text
    │           └─ [on fail] → Claude prompts for paste
    │
    ├─ [if no --cover-letter flag] → Claude asks yes/no
    │
    ├─ Claude searches: company, role, contacts
    │   └─ writes research.md
    │
    ├─ Claude reads master.md
    │
    ├─ Claude scores all entries (relevance × 0.7 + recency × 0.3)
    │
    ├─ Claude fills template slots → writes resume.md
    │
    ├─ render_pdf.py resume.md → resume.pdf
    │
    ├─ [if cover letter] Claude writes cover-letter.md
    │                    render_pdf.py cover-letter.md → cover-letter.pdf
    │
    └─ Claude prints package summary
```

### Merge command

```
/merge-resume /path/to/file
    │
    ├─ extract_text.py → plain text
    │
    ├─ Claude parses into sections
    │
    ├─ For each item:
    │   ├─ No match in master → add
    │   ├─ Exact match → skip
    │   └─ Same entity, different content → union + <!-- REVIEW -->
    │
    └─ Claude writes merged master.md + prints diff summary
```

### Parse-transcript command

```
/parse-transcript /path/to/transcript
    │
    ├─ extract_text.py → plain text
    │
    ├─ Claude reads all courses (ignores grades/pass-fail)
    │
    ├─ Maps courses → skill categories
    │   ├─ CS courses → Technical Skills
    │   └─ Aerospace/engineering courses → Engineering & Domain Knowledge
    │
    ├─ For hands-on courses (labs, design, capstone) → prompts user to confirm projects
    │
    └─ Claude inserts extracted skills into master.md
```

---

## 5. Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Intelligence / tailoring | Claude Code (host session) | No API key, no SDK, no extra cost |
| PDF rendering | WeasyPrint | Pure Python, CSS-based, predictable output |
| HTML conversion | markdown-it-py | Fast, no system deps, accurate CommonMark |
| PDF text extraction | pdfminer.six | Pure Python, no system deps |
| DOCX extraction | python-docx | Pure Python, handles modern Word format |
| URL fetching | requests + BeautifulSoup4 | Lightweight, controllable |
| Runtime | `~/.agents/venv/bin/python` | Consistent with all MARVIN scripts |

**Install:**
```bash
~/.agents/venv/bin/pip install weasyprint markdown-it-py pdfminer.six python-docx requests beautifulsoup4
```

---

## 6. Privacy Boundary

| Location | In git? | Contains personal data? |
|---|---|---|
| `~/.agents/skills/resume-tailor/` | Yes (public) | No |
| `~/.claude/resume/master.md` | No | Yes — full PII |
| `~/.claude/resume/tailored/` | No | Yes — full PII |
| `template/resume.css` | Yes (public) | No |
| `scripts/*.py` | Yes (public) | No — paths use `Path.home()` |

Scripts reference the master resume via `Path.home() / ".claude" / "resume" / "master.md"` — no hardcoded personal paths in the public repo.

---

## 7. Architecture Decision Records

### ADR-005: Dynamic title line, fixed experience format
**Decision:** Header title is derived from the JD title each time (dynamic). Experience uses inline bullet-point style (`• **Company:** description`) not traditional "Title | Company | Dates" blocks.  
**Rationale:** Dynamic title signals direct alignment with the role. Inline experience format is the format from the resume that landed Gil's current job — proven effective, kept as-is.  
**Trade-off:** Inline experience format is less conventional for conservative industries. Accepted: format is not modified unless Gil explicitly requests it.

### ADR-001: Claude Code skill over standalone script
**Decision:** Implement as a Claude Code skill, not a CLI script calling the Anthropic API.  
**Rationale:** Claude Code is already the execution environment; no API key management, no SDK dependency, no extra cost per run. The intelligence is the host session.  
**Trade-off:** Requires a Claude Code session to run (not usable as a pure CLI). Acceptable given the workflow.

### ADR-002: Fixed template over render-and-trim for 1-page enforcement
**Decision:** Enforce 1-page via fixed slot caps (max 4 roles × 3 bullets, etc.), not by rendering and iteratively trimming.  
**Rationale:** Render-and-trim requires multiple render cycles and contradicts the measure-once philosophy. Fixed caps are deterministic, fast, and produce consistent results.  
**Trade-off:** Occasionally a slightly shorter output than possible. Acceptable — consistent format is a feature.

### ADR-003: Union rule for resume merges
**Decision:** Merge always adds, never removes. Conflicts flagged with `<!-- REVIEW -->`, not resolved automatically.  
**Rationale:** Silent content deletion in a master resume is unacceptable. Human resolves ambiguity; Claude flags it.  
**Trade-off:** Master resume may accumulate `<!-- REVIEW -->` comments requiring cleanup. Acceptable given the stakes.

### ADR-004: Grades ignored in transcript parsing
**Decision:** Extract skills from all courses regardless of grade or pass/fail outcome.  
**Rationale:** Grade outcome reflects institutional factors; capability is demonstrated by having taken and engaged with the coursework. The aerospace background (~80% of a degree) is a genuine differentiator regardless of grade record.

---

## 8. Implementation Order

1. `scripts/fetch_jd.py` + `scripts/extract_text.py` — input layer, no Claude involvement
2. `template/resume.css` — visual spec, iteratable before any logic
3. `scripts/render_pdf.py` — mechanical output, testable standalone
4. `SKILL.md` — command routing + tailoring instructions (core intelligence layer)
5. End-to-end test: paste a real JD, produce resume + PDF
6. `scripts/render_pdf.py` cover letter mode
7. `/add-to-master` command
8. `/merge-resume` command
9. `/parse-transcript` command
10. README + public repo setup
