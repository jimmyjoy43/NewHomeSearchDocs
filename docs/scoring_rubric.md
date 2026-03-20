# Scoring Rubric

All scores are 1-5. 1 = unacceptable. 3 = acceptable. 5 = excellent.

## quiet_score
5: No noise complaints in reviews. Unit faces interior or quiet street.
4: Minor noise mentions. No chronic issues.
3: Noise mentioned but manageable.
2: Noise is a recurring theme in reviews.
1: Chronic noise complaints or unit faces major street/venue.

## management_score
5: Named staff praised across multiple independent reviews. Fast maintenance response confirmed.
4: Generally positive with isolated complaints.
3: Mixed. Depends on who you get.
2: Multiple reviews mention ignored requests or AI-gated communication.
1: Staff rated 1/5 on ApartmentRatings. Confirmed unresponsive.

## amenity_score
5: All essential amenities present + 4 or more nice-to-haves.
4: All essentials + 2-3 nice-to-haves.
3: All essentials, no nice-to-haves.
2: Missing 1 essential amenity.
1: Missing 2+ essential amenities.

## adult_vibe_score
5: Reviews specifically mention quiet community, professionals, stable long-term tenants.
4: No red flags. Community feels settled.
3: Mixed. Some party/noise culture present but not dominant.
2: Reviews mention rowdy neighbors, loud common areas, or party culture.
1: Stunt actors doing commercial shoots past 11 PM.
```

That last line is not a joke. You have a real data point from The Camden. Put it in the rubric as a reference anchor.

---

## 5. The Prompts Directory Needs to Actually Exist

The plan lists prompt filenames but doesn't write the prompts. That's the most important missing piece. Here are the two you need immediately:

### `prompts/chatgpt_breadth_scan.md`
```
You are helping me find a new apartment.

My canonical project repo is at: [GITHUB_REPO_URL]
Read README.md and data/buildings.csv before doing anything else.

Task: Do a breadth-first scan of luxury apartments in Hollywood and West Hollywood.
Target zone: within 1.5 miles of 1540 Vine St, Hollywood CA 90028.
Rent range: $3,800 to $5,300 all-in.
Required: cat-friendly, in-unit laundry, gym, secure access, controlled parking.
Disqualifiers: AI-only leasing contact, 1-star maintenance reviews, known noise enforcement failures.

For each building you find, output a CSV row matching this schema exactly:
[paste schema header row here]

Do not add commentary between rows. Output only valid CSV rows.
Flag any building where management_score would be 2 or below, with a one-line reason.
```

### `prompts/claude_repo_editor.md`
```
You are the editor and maintainer of my apartment search repo.

Repo location: [GITHUB_REPO_URL]
Before each session: read README.md, data/buildings.csv, and docs/07_decision_log.md.

Your job:
1. Accept new building data or research from me (or pasted from ChatGPT output).
2. Validate it against the schema in data/buildings.csv.
3. Append or update rows in buildings.csv.
4. Update docs/02_neighborhood_breadth_scan.md status table.
5. Log any decision or elimination in docs/07_decision_log.md with today's date.
6. Ask me one clarifying question if data is ambiguous. Then proceed.

Never overwrite existing data without confirming.
Always state what you changed and what file it went into.