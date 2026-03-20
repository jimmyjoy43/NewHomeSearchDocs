# Final Review Prompt

Use this prompt when you have toured your finalists and need a structured
decision. Feed it to either Claude or ChatGPT. Claude is preferred because
it can read the repo directly.

---

## Prompt

You are helping me make a final apartment decision.

My repo is at: https://github.com/jimmyjoy43/NewHomeSearchDocs

Before doing anything else, read:
- README.md (priorities and budget)
- docs/01_project_brief.md
- docs/scoring_rubric.md
- docs/06_management_red_flags.md
- docs/08_move_timeline.md (my hard deadlines)
- data/buildings.csv (all scored buildings)
- data/tours.csv (my in-person observations)
- research/building_packets/ (deep research for each finalist)
- docs/07_decision_log.md (what I have already ruled out and why)

## My finalists

[LIST EACH FINALIST WITH UNIT NUMBER AND ASKING RENT]

Example:
1. Modera Argyle - Unit 412 - $3,950/month base
2. [Building B] - Unit 207 - $4,100/month base
3. [Building C] - Unit 318 - $3,800/month base

## What I need

### Section 1: Head-to-head comparison table
| Criteria | [Building A] | [Building B] | [Building C] |
One row per criterion from docs/03_essential_amenities.md.
Flag any missing essential amenity in red (use bold in markdown).

### Section 2: Score summary
| Score | [Building A] | [Building B] | [Building C] |
quiet_score, management_score, amenity_score, adult_vibe_score, total.

### Section 3: Financial comparison
For each unit, calculate:
- Net effective monthly rent (accounting for concessions)
- True monthly cost (add parking, pet rent, estimated utilities)
- First-month out-of-pocket (application fee + admin fee + deposit + first month)
- 12-month total cost
- 18-month total cost

### Section 4: Red flag summary
One line per triggered red flag per building. Source and date for each.
Mark CONFIRMED vs INFERRED.

### Section 5: Your recommendation
Pick one. State it in the first sentence.
Then give three reasons.
Then state the single biggest risk with your pick.
Then tell me what to do in the next 48 hours to lock it in.

## Constraints
- My sign deadline is April 12, 2026.
- My move-in target is April 20, 2026.
- If a building requires more than 7 business days for approval, flag it.
- If any finalist has an unresolved hard red flag (management_score = 1,
  confirmed noise enforcement failures, AI-only contact), flag it and
  ask whether to remove it from consideration before proceeding.
