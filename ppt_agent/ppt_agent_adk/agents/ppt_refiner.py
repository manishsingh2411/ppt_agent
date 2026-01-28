from google.adk.agents import Agent
from ppt_state import PPTState


def refine_presentation(state: PPTState, user_feedback: str) -> dict:
    """Refines the presentation based on user feedback.
    
    Args:
        state: Current PPT state
        user_feedback: User's feedback for modifications
        
    Returns:
        dict: Refined presentation structure
    """
    # This is a simplified version - in a real implementation, you'd use the LLM
    # to analyze feedback and make appropriate modifications
    
    # Basic refinement logic based on feedback keywords
    feedback_lower = user_feedback.lower()
    
    if "add" in feedback_lower or "more" in feedback_lower:
        # Add more content
        return {
            "status": "success",
            "action": "add_content",
            "message": "Adding more content based on feedback"
        }
    elif "change" in feedback_lower or "modify" in feedback_lower:
        # Modify existing content
        return {
            "status": "success",
            "action": "modify_content",
            "message": "Modifying existing content based on feedback"
        }
    elif "improve" in feedback_lower or "better" in feedback_lower:
        # Improve existing content
        return {
            "status": "success",
            "action": "improve_content",
            "message": "Improving content quality based on feedback"
        }
    else:
        return {
            "status": "success",
            "action": "general_refinement",
            "message": "General refinement applied"
        }


def apply_refinements(state: PPTState, refinements: dict) -> dict:
    """Applies refinements to the PPT state.
    
    Args:
        state: Current PPT state
        refinements: Refinement instructions
        
    Returns:
        dict: Updated state information
    """
    if refinements["status"] == "success":
        # Apply refinements based on action type
        action = refinements["action"]
        
        if action == "add_content":
            # Add a new slide
            from ppt_state import create_slide, add_slide_to_state
            new_slide = create_slide(
                title="Additional Information",
                content="Additional content based on feedback",
                message_here="Addressing user feedback",
                layout_description="Additional content slide"
            )
            add_slide_to_state(state, new_slide)
        
        elif action == "modify_content":
            # Modify existing slides
            if state.slides:
                state.slides[0].content += "\n\nModified based on feedback"
        
        elif action == "improve_content":
            # Improve existing content
            if state.slides:
                state.slides[0].content += "\n\nImproved content quality"
        
        state.current_agent = "ppt_refiner"
        
        return {
            "status": "success",
            "state": state,
            "message": f"Applied {action} refinements"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to apply refinements"
        }


# Create the PPT Refiner Agent
ppt_refiner_agent = Agent(
    name="ppt_refiner",
    model="gemini-1.5-flash-002",
    description="Agent responsible for refining and improving presentations based on user feedback.",
    instruction="""You are a PPT refiner. Your job is to:
1. Analyze user feedback for presentation modifications
2. Determine what changes are needed
3. Apply refinements to the presentation
4. Update the PPT state with improvements

Always respond with a JSON object containing:
- status: "success" or "error"
- action: type of refinement applied
- message: explanation of changes made""",
    tools=[refine_presentation, apply_refinements]
) 