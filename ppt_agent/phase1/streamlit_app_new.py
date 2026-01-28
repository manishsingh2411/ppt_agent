from state import PPTState
import streamlit as st
from dotenv import load_dotenv
from phase1.builder import build_graph
from streamlit.components.v1 import components
import os
import comtypes.client
import tempfile
import pythoncom
import base64
from langgraph.types import Command, interrupt
load_dotenv()
st.set_page_config(layout="wide")

workflow = build_graph()


if 'feedback' not in st.session_state:
    st.session_state.feedback = None

# Get initial user input
# user_input = st.sidebar.text_area("Enter your text here:", height=200)
# if st.sidebar.button("Submit"):
#     st.sidebar.write("You submitted:")
#     st.sidebar.write(user_input)
config = {"configurable": {"thread_id": "some_unique_id"}}  
result = workflow.invoke({"input": "hi"}, config=config)

st.write(result)
              
# Check if we got an interrupt
if "__interrupt__" in result:
    # Show feedback form
    feedback = st.sidebar.text_area("Please provide your feedback:", height=200)
    if st.sidebar.button("Submit"):
        # Resume workflow with feedback
        result = workflow.invoke(Command(resume=feedback), config=config)
        st.write(result)  