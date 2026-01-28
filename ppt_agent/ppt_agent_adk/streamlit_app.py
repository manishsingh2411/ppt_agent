import streamlit as st
from ppt_orchestrator import orchestrate_ppt_creation
from ppt_state import create_empty_ppt_state, state_to_dict
import json


def main():
    st.set_page_config(
        page_title="PPT Agent ADK",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 PPT Creation Agent (ADK)")
    st.markdown("Create presentations using Google ADK multi-agent system")
    
    # Initialize session state
    if "ppt_state" not in st.session_state:
        st.session_state.ppt_state = create_empty_ppt_state()
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        if st.button("🔄 Reset Session"):
            st.session_state.ppt_state = create_empty_ppt_state()
            st.session_state.conversation = []
            st.rerun()
        
        if st.button("💾 Save State"):
            from ppt_state import save_state_to_file
            save_state_to_file(st.session_state.ppt_state, "ppt_state.json")
            st.success("State saved to ppt_state.json")
        
        if st.button("📂 Load State"):
            from ppt_state import load_state_from_file
            try:
                st.session_state.ppt_state = load_state_from_file("ppt_state.json")
                st.success("State loaded from ppt_state.json")
                st.rerun()
            except FileNotFoundError:
                st.error("No saved state found")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Display conversation history
        for i, conv in enumerate(st.session_state.conversation):
            with st.chat_message("user"):
                st.write(f"**You:** {conv['user_input']}")
            
            with st.chat_message("assistant"):
                st.write(f"**Agent:** {conv['agent']}")
                st.write(f"**Reason:** {conv['reason']}")
                if conv['result'].get('message'):
                    st.write(f"**Result:** {conv['result']['message']}")
        
        # Chat input
        user_input = st.chat_input("Enter your request...")
        
        if user_input:
            # Add user message to conversation
            st.session_state.conversation.append({
                "user_input": user_input,
                "agent": "user",
                "reason": "User input",
                "result": {}
            })
            
            # Process with orchestrator
            with st.spinner("Processing your request..."):
                result = orchestrate_ppt_creation(
                    user_input, 
                    st.session_state.ppt_state
                )
            
            # Update state
            if result["status"] == "success":
                st.session_state.ppt_state = result["state"]
                st.session_state.conversation.append({
                    "user_input": user_input,
                    "agent": result["agent_used"],
                    "reason": result["reason"],
                    "result": result["result"]
                })
            
            st.rerun()
    
    with col2:
        st.header("📋 Current State")
        
        # Display current state information
        state = st.session_state.ppt_state
        
        st.subheader("📄 Basic Info")
        st.write(f"**Title:** {state.ppt_title or 'Not set'}")
        st.write(f"**File:** {state.file_name or 'Not set'}")
        st.write(f"**Slides:** {state.number_of_slides}")
        st.write(f"**Current Agent:** {state.current_agent or 'None'}")
        
        if state.key_messages:
            st.subheader("🎯 Key Messages")
            for i, km in enumerate(state.key_messages):
                st.write(f"{i+1}. {km.message} (Slide {km.milestone_slide_number})")
        
        if state.slides:
            st.subheader("📑 Slides")
            for i, slide in enumerate(state.slides):
                with st.expander(f"Slide {i+1}: {slide.title}"):
                    st.write(f"**Content:** {slide.content}")
                    st.write(f"**Message:** {slide.message_here}")
                    st.write(f"**Layout:** {slide.layout_description}")
    
    # Debug information
    with st.expander("🔍 Debug Information"):
        st.json(state_to_dict(st.session_state.ppt_state))


if __name__ == "__main__":
    main() 