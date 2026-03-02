from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Simulating a strict government document
content = """
SECTION C - DESCRIPTION/SPECIFICATIONS/STATEMENT OF WORK
The Department of Defense requires an advanced perimeter security system. 

SECTION L - INSTRUCTIONS TO OFFERORS
The contractor must provide proof of integration with existing military infrastructure.
CRITICAL EVALUATION FACTOR: The proposed solution MUST explicitly be certified for FIPS 201 compliance. 
Offers missing FIPS 201 certification will be immediately rejected.

SECTION M - EVALUATION CRITERIA
1. Technical Capability: Demonstrated understanding of secure access controls.
2. Past Performance: Must show successful deployment in a federal environment within the last 3 years.
"""

for line in content.split('\n'):
    pdf.cell(200, 10, txt=line, ln=True, align='L')

# Save it to a new data folder
os.makedirs("data", exist_ok=True)
pdf_path = "data/mock_solicitation.pdf"
pdf.output(pdf_path)
print(f"Mock RFP PDF created at: {pdf_path}")