from typing import List, Optional, TypedDict
from langgraph.graph import MessagesState

# === LANGGRAPH COMPATIBLE STATE DEFINITIONS ===

class KeyMessage(TypedDict):
    """Represents a key message to be delivered in the presentation"""
    message: str
    milestone_slide_number: int  # By which slide this message should be delivered

class Slide(TypedDict):
    """Individual slide representation"""
    which_key_message_this_slide_supports: str        # Which key message this slide supports
    title: str
    content: str
    image: Optional[str]         # Image path or description
    message_here: str           # Specific message for this slide
    layout_description: str
    slide_content : dict     # Manual layout instructions

class PPTState(MessagesState):
    """LangGraph compatible PPT state - User's simplified design"""
    file_name: str = ""
    user_requirement: str 
    requirement_cleaned: str
    ppt_title: str
    number_of_slides: int
    key_messages: List[KeyMessage]  # Sequence of (message, milestone_slide_number)
    slides: List[Slide]
    latest_response : str
    missing_information: str

# === HELPER FUNCTIONS FOR STATE MANAGEMENT ===

def create_empty_ppt_state() -> PPTState:
    """Create an empty PPT state for initialization"""
    
    return PPTState(
        file_name="",
        ppt_title="",
        number_of_slides=0,
        key_messages=[],
        slides=[]
    )

def create_key_message(message: str, milestone_slide: int) -> KeyMessage:
    """Helper to create a KeyMessage"""
    return KeyMessage(
        message=message,
        milestone_slide_number=milestone_slide
    )

def create_slide(
    key_message_part: str,
    title: str,
    content: str = "",
    image: Optional[str] = None,
    message_here: str = "",
    layout_description: str = "Standard content layout"
) -> Slide:
    """Helper to create a Slide"""
    return Slide(
        key_message_part=key_message_part,
        title=title,
        content=content,
        image=image,
        message_here=message_here,
        layout_description=layout_description
    )

def add_slide_to_state(state: PPTState, slide: Slide) -> PPTState:
    """Add a slide to the PPT state"""
    new_slides = state["slides"].copy()
    new_slides.append(slide)
    
    return {
        **state,
        "slides": new_slides
    }

def update_slide_count(state: PPTState) -> PPTState:
    """Update the slide count based on actual slides"""
    return {
        **state,
        "number_of_slides": len(state["slides"])
    }

# === USAGE EXAMPLES ===

def example_ppt_state() -> PPTState:
    """Example of how to create and populate PPT state"""
    
    # Initialize empty state
    state = create_empty_ppt_state()
    
    # Set basic info
    state["file_name"] = "ml_presentation.pptx"
    state["ppt_title"] = "Introduction to Machine Learning"
    
    # Add key messages
    key_messages = [
        create_key_message("ML transforms business operations", 3),
        create_key_message("Data quality is crucial for ML success", 6),
        create_key_message("Implementation requires strategic planning", 9)
    ]
    state["key_messages"] = key_messages
    
    # Add slides
    slide1 = create_slide(
        key_message_part="ML transforms business operations",
        title="Welcome to ML Transformation",
        content="Machine Learning is revolutionizing how businesses operate",
        message_here="Introduce the transformative power of ML",
        layout_description="Title slide with main message"
    )
    
    slide2 = create_slide(
        key_message_part="ML transforms business operations", 
        title="Key Benefits of ML",
        content="• Automation of repetitive tasks\n• Improved decision making\n• Enhanced customer experience",
        message_here="Show specific benefits",
        layout_description="Bullet point layout"
    )
    
    # Add slides to state
    state = add_slide_to_state(state, slide1)
    state = add_slide_to_state(state, slide2)
    
    # Update slide count
    state = update_slide_count(state)
    
    return state

if __name__ == "__main__":
    # Test the state creation
    test_state = example_ppt_state()
    print(f"PPT Title: {test_state['ppt_title']}")
    print(f"Number of slides: {test_state['number_of_slides']}")
    print(f"Key messages: {len(test_state['key_messages'])}")
    print(f"First slide title: {test_state['slides'][0]['title']}")

"""
# === ANALYSIS ===

BENEFITS of User's Approach:
✅ 1. SIMPLICITY: Easy to understand and implement
✅ 2. MESSAGE-DRIVEN: Ensures coherent narrative flow
✅ 3. MILESTONE-BASED: Guarantees key messages are delivered on time
✅ 4. MANUAL CONTROL: Flexibility in layout decisions
✅ 5. INCREMENTAL-FRIENDLY: Can build piece by piece
✅ 6. CLEAR STRUCTURE: Each component has obvious purpose

NOW LANGGRAPH COMPATIBLE:
✅ 7. TYPEDDICT FORMAT: Works directly with LangGraph state management
✅ 8. IMMUTABLE UPDATES: Helper functions follow LangGraph patterns
✅ 9. SERIALIZABLE: Can be passed between graph nodes
"""