# New Home Search Docs

## Purpose

This repo is the canonical source of truth for an apartment search in Hollywood / West Hollywood, targeting a move-in by April 20, 2026.

GitHub holds all structured data and narrative docs. Notion is a read-only phone mirror. ChatGPT does breadth-first web research. Claude edits the repo, runs deep research, and makes final calls. You are the human in the loop who tours, contacts buildings, and signs the lease.

---

## Search Priorities

- Match or exceed Camden Hollywood amenity level
- Stay in Hollywood or West Hollywood
- Quieter, more stable, more adult building culture than Camden
- Responsive, human leasing and maintenance team (not AI-gated)
- Newer construction or very well-maintained interiors preferred
- Cat friendly, no exceptions
- Target rent: $3,800 to $4,700/month all-in
- Stretch to $5,300 only if the building strongly justifies it

---

## Directory Structure

```
NewHomeSearchDocs/
├── README.md                        # This file. Start here.
├── .gitignore
├── requirements.txt                 # Python deps: notion-client, pandas, python-dotenv
├── .python-version                  # pyenv: NewHomeSearchDocs-py3.14.0
│
├── data/                            # Canonical structured data. Edit CSVs, not markdown.
│   ├── buildings.csv                # One row per unit under consideration
│   ├── tours.csv                    # One row per completed tour
│   ├── contacts.csv                 # One row per leasing contact made
│   └── decisions.csv                # One row per eliminate/advance/sign decision
│
├── docs/                            # Human-readable reference docs
│   ├── 01_project_brief.md          # Objective, neighborhood, budget, required qualities
│   ├── 02_neighborhood_breadth_scan.md  # Status table; auto-section regenerated from CSV
│   ├── 03_essential_amenities.md    # Must-have list for unit, building, and lifestyle
│   ├── 04_nice_to_have_amenities.md # Scoring tiebreakers
│   ├── 05_tour_questions.md         # 31 questions to ask at every tour
│   ├── 06_management_red_flags.md   # Red flag checklist used in research and tours
│   ├── 07_decision_log.md           # Running log of every eliminate/advance/sign call
│   ├── 08_move_timeline.md          # Hard deadlines and decision gates
│   ├── 09_scoring_rubric.md         # 1-5 scale definitions for all four scores
│   └── 10_unit_comparison.md        # Auto-generated; sorted by net effective rent
│
├── prompts/                         # Ready-to-paste prompts for ChatGPT and Claude
│   ├── chatgpt_breadth_scan.md      # Stage 1: find all candidate buildings
│   ├── chatgpt_unit_extraction.md   # Stage 2: pull unit-level data from a listing
│   ├── claude_building_research.md  # Stage 3: deep-dive a specific building
│   ├── claude_repo_editor.md        # Ongoing: Claude's standing instructions for repo edits
│   └── final_review_prompt.md       # Stage 5: structured decision across finalists
│
├── research/
│   ├── building_packets/            # One .md file per building after deep research
│   ├── screenshots/                 # Floor plan images, listing screenshots
│   ├── leases/                      # Lease drafts for review before signing
│   └── raw_notes/                   # Unstructured notes, call logs, email threads
│
├── scripts/
│   ├── validate_csv.py              # Validates all data CSVs; called by CI before sync
│   ├── sync_buildings_to_notion.py  # Upserts buildings.csv rows into Notion database
│   └── generate_markdown_reports.py # Regenerates docs/02 and docs/10 from CSV
│
└── .github/
    └── workflows/
        ├── sync-notion.yml          # Fires on buildings.csv push; validates then syncs
        └── rebuild-docs.yml         # Fires on CSV push; regenerates markdown reports
```

---

## Data Architecture

**GitHub is the source of truth.** If there is a conflict between GitHub and Notion, GitHub wins.

**Notion is a mirror.** It is updated automatically by `sync-notion.yml` whenever `data/buildings.csv` changes on `main`. Use it to browse buildings on your phone. Do not edit it directly.

**The data flow is one-directional:**

```
ChatGPT (research) --> you paste CSV rows --> Claude validates + commits
                                                      |
                                              GitHub Actions fires
                                                      |
                              +---------------------------+------------------+
                              |                           |                  |
                    sync-notion.yml              rebuild-docs.yml      (done)
                              |                           |
                      Notion database          docs/02 + docs/10
                      (phone mirror)           (auto-regenerated)
```

**The scoring columns** (`quiet_score`, `management_score`, `amenity_score`, `adult_vibe_score`) use a 1-5 scale defined in `docs/scoring_rubric.md`. A score of 1 on management AND quiet together is an automatic disqualifier. See the rubric before assigning any scores.

---

## Workflow: Stage by Stage

### Stage 1: Breadth Scan

**Goal:** Identify 10-15 candidate buildings in the target zone before going deep on any one of them.

**Tool:** ChatGPT (has live web browsing; use it for discovery)

**Prompt file:** `prompts/chatgpt_breadth_scan.md`

**How to run it:**
1. Open ChatGPT Plus (GPT-4o with browsing enabled).
2. Paste the full contents of `prompts/chatgpt_breadth_scan.md` into the chat.
3. Send it. ChatGPT will read the repo, search the web, and return CSV rows.

**What the prompt does:**

```
You are helping me find a new apartment.

My canonical project repo is at: https://github.com/jimmyjoy43/NewHomeSearchDocs
Read README.md and data/buildings.csv before doing anything else.

Task: Do a breadth-first scan of luxury apartments in Hollywood and West Hollywood.
Target zone: within 1.5 miles of 1540 Vine St, Hollywood CA 90028.
Rent range: $3,800 to $5,300 all-in.
Required: cat-friendly, in-unit laundry, gym, secure access, controlled parking.
Disqualifiers: AI-only leasing contact, 1-star maintenance reviews, known noise enforcement failures.

Output one CSV row per building matching the buildings.csv schema.
Flag any building where management_score would be 2 or below with a note in remarks.
After the CSV block, output a "## Red flags summary" section.
```

**Expected output:**
- 10-20 CSV rows, one per building (not per unit at this stage)
- A red flags summary section naming any building with management or noise issues
- Most score fields will be blank or estimated; that is expected at this stage

**What to do with the output:**
1. Copy the CSV rows.
2. Open a Claude session and paste the `prompts/claude_repo_editor.md` prompt first.
3. Then paste the CSV rows and tell Claude: "Append these to data/buildings.csv. Validate each row against the schema first."
4. Claude commits the rows. GitHub Actions fires. Notion updates.

---

### Stage 2: Unit Extraction

**Goal:** For each shortlisted building, pull every qualifying unit with current pricing.

**Tool:** ChatGPT (live browsing of listing pages)

**Prompt file:** `prompts/chatgpt_unit_extraction.md`

**How to run it:**
1. For each building that passed Stage 1 screening, get its listing URL (apartments.com, its own site, etc.).
2. Paste the contents of `prompts/chatgpt_unit_extraction.md` into ChatGPT, filling in the building name, address, and URL.

**What the prompt does:**

```
I have already identified the following building for deep research:
Building name: [BUILDING NAME]
Address: [ADDRESS]
URL: [LISTING URL]

Task:
1. Read the listing at the URL.
2. Extract every available unit: 1 bed or larger, under $5,300/month, available within 60 days.
3. Output one CSV row per qualifying unit.

Rules:
- Leave fields empty if data is not available. Do not guess.
- Calculate net_effective_rent from concessions: base_rent minus (free rent value / lease months).
- Repeat building-level fields (gym, pool, cat_policy) across all rows.
- Flag management_score of 2 or below in remarks.

After CSV: output "## Red flags for [BUILDING NAME]" with one line per issue.
```

**Expected output:**
- Multiple CSV rows, one per qualifying unit, with unit numbers, sqft, base rent, net effective rent, and available dates populated
- Net effective rent calculated where concessions are advertised
- A red flags section per building

**What to do with the output:**
Same as Stage 1: paste into Claude with the repo editor prompt active. Claude validates and appends. If a unit already exists in the CSV (same building + unit number), Claude will update the row rather than duplicate it.

---

### Stage 3: Deep Building Research

**Goal:** For each building that survived Stage 2, do a full research pass: reviews, Reddit, news, management history, scores, red flag audit, and a written building packet.

**Tool:** Claude (has web search + can write directly to the repo)

**Prompt file:** `prompts/claude_building_research.md`

**How to run it:**
1. Open a Claude session.
2. Paste the contents of `prompts/claude_building_research.md`, filling in the building name, address, and URL.
3. Claude runs the full 5-step sequence autonomously.

**What the prompt does:**

```
Step 1: Search and gather
  - ApartmentRatings.com, Yelp, Google reviews, Reddit, news, leasing site

Step 2: Score the building
  - Assign quiet_score, management_score, amenity_score, adult_vibe_score (1-5)
  - Label every piece of evidence CONFIRMED or INFERRED

Step 3: Red flag check
  - Go through docs/06_management_red_flags.md line by line
  - Mark each flag TRIGGERED / CLEAR / UNKNOWN with source citation

Step 4: Write building packet
  - Save to research/building_packets/[building_name_slug].md
  - Contents: summary paragraph, scores with reasoning, red flag audit table,
    paraphrased review excerpts, pricing summary, recommended floors/units,
    open questions for tour

Step 5: Update the CSV
  - Append or update the row in data/buildings.csv
  - Set deep_research_done = yes, review_scan_done = yes
  - Report exactly what changed

Hard stop rule: if management_score = 1 AND quiet_score <= 2, stop and ask
before writing anything. Do not proceed without explicit confirmation.
```

**Expected output:**
- A `research/building_packets/[slug].md` file committed to the repo
- Updated rows in `data/buildings.csv` with scores and research flags set
- A clear "worth touring / not worth touring" recommendation in the packet summary

**What disqualifies a building at this stage:**
- management_score of 1 (AI-gated, confirmed unresponsive)
- quiet_score of 1 combined with management_score of 1 or 2
- Any hard red flag that is CONFIRMED (not just INFERRED) from multiple independent sources

---

### Stage 4: Tours

**Goal:** Visit the surviving buildings in person. Stress-test what the research found.

**Tool:** You. In person. With `docs/05_tour_questions.md` open on your phone.

**Before each tour:**
- Read the building's packet in `research/building_packets/`.
- Note which red flags were UNKNOWN so you can probe them on tour.
- Call to schedule. Track how long it takes to reach a human. That is your first data point.

**During the tour:**
- Work through `docs/05_tour_questions.md`. All 31 questions. Every tour.
- Key questions that cannot be skipped:
  - "How long does approval typically take from submission?" (>7 days = flag)
  - "Is this the exact unit I'd be signing for?"
  - "What floor and exposure does this unit have?"
  - "Who do I contact for maintenance and what is the typical response time?"
- Observe the red flag calibration section: hallways, amenities, how the agent handles pushback.

**Immediately after each tour:**
- Fill in a row in `data/tours.csv` before leaving the parking lot.
- Use `data/contacts.csv` to log the leasing agent name, phone, and email.
- Open a Claude session and paste the `prompts/claude_repo_editor.md` prompt, then paste your tour notes. Claude will update the CSV and the decision log.

**What to look for that reviews cannot tell you:**
- Whether the agent is the same person who answered the phone (staffing continuity)
- Whether hallways and amenities match the marketing photos
- Whether the unit faces what you were told it faces
- How the agent responds when you ask about noise complaints or maintenance response times

---

### Stage 5: Final Decision

**Goal:** Pick one building and unit. Commit. Move fast.

**Tool:** Claude (preferred; can read the full repo state)

**Prompt file:** `prompts/final_review_prompt.md`

**How to run it:**
1. Make sure `data/buildings.csv`, `data/tours.csv`, and `docs/07_decision_log.md` are up to date.
2. Open a Claude session.
3. Paste the contents of `prompts/final_review_prompt.md`, filling in your finalists with unit numbers and asking rents.

**What the prompt does:**

```
Before responding, read:
  README.md, 01_project_brief.md, scoring_rubric.md, 06_management_red_flags.md,
  08_move_timeline.md, buildings.csv, tours.csv, building_packets/, 07_decision_log.md

Then produce:
  Section 1: Head-to-head comparison table (one row per essential amenity)
  Section 2: Score summary (quiet, management, amenity, adult_vibe, total)
  Section 3: Financial comparison
    - Net effective monthly rent
    - True monthly cost (base + parking + pet rent + utilities estimate)
    - First-month out-of-pocket (app fee + admin fee + deposit + first month)
    - 12-month total cost
    - 18-month total cost
  Section 4: Red flag summary (one line per flag, CONFIRMED vs INFERRED)
  Section 5: Recommendation
    - Pick one. First sentence.
    - Three reasons.
    - Biggest single risk.
    - Next 48 hours of action to lock it in.

Hard constraints enforced by the prompt:
  - Sign deadline: April 12, 2026
  - Move-in: April 20, 2026
  - Flag any building requiring >7 business days for approval
  - Flag any finalist with management_score = 1 or confirmed noise failures
    and ask whether to remove before proceeding
```

**Expected output:**
- A clear single recommendation in the first sentence
- Full financial breakdown across all finalists
- A concrete 48-hour action list to close on the chosen unit

**After you decide:**
- Log the decision in `data/decisions.csv` and `docs/07_decision_log.md`
- Move eliminated buildings to "Rejected" status in `docs/02_neighborhood_breadth_scan.md`
- Save the lease draft to `research/leases/` before signing

---

## Automation: How GitHub Actions Works

Two workflows fire automatically on pushes to `main`.

### `sync-notion.yml`

Triggers when `data/buildings.csv` changes.

Steps:
1. Validate `buildings.csv` with `scripts/validate_csv.py`. If validation fails, the workflow aborts and nothing touches Notion.
2. Run `scripts/sync_buildings_to_notion.py`. Upserts each row into the Notion "Apartment Units" database, matching on `(building_name, unit_number)`.

### `rebuild-docs.yml`

Triggers when `data/buildings.csv` or `data/tours.csv` changes.

Steps:
1. Validate `buildings.csv`.
2. Run `scripts/generate_markdown_reports.py`. Regenerates the auto-section in `docs/02_neighborhood_breadth_scan.md` and rewrites `docs/10_unit_comparison.md` sorted by net effective rent.
3. Commits the regenerated docs back to `main` with `[skip ci]` in the commit message to prevent a loop.

Both workflows can also be triggered manually from the GitHub Actions tab without making a commit.

---

## One-Time Setup

Before the automation works, complete these steps once:

**1. Create a Notion integration:**
- Go to https://www.notion.so/my-integrations
- Create a new internal integration named "NewHomeSearchDocs"
- Copy the integration token

**2. Share your Notion database with the integration:**
- Open the "Apartment Units" database in Notion
- Click the three-dot menu, then "Connections", then add your integration

**3. Get the database ID:**
- Open the database as a full page in Notion
- Copy the ID from the URL: `notion.so/[workspace]/[DATABASE_ID]?v=...`

**4. Add secrets to GitHub:**
- Go to repo Settings > Secrets and variables > Actions
- Add `NOTION_TOKEN` (the integration token)
- Add `NOTION_DATABASE_ID` (the ID from step 3)

**5. Add a local `.env` file for running scripts on your machine:**
```
NOTION_TOKEN=secret_...
NOTION_DATABASE_ID=...
```
This file is already in `.gitignore`. Never commit it.

**6. Install dependencies:**
```bash
pip install -r requirements.txt
```

**7. Test the sync locally before relying on CI:**
```bash
python scripts/validate_csv.py data/buildings.csv
python scripts/sync_buildings_to_notion.py --dry-run
```

The dry run shows you exactly what would be created or updated in Notion without touching anything real. Always run it first.

---

## Canonical Structured Files

| File | Purpose | Who edits it |
|---|---|---|
| `data/buildings.csv` | One row per unit under consideration | Claude (via repo editor prompt) |
| `data/tours.csv` | One row per completed in-person tour | Claude (from your pasted tour notes) |
| `data/contacts.csv` | One row per leasing contact | Claude or you directly |
| `data/decisions.csv` | One row per eliminate/advance/sign decision | Claude (from your instructions) |

Do not edit these files directly in the GitHub UI unless you are fixing a specific known error. Route all edits through Claude with the repo editor prompt active so changes are validated before commit.

---

## Key Dates

| Gate | Date |
|---|---|
| Breadth scan complete, buildings.csv seeded | 2026-03-21 |
| Deep research on top 5 candidates | 2026-03-23 |
| Tours complete | 2026-03-29 |
| Red-flag eliminations logged | 2026-03-30 |
| Final review prompt run | 2026-03-31 |
| Applications submitted | 2026-04-01 |
| Lease signed | 2026-04-12 |
| Movers scheduled | 2026-04-13 |
| Move-in | 2026-04-20 |

Last safe application submission date given typical 3-5 day approval windows: **2026-04-04**.
Any building that cannot confirm a sub-7-business-day approval timeline is off the list.
