import os
from openai import OpenAI

class ProposalEvaluator:
    def __init__(self):
        # Using your local Ollama setup for zero-cost, private evaluation
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama" 
        )
        self.model_name = "llama3" # Or mistral

    def _get_evaluator_prompt(self) -> str:
        return """
        You are an elite Government Compliance Auditor. Your job is to review AI-generated proposals for strict compliance and hallucination detection.
        
        Compare the [GENERATED DRAFT] against the [ORIGINAL RFP CONSTRAINTS].
        
        Rules for Evaluation:
        1. NO HALLUCINATIONS: Did the draft invent any past performance, metrics, or certifications?
        2. MISSING INFO: Did the draft properly flag missing requirements using the [REQUIRES USER INPUT] tag?
        3. TONE: Is the tone professional and free of marketing fluff?
        
        Output your evaluation strictly as a short JSON object:
        {
            "compliance_score": (0-100),
            "hallucinations_detected": true/false,
            "auditor_notes": "Brief explanation of any issues found."
        }
        """

    def evaluate_draft(self, draft_text: str, rfp_chunks: str) -> str:
        """Acts as a Red Team agent to audit the generated proposal."""
        print(f"Initiating local AI compliance audit using {self.model_name}...")
        
        system_prompt = self._get_evaluator_prompt()
        user_prompt = f"[ORIGINAL RFP CONSTRAINTS]\n{rfp_chunks}\n\n[GENERATED DRAFT]\n{draft_text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0 # Maximum strictness for auditing
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Evaluator Error: {e}")
            return '{"compliance_score": 0, "hallucinations_detected": true, "auditor_notes": "Audit failed to run."}'