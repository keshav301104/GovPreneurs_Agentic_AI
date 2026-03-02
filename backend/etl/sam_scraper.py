import os
import requests
from typing import List, Dict, Any

class SAMGovScraper:
    def __init__(self):
        # In a real app, this comes from backend/.env
        self.api_key = os.getenv("SAM_GOV_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.sam.gov/opportunities/v2/search"

    def fetch_opportunities(self, naics_code: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches active contract opportunities from SAM.gov based on NAICS code.
        """
        print(f"Initiating SAM.gov API call for NAICS: {naics_code}...")
        
        params = {
            "api_key": self.api_key,
            "postedFrom": "01/01/2026", # Using recent dates
            "postedTo": "03/01/2026",
            "naicsCode": naics_code,
            "ptype": "o", # 'o' for pre-solicitation/solicitation
            "limit": limit
        }

        # For the sake of the case study, we will simulate the exact JSON response 
        # SAM.gov returns, so the pipeline can actually run without waiting for api key approval.
        if self.api_key == "DEMO_KEY":
            return self._mock_sam_response()

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("opportunitiesData", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from SAM.gov: {e}")
            return []

    def _mock_sam_response(self) -> List[Dict[str, Any]]:
        """Simulates raw, messy government data for our normalizer to clean."""
        return [
            {
                "noticeId": "7a8b9c0d1e2f3g4h",
                "title": "Advanced Security Systems Upgrade",
                "department": "Department of Defense",
                "subTier": "Department of the Army",
                "postedDate": "2026-02-15T10:00:00Z",
                "responseDeadLine": "2026-03-30T17:00:00Z",
                "naicsCode": "541512",
                "typeOfSetAsideDescription": "Total Small Business Set-Aside (FAR 19.5)",
                "description": "The Department of the Army requires advanced access control and perimeter security upgrades...",
                "uiLink": "https://sam.gov/opp/7a8b9c0d1e2f3g4h/view"
            }
        ]