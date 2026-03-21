# Claude Prompt: Building Research

Use this prompt when you want Claude to do a deep-dive research pass on a
specific building: scraping reviews, news, Reddit, and any available management
history, then scoring it and writing a building packet.

---

## Prompt

You are the researcher and analyst for my apartment search.

My repo is at: https://github.com/jimmyjoy43/NewHomeSearchDocs
My scoring rubric is in: docs/scoring_rubric.md
My red flag checklist is in: docs/06_management_red_flags.md
My essential amenities list is in: docs/03_essential_amenities.md

I need a deep research pass on this building:
**Building name:** [BUILDING NAME]
**Address:** [ADDRESS]
**URL:** [LISTING URL]

## What I need you to do

### Step 1: Search and gather
Search for the following and note your sources:
- ApartmentRatings.com reviews
- Yelp reviews
- Google reviews (summarized)
- Reddit mentions (r/LosAngeles, r/ApartmentList, r/westla, or similar)
- Any news articles about the building, developer, or management company
- The building's own leasing site for current concessions and availability

### Step 2: Score the building
Using docs/scoring_rubric.md, assign scores 1-5 for:
- quiet_score
- management_score
- amenity_score
- adult_vibe_score

For each score, show your reasoning in 1-2 sentences. Label each piece of
evidence as CONFIRMED (from reviews/public record) or INFERRED (from patterns
or limited data).

### Step 3: Red flag check
Go through docs/06_management_red_flags.md line by line.
For each flag, mark: TRIGGERED / CLEAR / UNKNOWN.
If triggered, cite the source.

### Step 4: Write a building packet
Save a file to research/building_packets/[building_name_slug].md with:
- One-paragraph summary (what this building is and whether it's worth touring)
- Scores with reasoning
- Red flag audit table
- 3-5 most useful review quotes (paraphrased, attributed by source and date)
- Current pricing and concessions summary
- Recommended units or floors to request (based on noise/exposure data if available)
- Open questions to answer on tour

### Step 5: Update the CSV
Append or update the row in data/buildings.csv for this building.
Set deep_research_done = yes and review_scan_done = yes.
Update last_updated to today.
Tell me exactly what changed.

## Hard stop rule
If management_score comes back as 1 and quiet_score comes back as 1 or 2,
stop and tell me before writing the packet. Ask whether to proceed or reject.
