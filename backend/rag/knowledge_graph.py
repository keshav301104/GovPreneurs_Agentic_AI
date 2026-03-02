import networkx as nx
from typing import Dict, Any

class DynamicKnowledgeGraph:
    def __init__(self):
        # We start with a completely blank canvas for every request
        self.G = nx.Graph()

    def build_and_match(self, opportunity: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """
        Dynamically builds a graph from arbitrary user and government data, 
        then traverses it to find verified matches.
        """
        # --- 1. Map the Government Opportunity Nodes ---
        opp_id = opportunity.get("opportunity_id", "UNKNOWN_OPP")
        self.G.add_node(opp_id, type="Opportunity")

        opp_naics = opportunity.get("classification", {}).get("naics_code")
        if opp_naics:
            self.G.add_node(opp_naics, type="NAICS")
            self.G.add_edge(opp_id, opp_naics, relation="REQUIRES_NAICS")

        # --- 2. Map the User Profile Nodes ---
        company_name = user_profile.get("company_name", "Unknown Contractor")
        self.G.add_node(company_name, type="Contractor")

        # Dynamically map all past projects from the user's JSON
        for project in user_profile.get("past_performance", []):
            proj_name = project.get("project_name")
            self.G.add_node(proj_name, type="PastPerformance")
            self.G.add_edge(company_name, proj_name, relation="COMPLETED")

            # Link this specific project to the NAICS codes the user claims it used
            for naics in project.get("naics_codes", []):
                if not self.G.has_node(naics):
                    self.G.add_node(naics, type="NAICS")
                self.G.add_edge(proj_name, naics, relation="USED_NAICS")

        # --- 3. Graph Traversal (The Entity Resolution) ---
        matches = set()
        
        # Does the government's required NAICS code exist in our graph?
        if opp_naics and self.G.has_node(opp_naics):
            # Find all nodes connected to this required NAICS code
            for neighbor in self.G.neighbors(opp_naics):
                # If a connected node is a past project, verify the current company actually did it
                if self.G.nodes[neighbor].get("type") == "PastPerformance":
                    if self.G.has_edge(company_name, neighbor):
                        matches.add(neighbor)

        # --- 4. Format Output for the LLM ---
        if not matches:
            return "Graph Retrieval: No verified past performance directly maps to this opportunity's primary NAICS code."

        context = "GRAPH RETRIEVAL (VERIFIED PAST PERFORMANCE):\n"
        for match in matches:
            context += f"- {company_name} successfully executed '{match}', which directly maps to the required constraint (NAICS: {opp_naics}).\n"
        
        return context