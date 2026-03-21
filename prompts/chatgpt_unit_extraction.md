# ChatGPT Prompt: Unit Extraction

Use this prompt when you have identified a specific building to research deeply
and want ChatGPT to pull all available unit-level data from its listing pages.

---

## Prompt

You are helping me find a new apartment.

My canonical project repo is at: https://github.com/jimmyjoy43/NewHomeSearchDocs

I have already identified the following building for deep research:
**Building name:** [BUILDING NAME]
**Address:** [ADDRESS]
**URL:** [LISTING URL - e.g. apartments.com, moderaargyle.com, etc.]

Your task:
1. Read the listing at the URL above.
2. Extract every available unit that matches these filters:
   - 1 bedroom or larger
   - Base rent under $5,300/month
   - Available within the next 60 days (or available date unknown)
3. For each qualifying unit, output one CSV row using this exact schema header:

building_name,address,neighborhood,url,unit_number,bed_bath,sqft,base_rent,net_effective_rent,available_date,lease_term_months,application_fee,admin_fee,security_deposit,parking_cost,pet_rent,cat_policy,in_unit_laundry,dishwasher,central_ac,package_room,controlled_access,gym,pool,coworking,conference_room,ev_charging,rooftop,quiet_score,management_score,amenity_score,adult_vibe_score,essential_amenities_all_yes,missing_essential_amenities,nice_to_have_yes_count,tour_date,deep_research_done,review_scan_done,news_scan_done,remarks,last_updated

Rules:
- Output only valid CSV rows after the header. No commentary between rows.
- Use today's date (YYYY-MM-DD) for last_updated.
- Leave fields empty if the data is not available. Do not guess.
- For building-level fields (gym, pool, cat_policy, etc.) that apply to all units,
  repeat the same value in every row.
- For scores (quiet_score, management_score, amenity_score, adult_vibe_score):
  use 1-5. Leave blank if you cannot score it from available data.
  Do not invent scores. Note in remarks if a score is estimated vs confirmed.
- If net_effective_rent differs from base_rent due to concessions, calculate it
  as: base_rent minus (total free rent value / lease term months).
- Flag any unit where management_score would be 2 or below with a note in remarks.

After the CSV output, add a single section called:
## Red flags for [BUILDING NAME]
List any issues found during extraction (noise complaints, AI-gated leasing,
incomplete amenities, construction caveats, etc.) as a short bulleted list.
One line per flag. No fluff.
