SYSTEM = """
You are a Security Architecture advisor reviewing a SOC incident.
"""

def build_prompt(extracted_context: str, soc_narrative: str, dr_actions: str) -> str:
    return f"""Based in this incident, recommend targeted security improvements. 
            EXTRACTED CONTEXT: 
             {extracted_context}

            SOC A
           """ 

