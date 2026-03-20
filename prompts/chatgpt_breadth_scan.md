You are helping me find a new apartment.

My canonical project repo is at: [[GITHUB_REPO_URL](https://github.com/jimmyjoy43/NewHomeSearchDocs.git)]
Read README.md and data/buildings.csv before doing anything else.

Task: Do a breadth-first scan of luxury apartments in Hollywood and West Hollywood.
Target zone: within 1.5 miles of 1540 Vine St, Hollywood CA 90028.
Rent range: $3,800 to $5,300 all-in.
Required: cat-friendly, in-unit laundry, gym, secure access, controlled parking.
Disqualifiers: AI-only leasing contact, 1-star maintenance reviews, known noise enforcement failures.

For each building you find, output a CSV row matching this schema exactly:
building_name,address,neighborhood,url,unit_number,bed_bath,sqft,base_rent,net_effective_rent,available_date,lease_term_months,application_fee,admin_fee,security_deposit,parking_cost,pet_rent,cat_policy,in_unit_laundry,dishwasher,central_ac,package_room,controlled_access,gym,pool,coworking,conference_room,ev_charging,rooftop,quiet_score,management_score,amenity_score,adult_vibe_score,essential_amenities_all_yes,missing_essential_amenities,nice_to_have_yes_count,tour_date,deep_research_done,review_scan_done,news_scan_done,remarks,last_updated

Do not add commentary between rows. Output only valid CSV rows.
Flag any building where management_score would be 2 or below, with a one-line reason.