# Resume Tailor Skill

**Triggers:** `/tailor`, `/add-to-master`, `/merge-resume`, `/parse-transcript`  
**Purpose:** Maintain a master resume and generate tailored 1-page application packages from job descriptions.

---

## Constants

- **Master resume:** `~/.claude/resume/master.md`
- **Output base:** `~/.claude/resume/tailored/`
- **Output pattern:** `~/.claude/resume/tailored/[company-slug]-[YYYY-MM-DD]/`
- **Scripts:** `~/.agents/skills/resume-tailor/scripts/`
- **Python:** `~/.agents/venv/bin/python`

---

## Command Routing

| Invocation | Handler |
|---|---|
| `/tailor [url] [--cover-letter]` | [TAILOR] |
| `/add-to-master "..."` | [ADD-TO-MASTER] |
| `/merge-resume [path]` | [MERGE-RESUME] |
| `/parse-transcript [path]` | [PARSE-TRANSCRIPT] |

---

## [TAILOR] — Full Application Package

### Phase 1: Intake

1. If a URL was provided: run `~/.agents/venv/bin/python ~/.agents/skills/resume-tailor/scripts/fetch_jd.py <url>`
   - If it succeeds: use stdout as the JD text
   - If it fails (non-zero exit): say "Couldn't fetch that URL — please paste the job description directly."
2. If no URL: ask "Please paste the job description."
3. If `--cover-letter` was NOT in the invocation: ask "Would you like a cover letter with this application? (yes/no)"

### Phase 2: Research

Search for:
- **Company:** mission, values, product, recent news (last 12 months), tech stack, team size/stage, culture signals (startup vs. enterprise)
- **Role:** seniority signals, team context, reporting structure if visible, tech signals
- **Contact:** hiring manager name, recruiter, team lead — check company site, LinkedIn, job post

Determine output folder name: slugify company name (lowercase, hyphens, no special chars) + today's date.  
Write `~/.claude/resume/tailored/[slug]-[date]/research.md` with all findings.

### Phase 3: Tailoring

Read `~/.claude/resume/master.md` in full.

**Extract from JD:**
- Job title → use verbatim as the header title line (all-caps). If ambiguous, infer the best match.
- Semantic concepts: domain areas, responsibility types, tech clusters, cultural signals
- Aerospace/defense signals: check for keywords — systems, engineering, simulation, physics, aerospace, hardware, robotics, defence, aviation, space, dynamics, structural, fluid, orbital, DoD, government, clearance

**Score every master resume entry:**
```
combined = (relevance × 0.7) + (recency × 0.3)

recency: 1.0 = current | 0.85 = <1yr | 0.65 = 1–3yr | 0.40 = 3–6yr | 0.20 = >6yr
relevance: 1.0 = direct match | 0.6 = transferable | 0.3 = adjacent
```
Select top 4 roles and top 2 projects. Ties broken by recency.

**Aerospace crossover signal:** If JD has any aerospace/defense/systems keyword → surface the aerospace background in:
- The summary (explicitly mention dual-discipline background)
- The Engineering & Domain Knowledge skills category
- The cover letter unique angle paragraph

**Security clearance signal:** If JD is for a government/defense/cleared role → surface "Security Clearance: Secret (Reinstatable)" prominently in the header contact block.

**Mirror company language:** Use their terminology, not generic buzzwords.

### Phase 4: Build Resume

Write `~/.claude/resume/tailored/[slug]-[date]/resume.md` using this exact template structure.

**CRITICAL FORMATTING RULE:** Every paragraph element (bullets, project titles, achievement lines) MUST be separated by a blank line. Items within the same markdown block merge into a single visual line. One blank line = one visual paragraph break.

```markdown
# GIL ESKAYO

[JD-DERIVED TITLE — ALL CAPS]

Portfolio: gileskayo.me  |  geskayo@gmail.com  |  linkedin.com/in/gileskayo

(650) 867-2527  |  github.com/G-Eskayo  |  U.S. Citizen[  |  Security Clearance: Secret (Reinstatable) — if defense/gov role]

---

[SUMMARY — 2–3 sentences. Tailored to the specific role. No "I am a..." opener. Lead with what you build, then the crossover if relevant, then the current work.]

## PROFESSIONAL EXPERIENCE

• **[Company Name]:** [narrative — action verbs, quantified impact where available, mirrors JD language]

• **[Company Name]:** [bullet 2 — each role gets its own blank-line-separated paragraph]

• **[Company Name]:** [bullet 3 — up to 3 bullets per company, each separated by blank line]

[Max 4 roles total. Each additional bullet for a company: also blank-line separated.]

## TECHNICAL SKILLS

• **[Category] –** [skill], [skill], [skill], [skill — max 4 items per category]

• **[Category] –** [skill], [skill], [skill], [skill]

• **[Category] –** [skill], [skill], [skill], [skill]

• **[Category] –** [skill], [skill], [skill], [skill]

[Max 4 categories. Include Cybersecurity if JD is security-relevant. Include Engineering & Domain Knowledge if aerospace signal detected.]

## SOFT SKILLS

[skill]  ·  [skill]  ·  [skill]  ·  [skill]  ·  [skill]  ·  [skill — max 6, JD-matched, on one line]

---

## PROJECTS

**[Project Name — bold, no bullet]** ([brief tech stack or award context])

• [bullet 1 — what was built, impact, scale]

• [bullet 2 — optional, max 2 per project]

**[Project Name]** ([tech stack])

• [bullet 1]

[Max 2 projects.]

---

## EDUCATION

B.S. Computer Science – University of Colorado Boulder  |  August 2025

## RELEVANT TRAINING

• [Cert name] – [Issuer] – [one-line description of what was built/learned]

• [Cert name] – [Issuer] – [description]

• [Cert name] – [Issuer] – [description]

[Max 3 certs — select most relevant to JD. Each cert on its own blank-line-separated paragraph.]

## ACHIEVEMENTS

U.S. Armed Forces Veteran – Chemical, Biological, Radiological & Nuclear (CBRN) Defense Specialist[, Security Clearance: Secret (Reinstatable) — append if defense/gov role]

Eagle Scout – Highest rank in Boy Scouts; 31 merit badges and two Eagle Palms

[Include both for leadership/character-signal roles. Include just Veteran for defense/gov roles if space is tight.]
```

**Slot caps (non-negotiable):**
- Summary: 2–3 sentences
- Tech Skills: max 4 categories × 4 items
- Soft Skills: max 6 items
- Experience: max 4 roles × 3 bullets
- Projects: max 2 × 2 bullets
- Certs: max 3
- Education: 1 line only

### Phase 5: Render PDF

Run:
```
~/.agents/venv/bin/python ~/.agents/skills/resume-tailor/scripts/render_pdf.py \
  ~/.claude/resume/tailored/[slug]-[date]/resume.md \
  ~/.claude/resume/tailored/[slug]-[date]/resume.pdf
```

### Phase 6: Cover Letter (if requested)

Write `~/.claude/resume/tailored/[slug]-[date]/cover-letter.md`:

```
[Name]
[email]  |  [phone]
[Date]

[Hiring Manager Name], [Title] at [Company]   ← use researched name if found
[else: Dear [Company] Hiring Team,]

PARAGRAPH 1 — HOOK (3–4 sentences)
  Reference something specific and real about the company — a product, stated mission, recent
  announcement, or known challenge. Never open with "I am writing to apply for..."
  State the role and why this company specifically.

PARAGRAPH 2 — STRONGEST MATCH (4–5 sentences)
  The single most relevant experience mapped to the JD.
  Concrete: what was built, what was the impact, what was the scale.
  Use the JD's own language where it fits naturally.

PARAGRAPH 3 — UNIQUE ANGLE (3–4 sentences)
  What Giles brings that a typical candidate doesn't.
  Lead with aerospace + CS crossover if JD has any engineering/systems angle.
  Otherwise: MARVIN (self-directed agentic systems project), cross-disciplinary builder mentality,
  shipped public work.
  If clearance-relevant: mention Secret clearance reinstatable status.

PARAGRAPH 4 — CLOSE (2–3 sentences)
  Confident, not desperate. Genuine enthusiasm for the conversation.
  Clear call to action. Match company energy (direct for startups, measured for enterprise).
```

Then render:
```
~/.agents/venv/bin/python ~/.agents/skills/resume-tailor/scripts/render_pdf.py \
  ~/.claude/resume/tailored/[slug]-[date]/cover-letter.md \
  ~/.claude/resume/tailored/[slug]-[date]/cover-letter.pdf \
  --cover-letter
```

### Phase 7: Package Summary

Print:
```
✓ Application package ready: ~/.claude/resume/tailored/[slug]-[date]/
  Files:
    resume.md / resume.pdf
    [cover-letter.md / cover-letter.pdf — if generated]
    research.md

  Key matches: [top 3 JD concepts → master resume entries that scored highest]
  Title used: [derived title]
  Contact found: [name + title if found, else "not found — used generic salutation"]
  Aerospace signal: [yes/no — surfaced or not]
  Clearance surfaced: [yes/no]
```

---

## [ADD-TO-MASTER] — Add New Entry

Input: natural language description of a new experience, project, skill, cert, or achievement.

1. Identify which section the entry belongs in (Experience / Projects / Skills / Relevant Training / Achievements)
2. Format it following the conventions in that section
3. For Experience: convert to action-verb bullets, extract implicit dates if mentioned
4. Insert at the correct chronological position (most recent first)
5. Write the updated master.md
6. Confirm: "Added to [Section]. Review: ~/.claude/resume/master.md"

---

## [MERGE-RESUME] — Merge Uploaded Resume

Input: file path to .pdf, .docx, .md, or .txt resume

1. Run `~/.agents/venv/bin/python ~/.agents/skills/resume-tailor/scripts/extract_text.py <path>`
2. Parse the extracted text into sections matching master.md structure
3. For each item:
   - **No match in master:** add to master in correct section and position
   - **Exact match:** skip (already present)
   - **Same entity, different content** (same company + overlapping dates, different title or bullets): keep ALL content, add `<!-- REVIEW: same company/dates, different content — verify and consolidate -->`
4. Write merged master.md
5. Print: "Merge complete: N added, N flagged for review (<!-- REVIEW --> comments), N unchanged"

**Rule:** NEVER silently remove any content from the master resume. Union only.

---

## [PARSE-TRANSCRIPT] — Extract Skills from Academic Transcript

Input: file path to transcript (.pdf or .txt)

1. Run `~/.agents/venv/bin/python ~/.agents/skills/resume-tailor/scripts/extract_text.py <path>`
2. Read ALL courses regardless of grade or pass/fail status
3. Map courses to skill categories:
   - CS/programming/data/AI courses → Technical Skills (add to appropriate subcategory)
   - Aerospace/engineering/physics/math courses → Engineering & Domain Knowledge
   - Leadership/military courses → Achievements section (if veteran-relevant) or Soft Skills
4. For courses implying hands-on work (labs, capstone, design courses, experimental courses):
   - Ask: "[Course name] — did this involve a project worth adding to your Projects section?"
5. Identify any new skills not already in master.md and add them
6. Print: "Parsed [N] courses. Added: [N] skills to Technical Skills, [N] to Engineering & Domain Knowledge, [N] projects flagged for review."

**Rule:** Grades do not gate skill extraction. ~80% of an aerospace engineering degree = genuine domain knowledge regardless of grade record.

---

## Quality Checks (apply to all outputs)

- No "Responsible for..." openers — use action verbs (Built, Designed, Led, Developed, Implemented)
- No years-of-experience filtering from JD applied to master resume entries
- No GPA, no honors, no coursework in Education section of tailored resume
- No photo placeholder
- No personal data in any file under `~/.agents/skills/resume-tailor/` (public repo)
- All scripts run via `~/.agents/venv/bin/python`
