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
# chat_container, content_container = st.columns(2)
key_messages_tab, slides_tab, convertation_tab, others_tab = st.tabs(["Key Messages", "Slides", "Convertation", "Others"])



if 'feedback' not in st.session_state:
    st.session_state.feedback = None
config = {"configurable": {"thread_id": "some_unique_id"}} 

if "result" not in st.session_state:
    result = workflow.invoke({"input": "hi"}, config=config)
    st.session_state.result = result

# Streamlit's chat_input is always rendered at the bottom of the page by default.
# To ensure the chat input stays at the bottom, do not place it inside a container or column.
# Instead, use it outside of the columns, and use the chat_container only for displaying messages.

if "__interrupt__" in st.session_state.result:
    user_message = st.sidebar.chat_message("user")
    system_message = st.sidebar.chat_message("assistant")
# Place chat_input outside the columns to keep it at the bottom
    prompt = st.sidebar.chat_input(
        "Say something and/or attach an image",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
    )
    if prompt:
        if "messages" in st.session_state.result:
            for item in st.session_state.result["messages"]:
                # Use getattr() to safely access the name attribute
                if getattr(item, "name", None) == "requirement":
                    user_message.write(item.content)
                else:
                    system_message.write(item.content)
                    # system_message.write(item.name)
        # Access the text content from ChatInputValue
        prompt_text = prompt.text if hasattr(prompt, 'text') else str(prompt)
        st.sidebar.write("Working On: " + prompt_text)
        
        # Resume workflow with the text content
        st.session_state.result = workflow.invoke(Command(resume=prompt_text), config=config)
        print(st.session_state.result)
        try:
            key_messages = st.session_state.result["key_messages"]
            slides = st.session_state.result["slides"]
            convertation = st.session_state.result["messages"]
            key_messages_tab.write(key_messages)
            slides_tab.write(slides)
            convertation_tab.write(convertation)
            others_tab.write(st.session_state.result["file_name"])
            others_tab.write(st.session_state.result["user_requirement"])
            others_tab.write(st.session_state.result["requirement_cleaned"])
            others_tab.write(st.session_state.result["ppt_title"])
            others_tab.write(st.session_state.result["missing_information"])
        except Exception as e:
            st.write(e)
        # if "messages" in st.session_state.result:
        #     for item in st.session_state.result["messages"][:-1]:
        #         # Use getattr() to safely access the name attribute
        #         if getattr(item, "name", None) == "requirement":
        #             user_message.write(item.content)

        