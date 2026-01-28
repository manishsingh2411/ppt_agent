from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json

# === ADK COMPATIBLE STATE DEFINITIONS ===

@dataclass
class KeyMessage:
    """Represents a key message to be delivered in the presentation"""
    message: str
    milestone_slide_number: int  # By which slide this message should be delivered

@dataclass
class Slide:
    """Individual slide representation"""
    key_message_part: str = ""        # Which key message this slide supports
    title: str = ""
    content: str = ""
    image: Optional[str] = None       # Image path or description
    message_here: str = ""           # Specific message for this slide
    layout_description: str = "Standard content layout"

@dataclass
class PPTState:
    """ADK compatible PPT state - User's simplified design"""
    file_name: str = ""
    user_requirement: str = ""
    requirement_cleaned: str = ""
    ppt_title: str = ""
    number_of_slides: int = 0
    key_messages: List[KeyMessage] = field(default_factory=list)
    slides: List[Slide] = field(default_factory=list)
    latest_response: str = ""
    missing_information: str = ""
    current_agent: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)

# === HELPER FUNCTIONS FOR STATE MANAGEMENT ===

def create_empty_ppt_state() -> PPTState:
    """Create an empty PPT state for initialization"""
    return PPTState()

def create_key_message(message: str, milestone_slide: int) -> KeyMessage:
    """Helper to create a KeyMessage"""
    return KeyMessage(message=message, milestone_slide_number=milestone_slide)

def create_slide(
    key_message_part: str = "",
    title: str = "",
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
    state.slides.append(slide)
    state.number_of_slides = len(state.slides)
    return state

def add_key_message_to_state(state: PPTState, key_message: KeyMessage) -> PPTState:
    """Add a key message to the PPT state"""
    state.key_messages.append(key_message)
    return state

def state_to_dict(state: PPTState) -> Dict[str, Any]:
    """Convert PPTState to dictionary for JSON serialization"""
    return {
        "file_name": state.file_name,
        "user_requirement": state.user_requirement,
        "requirement_cleaned": state.requirement_cleaned,
        "ppt_title": state.ppt_title,
        "number_of_slides": state.number_of_slides,
        "key_messages": [
            {
                "message": km.message,
                "milestone_slide_number": km.milestone_slide_number
            } for km in state.key_messages
        ],
        "slides": [
            {
                "key_message_part": slide.key_message_part,
                "title": slide.title,
                "content": slide.content,
                "image": slide.image,
                "message_here": slide.message_here,
                "layout_description": slide.layout_description
            } for slide in state.slides
        ],
        "latest_response": state.latest_response,
        "missing_information": state.missing_information,
        "current_agent": state.current_agent,
        "conversation_history": state.conversation_history
    }

def dict_to_state(data: Dict[str, Any]) -> PPTState:
    """Convert dictionary back to PPTState"""
    state = PPTState()
    state.file_name = data.get("file_name", "")
    state.user_requirement = data.get("user_requirement", "")
    state.requirement_cleaned = data.get("requirement_cleaned", "")
    state.ppt_title = data.get("ppt_title", "")
    state.number_of_slides = data.get("number_of_slides", 0)
    state.latest_response = data.get("latest_response", "")
    state.missing_information = data.get("missing_information", "")
    state.current_agent = data.get("current_agent", "")
    state.conversation_history = data.get("conversation_history", [])
    
    # Convert key messages
    for km_data in data.get("key_messages", []):
        state.key_messages.append(create_key_message(
            km_data["message"], 
            km_data["milestone_slide_number"]
        ))
    
    # Convert slides
    for slide_data in data.get("slides", []):
        state.slides.append(create_slide(
            key_message_part=slide_data.get("key_message_part", ""),
            title=slide_data.get("title", ""),
            content=slide_data.get("content", ""),
            image=slide_data.get("image"),
            message_here=slide_data.get("message_here", ""),
            layout_description=slide_data.get("layout_description", "Standard content layout")
        ))
    
    return state

def save_state_to_file(state: PPTState, filename: str) -> None:
    """Save PPT state to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(state_to_dict(state), f, indent=2)

def load_state_from_file(filename: str) -> PPTState:
    """Load PPT state from a JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return dict_to_state(data)

# === USAGE EXAMPLES ===

def example_ppt_state() -> PPTState:
    """Example of how to create and populate PPT state"""
    
    # Initialize empty state
    state = create_empty_ppt_state()
    
    # Set basic info
    state.file_name = "ml_presentation.pptx"
    state.ppt_title = "Introduction to Machine Learning"
    
    # Add key messages
    key_messages = [
        create_key_message("ML transforms business operations", 3),
        create_key_message("Data quality is crucial for ML success", 6),
        create_key_message("Implementation requires strategic planning", 9)
    ]
    for km in key_messages:
        add_key_message_to_state(state, km)
    
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
    add_slide_to_state(state, slide1)
    add_slide_to_state(state, slide2)
    
    return state

if __name__ == "__main__":
    # Test the state creation
    test_state = example_ppt_state()
    print(f"PPT Title: {test_state.ppt_title}")
    print(f"Number of slides: {test_state.number_of_slides}")
    print(f"Key messages: {len(test_state.key_messages)}")
    print(f"First slide title: {test_state.slides[0].title}")
    
    # Test serialization
    state_dict = state_to_dict(test_state)
    print(f"Serialized state keys: {list(state_dict.keys())}")
    
    # Test deserialization
    restored_state = dict_to_state(state_dict)
    print(f"Restored state title: {restored_state.ppt_title}") 