from typing import Dict, Any, List

class DataNormalizer:
    @staticmethod
    def normalize_sam_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforms messy SAM.gov API responses into our clean GovPreneursOpportunity schema.
        """
        normalized_records = []
        
        for item in raw_data:
            normalized_record = {
                "opportunity_id": item.get("noticeId", "UNKNOWN"),
                "title": item.get("title", "Untitled Opportunity"),
                "agency": {
                    "department": item.get("department", "Unknown"),
                    "sub_tier": item.get("subTier", "Unknown")
                },
                "dates": {
                    "posted_date": item.get("postedDate", ""),
                    "response_deadline": item.get("responseDeadLine", ""),
                    "last_modified": item.get("modifiedDate", "")
                },
                "classification": {
                    "naics_code": item.get("naicsCode", ""),
                    "set_aside": item.get("typeOfSetAsideDescription", "None")
                },
                "description": item.get("description", ""),
                # Mocking the attachment extraction that would normally scrape the uiLink
                "attachments": [
                    {
                        "file_name": "solicitation_requirements.pdf",
                        "url": item.get("uiLink", "") + "/attachment/1",
                        "type": "solicitation"
                    }
                ],
                "status": "Active" if item.get("responseDeadLine") else "Unknown"
            }
            normalized_records.append(normalized_record)
            
        return normalized_records