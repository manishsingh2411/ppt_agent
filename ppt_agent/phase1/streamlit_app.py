from state import PPTState
import streamlit as st
from dotenv import load_dotenv
from phase1.builder import build_graph
import os
import traceback
from langgraph.types import Command, interrupt

load_dotenv()
st.set_page_config(layout="wide")

# Add a simple test to ensure Streamlit is working
st.write("🚀 Streamlit app is running!")

# Build workflow with error handling
try:
    st.info("🔄 Building workflow...")
    workflow = build_graph()
    st.success("✅ Workflow built successfully")
except Exception as e:
    st.error(f"❌ Failed to build workflow: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Initialize session state
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

config = {"configurable": {"thread_id": "some_unique_id"}} 

# Initialize result with error handling
if "result" not in st.session_state:
    try:
        st.info("🔄 Initializing workflow...")
        result = workflow.invoke({"input": "hi"}, config=config)
        st.session_state.result = result
        st.success("✅ Workflow initialized successfully")
    except Exception as e:
        st.error(f"❌ Failed to initialize workflow: {e}")
        st.code(traceback.format_exc())
        # Set a safe default state
        st.session_state.result = {"__interrupt__": True, "messages": []}

# Create tabs
try:
    key_messages_tab, slides_tab, convertation_tab, others_tab = st.tabs(["Key Messages", "Slides", "Convertation", "Others"])
except Exception as e:
    st.error(f"❌ Failed to create tabs: {e}")
    st.stop()

# Debug sidebar
with st.sidebar:
    st.markdown("### 🔧 Debug Info")
    if st.session_state.result:
        st.write(f"Result keys: {list(st.session_state.result.keys())}")
        st.write(f"Has __interrupt__: {'__interrupt__' in st.session_state.result}")
        st.write(f"Result type: {type(st.session_state.result)}")
    else:
        st.write("No result in session state")

# Main chat interface
if "__interrupt__" in st.session_state.result:
    st.sidebar.markdown("### 💬 Chat")
    
    try:
        user_message = st.sidebar.chat_message("user")
        system_message = st.sidebar.chat_message("assistant")
        
        # Display existing messages with error handling
        if "messages" in st.session_state.result:
            for item in st.session_state.result["messages"]:
                try:
                    if getattr(item, "name", None) == "requirement":
                        user_message.write(item.content)
                    else:
                        system_message.write(item.content)
                except Exception as e:
                    st.sidebar.error(f"Error displaying message: {e}")
                    st.sidebar.code(traceback.format_exc())
        
        # Chat input
        prompt = st.sidebar.chat_input(
            "Say something and/or attach an image",
            accept_file=True,
            file_type=["jpg", "jpeg", "png"],
        )
        
        if prompt:
            try:
                # Get prompt text
                prompt_text = prompt.text if hasattr(prompt, 'text') else str(prompt)
                st.sidebar.info(f"🔄 Processing: {prompt_text}")
                
                # Add loading spinner and progress tracking
                with st.spinner("Processing your request..."):
                    st.sidebar.write("⏳ Invoking workflow...")
                    
                    # Resume workflow with comprehensive error handling
                    new_result = workflow.invoke(
                        Command(resume=prompt_text), 
                        config=config
                    )
                    
                    st.session_state.result = new_result
                    st.sidebar.success("✅ Request processed successfully")
                
                # Display results with comprehensive error handling
                try:
                    # Display key messages
                    if "key_messages" in st.session_state.result:
                        key_messages_tab.write("### Key Messages")
                        key_messages_tab.write(st.session_state.result["key_messages"])
                    else:
                        key_messages_tab.write("No key messages available")
                    
                    # Display slides
                    if "slides" in st.session_state.result:
                        slides_tab.write("### Slides")
                        slides_tab.write(st.session_state.result["slides"])
                    else:
                        slides_tab.write("No slides available")
                    
                    # Display conversation
                    if "messages" in st.session_state.result:
                        convertation_tab.write("### Conversation")
                        convertation_tab.write(st.session_state.result["messages"])
                    else:
                        convertation_tab.write("No messages available")
                    
                    # Display other information
                    others_tab.write("### Other Information")
                    
                    others_tab.write("**File Name:**")
                    others_tab.write(st.session_state.result.get("file_name", "N/A"))
                    
                    others_tab.write("**User Requirement:**")
                    others_tab.write(st.session_state.result.get("user_requirement", "N/A"))
                    
                    others_tab.write("**Requirement Cleaned:**")
                    others_tab.write(st.session_state.result.get("requirement_cleaned", "N/A"))
                    
                    others_tab.write("**PPT Title:**")
                    others_tab.write(st.session_state.result.get("ppt_title", "N/A"))
                    
                    others_tab.write("**Missing Information:**")
                    others_tab.write(st.session_state.result.get("missing_information", "N/A"))
                    
                    # Display progress information if available
                    if "current_slide_index" in st.session_state.result:
                        others_tab.write("**Progress Information:**")
                        others_tab.write(f"Current slide: {st.session_state.result.get('current_slide_index', 0)}")
                        others_tab.write(f"Total slides: {st.session_state.result.get('total_slides_to_process', 0)}")
                        others_tab.write(f"Progress: {st.session_state.result.get('slide_building_progress', 'N/A')}")
                    
                except Exception as e:
                    st.error(f"❌ Error displaying results: {e}")
                    st.code(traceback.format_exc())
                    
            except Exception as e:
                st.error(f"❌ Error processing request: {e}")
                st.code(traceback.format_exc())
                
                # Reset to a safe state
                st.session_state.result = {"__interrupt__": True, "messages": []}
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error in chat interface: {e}")
        st.code(traceback.format_exc())

else:
    st.warning("⚠️ Workflow not in interrupt state")
    st.write("Current result:", st.session_state.result)

# Add comprehensive debug section
with st.expander("🔍 Detailed Debug Information"):
    st.write("### Session State")
    st.write("Session State Keys:", list(st.session_state.keys()))
    
    st.write("### Current Result")
    st.write("Result Type:", type(st.session_state.result))
    st.write("Result Content:", st.session_state.result)
    
    st.write("### Environment Info")
    st.write("Python Version:", os.sys.version)
    st.write("Working Directory:", os.getcwd())
    
    # Test basic functionality
    st.write("### Basic Tests")
    try:
        st.write("✅ Streamlit rendering works")
        st.write("✅ Session state access works")
        if workflow:
            st.write("✅ Workflow object exists")
        else:
            st.write("❌ Workflow object is None")
    except Exception as e:
        st.write(f"❌ Basic test failed: {e}")

# Add a reset button for debugging
if st.sidebar.button("🔄 Reset Session State"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Add error boundary
if st.session_state.get('error_count', 0) > 3:
    st.error("❌ Too many errors occurred. Please refresh the page.")
    st.stop()