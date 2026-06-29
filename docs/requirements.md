# Requirements Document — Resume Tailor

**Version:** 1.0  
**Date:** 2026-06-29  
**Status:** Approved (post-grill session)

---

## 1. Purpose

A Claude Code skill that maintains a comprehensive master resume and generates tailored, consistently formatted 1-page resumes from any job description. The goal is to eliminate manual tailoring effort while producing higher-quality, concept-matched outputs than keyword-stuffed resumes.

---

## 2. Functional Requirements

### 2.1 Master Resume

| ID | Requirement |
|---|---|
| FR-01 | The system SHALL maintain a single master resume at `~/.claude/resume/master.md` in Markdown format with YAML frontmatter. |
| FR-02 | The master resume SHALL contain all experience, projects, skills, education, and certifications with no length restriction. |
| FR-03 | The YAML frontmatter SHALL include: `name`, `email`, `phone`, `location`, `linkedin`, `github`, `portfolio`. |
| FR-04 | The master resume SHALL never be transmitted to any external service, stored in git, or leave the local machine. |

### 2.2 Company & Role Research

| ID | Requirement |
|---|---|
| FR-05 | Before tailoring, the skill SHALL research: the company (mission, culture, recent news, tech stack, product), the specific role (responsibilities, team context, seniority signals), and potential points of contact (hiring manager, team lead, recruiter — sourced via web search). |
| FR-06 | Research findings SHALL be saved to `~/.claude/resume/tailored/[company]-[YYYY-MM-DD]/research.md` for reference. |
| FR-07 | If a named contact is found, the cover letter SHALL address that person by name. If not, it SHALL use a professional fallback ("Dear [Team] Hiring Team"). |

### 2.3 Tailoring

| ID | Requirement |
|---|---|
| FR-08 | The skill SHALL accept a job description as either a URL (best-effort fetch) or pasted text. |
| FR-09 | If URL fetch fails, the skill SHALL notify the user clearly and prompt for a paste. |
| FR-10 | Matching SHALL be semantic and conceptual — ideas, domains, and transferable skills — not string or keyword matching. |
| FR-11 | The skill SHALL NOT filter based on years-of-experience requirements stated in the JD. |
| FR-12 | Each candidate experience/project SHALL be scored on two axes: (1) semantic relevance to JD concepts, (2) recency. Combined score = relevance × 0.7 + recency × 0.3. Top scorers fill template slots. |
| FR-13 | The skill SHALL incorporate company research findings into tailoring decisions: mirror the company's language, emphasise experiences that align with their known tech stack or domain, signal cultural fit. |
| FR-14 | The skill SHALL produce a tailored resume in both Markdown and PDF formats. |
| FR-15 | All PDF outputs SHALL use the same visual template. |
| FR-16 | The resume output SHALL always fit on exactly one page, enforced by fixed template slot limits (see Design Doc §4). |

### 2.4 Cover Letter

| ID | Requirement |
|---|---|
| FR-17 | The skill SHALL generate a tailored cover letter alongside every resume output if explicitly specified. If not specified, the skill SHALL ask "Would you like a cover letter with this application? (yes/no)" before proceeding. |
| FR-18 | The cover letter SHALL be grounded in company research — it MUST reference something specific about the company (product, mission, recent news, known challenge) to demonstrate genuine interest. |
| FR-19 | The cover letter SHALL tell a cohesive narrative: this is who I am → this is what I have built → this is why I specifically want to work here → this is what I will bring. |
| FR-20 | The cover letter SHALL be maximum 4 paragraphs, fitting on one page. |
| FR-21 | The cover letter SHALL NOT open with "I am writing to apply for..." or any equivalent dead opener. |
| FR-22 | The cover letter tone SHALL adapt to company culture: energetic and direct for startups, professional and structured for enterprise. Culture signal is derived from company research. |
| FR-23 | The cover letter SHALL highlight the aerospace + CS crossover as a unique differentiator when the role has any systems, engineering, physics, simulation, or technical depth angle. |
| FR-24 | Cover letter SHALL be saved as `cover-letter.md` and `cover-letter.pdf` in the same output folder as the resume. |

### 2.5 Output Package

Every application generates a complete package at `~/.claude/resume/tailored/[company]-[YYYY-MM-DD]/`:

| File | Contents |
|---|---|
| `research.md` | Company, role, and contact research notes |
| `resume.md` | Tailored 1-page resume (Markdown) |
| `resume.pdf` | Tailored 1-page resume (PDF) |
| `cover-letter.md` | Tailored cover letter (Markdown) |
| `cover-letter.pdf` | Tailored cover letter (PDF) |

### 2.3 Master Resume Updates

| ID | Requirement |
|---|---|
| FR-12 | The skill SHALL support a `add-to-master` command that accepts a natural language description of a new experience, project, skill, or certification and inserts it as a correctly formatted entry in the appropriate section. |
| FR-13 | The skill SHALL support a `merge-resume` command that accepts an uploaded resume file (`.md`, `.pdf`, `.docx`) and merges its content into the master resume using a union rule. |
| FR-14 | Merge SHALL never silently delete any content from the master resume. |
| FR-15 | When merge encounters ambiguous duplicates (same company, overlapping dates, different content), it SHALL keep all content and annotate conflicts with `<!-- REVIEW: ... -->` comments for manual resolution. |
| FR-16 | After merge, the skill SHALL output a summary of what was added, what was flagged, and what was unchanged. |

### 2.4 Transcript Parsing

| ID | Requirement |
|---|---|
| FR-17 | The skill SHALL support a `parse-transcript` command that accepts an academic transcript and extracts skills, domain knowledge, tools, and project-relevant coursework into the master resume. |
| FR-18 | Transcript parsing SHALL extract skills from ALL courses regardless of grade or pass/fail status. Grade outcome reflects institutional factors, not capability. |
| FR-19 | Courses from a non-graduated discipline (e.g. ~80% of an aerospace engineering degree) SHALL be treated as equivalent to completed coursework for skill extraction purposes. |
| FR-20 | Extracted aerospace/engineering coursework SHALL be categorised into a dedicated `Engineering & Domain Knowledge` skills section in the master resume, distinct from Technical Skills, to signal the cross-disciplinary background. |
| FR-21 | Where coursework implies hands-on projects (labs, capstone work, design courses), the skill SHALL prompt the user to confirm or expand on those as potential Projects entries. |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The tailored output SHALL be visually identical in format regardless of role or company. |
| NFR-02 | The PDF SHALL use a single-column layout for ATS compatibility. |
| NFR-03 | The skill SHALL require no Anthropic API key — it runs as a Claude Code skill using the host session. |
| NFR-04 | The public GitHub repo (`G-Eskayo/resume-tailor`) SHALL contain zero personal data. |
| NFR-05 | All scripts SHALL run via `~/.agents/venv/bin/python`. |

---

## 6. Output Format Rules & Best Practices

### 6.1 Section Order (fixed, non-negotiable)
Derived from Gil's actual resume format.

1. Header (name, title, contact block)
2. Summary paragraph (no section label — flows directly under header)
3. Professional Experience (bullet-point style, bold company name inline)
4. Technical Skills (category – skills format, em-dash separator)
5. Soft Skills (flat list, 6 items max — new section)
6. Projects
7. Education (single line)
8. Relevant Training (certs + self-directed learning)
9. Achievements (Veteran, Eagle Scout, awards)

### 6.2 Content Rules

**Header**
- Full name in largest font
- Title line: dynamically set to the target role's title (e.g. "SENIOR ML ENGINEER", "BACKEND ENGINEER"). Derived from the JD title; if ambiguous, Claude infers the closest match. Fallback: master resume default title.
- Contact line: Portfolio · email · LinkedIn · phone · GitHub · U.S. Citizen
- No photo, no headshot

**Summary**
- 2–3 sentences maximum
- Tailored to the specific role — never generic
- Written in first person implicit (no "I am a...")

**Technical Skills**
- Grouped by category (Languages, Frameworks, Tools, Platforms)
- Maximum 4 categories, maximum 4 items per category
- No proficiency bars or ratings — listing a skill implies competency

**Soft Skills**
- Flat list, maximum 6 items
- Each item is a single noun or noun phrase ("Cross-functional collaboration", not "I collaborate well")
- Selected based on JD language — if JD emphasises leadership, leadership-adjacent skills surface

**Experience**
- Maximum 4 entries
- Format: inline bullet-point style — `• **Company Name:** narrative description of role and impact`
- Maximum 3 bullets per company
- Each bullet is a self-contained achievement sentence starting with the bold company name
- Every bullet uses active, delivered language — no "Responsible for…"
- Quantified impact included wherever the master resume provides numbers

**Projects**
- Maximum 2 projects
- Format: `Project Name` with tech stack in parentheses
- Maximum 2 bullets per project
- Include GitHub link or live URL if present in master

**Education**
- Always included, always at the bottom
- Format: `Degree, Major | Institution | Year` — one line, nothing else
- No GPA, no honors, no coursework — experience and skills speak louder
- Institution name only; no ranking, no prestige signals

**Certifications**
- Maximum 3, only if present in master
- Format: `Certification Name | Issuer | Year`

### 6.3 Format Approval Process

The output template is treated as a locked design asset once approved. Workflow:
1. Prototype samples are shown in the design doc and during development
2. Giles uploads existing resumes; format is refined to match the newer ones
3. Explicit approval ("this looks right") locks the template
4. No template changes without explicit re-approval

---

## 4. Out of Scope (v1.0)

- LinkedIn API integration (ToS restriction — manual update only)
- Automatic GitHub project sync into master resume (Phase 2)
- Cover letter generation
- Multi-page resumes
- ATS submission automation
- Interview question generation from JD
- Salary research

---

## 5. Success Criteria

- Given the master resume and any real job description, the skill produces a correctly formatted 1-page PDF in a single invocation with no manual editing required.
- The merge command processes an uploaded resume and produces a clean master with no lost content.
- No personal data appears in the public repo at any point.
