#!/usr/bin/env python3
"""
Test script for the ADK multi-agent PPT creation system.
This demonstrates the basic workflow without requiring the full ADK setup.
"""

from ppt_state import create_empty_ppt_state, create_key_message, create_slide, add_slide_to_state
from ppt_orchestrator import route_user_input, orchestrate_ppt_creation


def test_basic_workflow():
    """Test the basic PPT creation workflow."""
    print("🚀 Testing ADK Multi-Agent PPT System")
    print("=" * 50)
    
    # Test 1: Initial requirement
    print("\n📝 Test 1: Initial Requirement")
    print("-" * 30)
    
    user_input = "Create a presentation about artificial intelligence in healthcare"
    print(f"User Input: {user_input}")
    
    # Route the input
    routing = route_user_input(user_input)
    print(f"Routing Decision: {routing['agent']}")
    print(f"Reason: {routing['reason']}")
    
    # Test 2: Add content
    print("\n📝 Test 2: Add Content")
    print("-" * 30)
    
    # Create a basic state
    state = create_empty_ppt_state()
    state.ppt_title = "AI in Healthcare"
    state.file_name = "ai_healthcare.pptx"
    
    user_input = "Add slides about machine learning applications"
    print(f"User Input: {user_input}")
    
    routing = route_user_input(user_input, state)
    print(f"Routing Decision: {routing['agent']}")
    print(f"Reason: {routing['reason']}")
    
    # Test 3: Modify content
    print("\n📝 Test 3: Modify Content")
    print("-" * 30)
    
    user_input = "Change the title to be more specific"
    print(f"User Input: {user_input}")
    
    routing = route_user_input(user_input, state)
    print(f"Routing Decision: {routing['agent']}")
    print(f"Reason: {routing['reason']}")
    
    # Test 4: Download
    print("\n📝 Test 4: Download")
    print("-" * 30)
    
    user_input = "Download the presentation"
    print(f"User Input: {user_input}")
    
    routing = route_user_input(user_input, state)
    print(f"Routing Decision: {routing['agent']}")
    print(f"Reason: {routing['reason']}")
    
    print("\n✅ All routing tests completed!")


def test_state_management():
    """Test the state management functionality."""
    print("\n🔧 Testing State Management")
    print("=" * 50)
    
    # Create empty state
    state = create_empty_ppt_state()
    print(f"Empty state created: {state.ppt_title}")
    
    # Add key messages
    km1 = create_key_message("AI transforms healthcare", 2)
    km2 = create_key_message("Machine learning improves diagnostics", 4)
    state.key_messages.append(km1)
    state.key_messages.append(km2)
    print(f"Added {len(state.key_messages)} key messages")
    
    # Add slides
    slide1 = create_slide(
        title="Introduction to AI in Healthcare",
        content="Artificial Intelligence is revolutionizing healthcare...",
        message_here="Introduce the topic"
    )
    slide2 = create_slide(
        title="Machine Learning Applications",
        content="• Medical imaging analysis\n• Drug discovery\n• Patient monitoring",
        message_here="Show specific applications"
    )
    
    add_slide_to_state(state, slide1)
    add_slide_to_state(state, slide2)
    print(f"Added {state.number_of_slides} slides")
    
    # Test serialization
    from ppt_state import state_to_dict, dict_to_state
    state_dict = state_to_dict(state)
    print(f"State serialized with {len(state_dict)} keys")
    
    # Test deserialization
    restored_state = dict_to_state(state_dict)
    print(f"State restored: {restored_state.ppt_title}")
    print(f"Restored slides: {restored_state.number_of_slides}")
    
    print("✅ State management tests completed!")


def test_agent_simulation():
    """Simulate agent interactions without actual ADK calls."""
    print("\n🤖 Testing Agent Simulation")
    print("=" * 50)
    
    # Simulate initiator agent
    print("\n📋 Initiator Agent Simulation")
    user_input = "Create a presentation about renewable energy"
    
    # Simulate initiator response
    initiator_response = {
        "status": "success",
        "file_name": "renewable_energy.pptx",
        "title_of_ppt": "Renewable Energy",
        "requirement_cleaned": "Create a presentation about renewable energy",
        "message": "Initialized PPT creation for: Renewable Energy"
    }
    print(f"Input: {user_input}")
    print(f"Response: {initiator_response}")
    
    # Simulate planner agent
    print("\n📋 Planner Agent Simulation")
    planner_response = {
        "status": "success",
        "key_messages": [
            {"message": "Renewable energy is the future", "milestone_slide_number": 2},
            {"message": "Solar and wind are leading technologies", "milestone_slide_number": 4},
            {"message": "Implementation requires investment", "milestone_slide_number": 6}
        ],
        "slides": [
            {
                "title": "Welcome to Renewable Energy",
                "content": "An introduction to renewable energy sources",
                "message_here": "Introduce renewable energy",
                "layout_description": "Title slide"
            }
        ],
        "number_of_slides": 1,
        "message": "Planned presentation with 1 slides"
    }
    print(f"Response: {planner_response}")
    
    # Simulate refiner agent
    print("\n📋 Refiner Agent Simulation")
    user_feedback = "Add more details about solar energy"
    refiner_response = {
        "status": "success",
        "action": "add_content",
        "message": "Adding more content based on feedback"
    }
    print(f"Feedback: {user_feedback}")
    print(f"Response: {refiner_response}")
    
    # Simulate coder agent
    print("\n📋 Coder Agent Simulation")
    coder_response = {
        "status": "success",
        "filename": "renewable_energy.pptx",
        "message": "Successfully created renewable_energy.pptx"
    }
    print(f"Response: {coder_response}")
    
    print("✅ Agent simulation tests completed!")


def main():
    """Run all tests."""
    try:
        test_basic_workflow()
        test_state_management()
        test_agent_simulation()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📚 Next Steps:")
        print("1. Install required packages: pip install -r requirements.txt")
        print("2. Set up Google ADK credentials")
        print("3. Run the Streamlit app: streamlit run streamlit_app.py")
        print("4. Or test individual agents with actual ADK calls")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 