# ChatGPT Prompt: Breadth Scan

Use this prompt to kick off the search. Paste it directly into ChatGPT.
ChatGPT will read the repo, then do a live web search for buildings.

---

You are helping me find a new apartment.

My canonical project repo is at: https://github.com/jimmyjoy43/NewHomeSearchDocs

Read README.md and data/buildings.csv before doing anything else.

Task: Do a breadth-first scan of luxury apartments in Hollywood and West Hollywood.
Target zone: within 2.5 miles of 1540 Vine St, Hollywood CA 90028.
Rent range: $3,800 to $5,300 all-in.
Required: cat-friendly, in-unit laundry, gym, secure access, controlled parking.
Disqualifiers: AI-only leasing contact, 1-star maintenance reviews, known noise enforcement failures.

For each building you find, output one CSV row matching this exact schema:
building_name,address,neighborhood,url,unit_number,bed_bath,sqft,base_rent,net_effective_rent,available_date,lease_term_months,application_fee,admin_fee,security_deposit,parking_cost,pet_rent,cat_policy,in_unit_laundry,dishwasher,central_ac,package_room,controlled_access,gym,pool,coworking,conference_room,ev_charging,rooftop,quiet_score,management_score,amenity_score,adult_vibe_score,essential_amenities_all_yes,missing_essential_amenities,nice_to_have_yes_count,tour_date,deep_research_done,review_scan_done,news_scan_done,remarks,last_updated

Rules:
- Output only valid CSV rows after the header. No commentary between rows.
- Use today's date in YYYY-MM-DD format for last_updated.
- Leave fields empty if data is not available. Do not guess or invent values.
- For scores (quiet_score, management_score, amenity_score, adult_vibe_score): use 1-5.
  Leave blank if you cannot score from available data.
- Flag any building where management_score would be 2 or below with a note in remarks.
- For available_date: use YYYY-MM-DD format only. If the listing says
  "available now" or "immediate", use today's date in YYYY-MM-DD format.
  Never use the words "Now", "Immediate", "ASAP", or any non-date string.
  
After the CSV block, output a section called:
## Red flags summary
One line per building that has a flag. Format: "BuildingName: reason"
