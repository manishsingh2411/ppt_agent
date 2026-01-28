from google.adk.agents import Agent
from ppt_state import PPTState, create_empty_ppt_state, state_to_dict
from agents.ppt_initiator import ppt_initiator_agent
from agents.ppt_planner import ppt_planner_agent
from agents.ppt_refiner import ppt_refiner_agent
from agents.pptx_coder import pptx_coder_agent
import json


def route_user_input(user_input: str, current_state: PPTState = None) -> dict:
    """Routes user input to the appropriate agent based on intent.
    
    Args:
        user_input: User's input/request
        current_state: Current PPT state (if any)
        
    Returns:
        dict: Routing decision and next agent
    """
    # Simple routing logic based on keywords
    input_lower = user_input.lower()
    
    if not current_state or not current_state.ppt_title:
        # First time - use initiator
        return {
            "agent": "ppt_initiator",
            "reason": "Initial requirement analysis"
        }
    elif "download" in input_lower or "save" in input_lower or "get" in input_lower:
        # User wants the final file
        return {
            "agent": "pptx_coder",
            "reason": "User requested final PowerPoint file"
        }
    elif "add" in input_lower or "more" in input_lower or "include" in input_lower:
        # User wants to add content
        return {
            "agent": "ppt_planner",
            "reason": "User requested to add new content"
        }
    elif "change" in input_lower or "modify" in input_lower or "improve" in input_lower:
        # User wants to modify existing content
        return {
            "agent": "ppt_refiner",
            "reason": "User requested modifications"
        }
    elif "build" in input_lower or "generate" in input_lower or "create" in input_lower:
        # User wants to build slides
        return {
            "agent": "ppt_planner",
            "reason": "User requested to build/generate slides"
        }
    else:
        # Default to planner for new requirements
        return {
            "agent": "ppt_planner",
            "reason": "Default routing to planner"
        }


def process_with_agent(agent_name: str, user_input: str, state: PPTState) -> dict:
    """Process user input with the specified agent.
    
    Args:
        agent_name: Name of the agent to use
        user_input: User's input
        state: Current PPT state
        
    Returns:
        dict: Result from the agent
    """
    try:
        if agent_name == "ppt_initiator":
            # Use initiator agent
            result = ppt_initiator_agent.invoke({
                "user_input": user_input
            })
            return result
        
        elif agent_name == "ppt_planner":
            # Use planner agent
            result = ppt_planner_agent.invoke({
                "requirement": state.requirement_cleaned or user_input,
                "state": state_to_dict(state)
            })
            return result
        
        elif agent_name == "ppt_refiner":
            # Use refiner agent
            result = ppt_refiner_agent.invoke({
                "state": state_to_dict(state),
                "user_feedback": user_input
            })
            return result
        
        elif agent_name == "pptx_coder":
            # Use coder agent
            result = pptx_coder_agent.invoke({
                "state": state_to_dict(state)
            })
            return result
        
        else:
            return {
                "status": "error",
                "message": f"Unknown agent: {agent_name}"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing with {agent_name}: {str(e)}"
        }


def orchestrate_ppt_creation(user_input: str, current_state: PPTState = None) -> dict:
    """Main orchestration function that coordinates all agents.
    
    Args:
        user_input: User's input/request
        current_state: Current PPT state (if any)
        
    Returns:
        dict: Final result with updated state
    """
    # Initialize state if not provided
    if current_state is None:
        current_state = create_empty_ppt_state()
    
    # Route the input to appropriate agent
    routing = route_user_input(user_input, current_state)
    
    # Process with the selected agent
    result = process_with_agent(routing["agent"], user_input, current_state)
    
    # Update conversation history
    current_state.conversation_history.append({
        "user_input": user_input,
        "agent": routing["agent"],
        "reason": routing["reason"],
        "result": result
    })
    
    return {
        "status": "success",
        "agent_used": routing["agent"],
        "reason": routing["reason"],
        "result": result,
        "state": current_state
    }


# Create the Main Orchestrator Agent
ppt_orchestrator_agent = Agent(
    name="ppt_orchestrator",
    model="gemini-1.5-flash-002",
    description="Main orchestrator that coordinates all PPT creation agents.",
    instruction="""You are the main PPT creation orchestrator. Your job is to:
1. Analyze user input to determine intent
2. Route to the appropriate specialized agent
3. Coordinate the workflow between agents
4. Maintain conversation history and state

Available agents:
- ppt_initiator: For initial requirement analysis
- ppt_planner: For planning and structuring presentations
- ppt_refiner: For modifications and improvements
- pptx_coder: For generating the final PowerPoint file

Always respond with a JSON object containing:
- status: "success" or "error"
- agent_used: which agent was selected
- reason: why that agent was chosen
- result: output from the agent
- state: updated PPT state""",
    tools=[route_user_input, process_with_agent, orchestrate_ppt_creation]
) 