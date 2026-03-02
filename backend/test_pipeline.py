import requests
import json
import time

# Make sure your FastAPI server is running (uvicorn app.main:app --reload)
API_URL = "http://127.0.0.1:8000/api/generate-proposal"

# This is the exact payload Next.js will send
payload = {
    "opportunity_id": "SAM_12345",
    "pdf_path": "data/mock_solicitation.pdf",
    "user_profile": {
        "company_name": "SafeGuard Security",
        "capabilities_statement": "SafeGuard provides elite perimeter defense and logical access control systems for high-security environments.",
        "past_performance": [
            {
                "project_name": "Project Alpha - Fort Bragg",
                "naics_codes": ["541512"],
                "standards": ["FIPS 201"] # Watch the Knowledge Graph find this!
            },
            {
                "project_name": "Project Beta - Commercial Bank",
                "naics_codes": ["561621"],
                "standards": ["ISO 9001"]
            }
        ]
    }
}

print("Firing test request to multi-agent LangGraph backend...")
print("This may take 1-2 minutes depending on your local Llama 3 speed and if the AI argues with itself.")
start_time = time.time()

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    
    data = response.json()
    end_time = time.time()
    
    print(f"\n=== TEST COMPLETE IN {round(end_time - start_time, 2)} SECONDS ===")
    print(f"Iterations Required: {data['iterations_required']}")
    print(f"Final Auditor Score: {data['final_compliance_score']}/100")
    print(f"Auditor Notes: {data['auditor_notes']}")
    print("\n=== GENERATED PROPOSAL DRAFT ===")
    print(data['draft_proposal'])

except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
    if response is not None:
        print(f"\n[HIDDEN SERVER ERROR DETAIL] -> {response.text}")