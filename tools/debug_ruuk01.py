#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.scrape_cc_mapped as scraper

# Override GAMES to only run Animal Crossing
scraper.GAMES = {
    "Animal Crossing City Folk": {
        "post_id": "10507857",
        "regions": {"USA": "RUUE01", "EUR": "RUUP01", "JPN": "RUUJ01", "KOR": "RUUK01"}
    }
}

scraper.main()
