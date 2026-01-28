from google.adk.agents import Agent
from ppt_state import PPTState, create_empty_ppt_state
import json

def analyze_requirement(user_input: str) -> dict:
    """Analyzes and cleans the user's initial requirement for PPT creation.
    
    Args:
        user_input: The user's raw requirement text
        
    Returns:
        dict: A dictionary containing cleaned requirement, file name, and title
    """
    # This is a simplified version - in a real implementation, you'd use the LLM
    # to analyze and clean the requirement
    
    # Basic cleaning logic
    cleaned_requirement = user_input.strip()
    
    # Generate file name from requirement
    words = cleaned_requirement.split()[:5]  # Take first 5 words
    file_name = "_".join(words).lower().replace(" ", "_") + ".pptx"
    
    # Generate title from requirement
    title = cleaned_requirement.title()
    
    return {
        "status": "success",
        "file_name": file_name,
        "title_of_ppt": title,
        "requirement_cleaned": cleaned_requirement
    }

def create_ppt_state(user_input: str) -> dict:
    """Creates initial PPT state from user input.
    
    Args:
        user_input: The user's requirement
        
    Returns:
        dict: A dictionary containing the initial PPT state
    """
    # Analyze the requirement
    analysis = analyze_requirement(user_input)
    
    if analysis["status"] == "success":
        # Create initial state
        state = create_empty_ppt_state()
        state.user_requirement = user_input
        state.requirement_cleaned = analysis["requirement_cleaned"]
        state.file_name = analysis["file_name"]
        state.ppt_title = analysis["title_of_ppt"]
        state.current_agent = "ppt_initiator"
        
        return {
            "status": "success",
            "state": state,
            "message": f"Initialized PPT creation for: {analysis['title_of_ppt']}"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to analyze requirement"
        }

# Create the PPT Initiator Agent
ppt_initiator_agent = Agent(
    name="ppt_initiator",
    model="gemini-1.5-flash-002",
    description="Agent responsible for analyzing and cleaning user requirements for PPT creation.",
    instruction="""You are a PPT requirement analyzer. Your job is to:
1. Understand the user's requirement for a presentation
2. Clean and structure the requirement
3. Generate appropriate file name and title
4. Create initial PPT state

Always respond with a JSON object containing:
- status: "success" or "error"
- file_name: suggested filename
- title_of_ppt: presentation title
- requirement_cleaned: cleaned requirement text
- message: explanation of what was done""",
    tools=[analyze_requirement, create_ppt_state]
) 