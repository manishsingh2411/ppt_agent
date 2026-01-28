from google.adk.agents import Agent
from ppt_state import (
    PPTState, create_key_message, create_slide, 
    add_key_message_to_state, add_slide_to_state
)


def plan_presentation(requirement: str) -> dict:
    """Plans the presentation structure based on the requirement.
    
    Args:
        requirement: The cleaned requirement for the presentation
        
    Returns:
        dict: A dictionary containing the planned presentation structure
    """
    # This is a simplified version - in a real implementation, you'd use the LLM
    # to generate key messages and slide structure
    
    # Generate key messages based on requirement
    key_messages = [
        {
            "message": f"Introduction to {requirement.split()[0]}",
            "milestone_slide_number": 2
        },
        {
            "message": f"Key benefits and applications of {requirement.split()[0]}",
            "milestone_slide_number": 4
        },
        {
            "message": f"Future trends and conclusion for {requirement.split()[0]}",
            "milestone_slide_number": 6
        }
    ]
    
    # Generate slide structure
    slides = [
        {
            "key_message_part": key_messages[0]["message"],
            "title": f"Welcome to {requirement.split()[0]}",
            "content": f"An introduction to {requirement}",
            "message_here": f"Introduce {requirement.split()[0]}",
            "layout_description": "Title slide with main message"
        },
        {
            "key_message_part": key_messages[1]["message"],
            "title": f"Benefits of {requirement.split()[0]}",
            "content": "• Improved efficiency\n• Cost savings\n• Better outcomes",
            "message_here": "Show key benefits",
            "layout_description": "Bullet point layout"
        },
        {
            "key_message_part": key_messages[2]["message"],
            "title": "Conclusion",
            "content": f"Summary of {requirement}",
            "message_here": "Wrap up the presentation",
            "layout_description": "Summary slide"
        }
    ]
    
    return {
        "status": "success",
        "key_messages": key_messages,
        "slides": slides,
        "number_of_slides": len(slides)
    }


def update_ppt_state_with_plan(state: PPTState, plan: dict) -> dict:
    """Updates the PPT state with the planned structure.
    
    Args:
        state: Current PPT state
        plan: The planning result from plan_presentation
        
    Returns:
        dict: Updated state information
    """
    if plan["status"] == "success":
        # Add key messages
        for km_data in plan["key_messages"]:
            key_message = create_key_message(
                km_data["message"], 
                km_data["milestone_slide_number"]
            )
            add_key_message_to_state(state, key_message)
        
        # Add slides
        for slide_data in plan["slides"]:
            slide = create_slide(
                key_message_part=slide_data["key_message_part"],
                title=slide_data["title"],
                content=slide_data["content"],
                message_here=slide_data["message_here"],
                layout_description=slide_data["layout_description"]
            )
            add_slide_to_state(state, slide)
        
        state.current_agent = "ppt_planner"
        
        return {
            "status": "success",
            "state": state,
            "message": f"Planned presentation with {len(plan['slides'])} slides"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to plan presentation"
        }


# Create the PPT Planner Agent
ppt_planner_agent = Agent(
    name="ppt_planner",
    model="gemini-1.5-flash-002",
    description="Agent responsible for planning presentation structure with key messages and slides.",
    instruction="""You are a PPT planner. Your job is to:
1. Analyze the cleaned requirement
2. Generate key messages for the presentation
3. Create slide structure to deliver those messages
4. Update the PPT state with the plan

Always respond with a JSON object containing:
- status: "success" or "error"
- key_messages: list of key messages with milestone slide numbers
- slides: list of slide structures
- number_of_slides: total number of slides
- message: explanation of the plan""",
    tools=[plan_presentation, update_ppt_state_with_plan]
) 