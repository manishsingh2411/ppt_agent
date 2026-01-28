from dotenv import load_dotenv
import logging
import json
import re
import textwrap
import os
from typing import Annotated, Literal

from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langgraph.types import Command, interrupt
from phase1.config.agents import AGENT_LLM_MAP
from phase1.prompts.template import get_prompt_template
from phase1.state import PPTState, create_key_message, create_slide
from phase1.llm import get_llm_by_type
logger = logging.getLogger(__name__)
load_dotenv()


def extract_code_from_response(response_text):
    """
    Returns the code between ##########THE CODE STRATS HERE########## and ##########THE CODE ENDS HERE##########
    as a string, or an empty string if not found.
    """
    pattern = (
        r"##########THE CODE STRATS HERE##########(.*?)##########THE CODE ENDS HERE##########"
    )
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def parse_llm_json(response_str):
    """Extract JSON from markdown code blocks and return as dictionary"""
    # Remove markdown code blocks
    json_str = re.sub(r"```json\n?|```\n?", "", response_str).strip()
    return json.loads(json_str)


def ppt_initiator_node(
    state: PPTState,
) -> Command[Literal["ppt_planner_node"]]:
    logger.info("Gathering Requirment ...")

    model = get_llm_by_type(AGENT_LLM_MAP["ppt_initiator"])

    ppt_initiator_response = model.invoke(
        [
            SystemMessage(content=get_prompt_template("ppt_initiator")),
            HumanMessage(content=state["user_requirement"]),
        ],
    )
    # to do look for mechanism that, if the response is not json, then retry the same prompt again
    # you need to see how do you couple it so that the if parsing fails, how llm will be called again
    parsed_response = parse_llm_json(ppt_initiator_response.content)

    return Command(
        update={
            "file_name": parsed_response["file_name"],
            "ppt_title": parsed_response["title_of_ppt"],
            "requirement_cleaned": parsed_response["requirement_cleaned"],
        },
        goto="ppt_planner_node",
    )



def user_input_node(
    state: PPTState,
) -> Command[Literal["user_task_manager_node"]]:
    logger.info("Getting user input ...")
    model = get_llm_by_type(AGENT_LLM_MAP["user_input"])
    initial_requirements = interrupt("Please Give you requirements for the PPT.")

    return Command(
        update={
            "messages": [
                HumanMessage(content=initial_requirements, name="requirement")
            ]
        },
        goto="user_task_manager_node",
    )


def user_task_manager_node(
    state: PPTState,
) -> Command[Literal["user_input_node", "__end__"]]:
    logger.info("Routing task ...")
    model = get_llm_by_type(AGENT_LLM_MAP["user_task_manager"])
    # The state is expected to have a "messages" field (list of HumanMessage/AIMessage/etc)
    messages = state.get("messages", [])
    file_name = state.get("file_name", "")
    requirement_contents = [
        msg.content
        for msg in messages
        if isinstance(msg, HumanMessage) and getattr(msg, "name", None) == "requirement"
    ]
    # TODO:cheeck if overall requirmenet makes sense and the last requirment makes sense
    # TODO: if the last requirment is not clear, ask for more input, and got to user_input_node
    if len(file_name) == 0:
        return Command(
            update={"user_requirement": str(requirement_contents),
                    "messages": [
                        SystemMessage(
                            content="Calling PPT Initiator",
                            name="action",
                        )
                    ]},
            goto="ppt_initiator_node",
        )

    user_task_manage_response = model.invoke(
        [
            SystemMessage(content=get_prompt_template("user_task_manager")),
            HumanMessage(content=str({
                    "ppt_content": state["slides"],
                    "user_requirment": requirement_contents,
                })),
        ],
    )
    print("USER TASK MANAGE RESPONSE", user_task_manage_response.content)
    user_task_manage_response_parsed = parse_llm_json(
        user_task_manage_response.content
    )

    if user_task_manage_response_parsed["status"] == "call_agent":
        if user_task_manage_response_parsed["agent"] == "ppt_planner":
            return Command(
                update={
                    "requirement_cleaned": user_task_manage_response_parsed[
                        "cleaned_requirement"
                    ],
                    "user_requirement": str(requirement_contents),
                    "messages": [
                        SystemMessage(
                            content="Calling PPT Planner : " + str(user_task_manage_response_parsed),
                            name="action",
                            
                        )
                    ]
                },
                goto="ppt_planner_node",
            )
        elif user_task_manage_response_parsed["agent"] == "ppt_refiner":
            return Command(
                update={
                    "user_requirement": str(requirement_contents),
                    "messages": [
                        SystemMessage(
                            content="Calling PPT Refiner : " + str(user_task_manage_response_parsed),
                            name="action",
                        ),
                    ]
                },
                goto="ppt_refiner_node",
            )
        elif user_task_manage_response_parsed["agent"] == "pptx_coder":
            return Command(
                update={
                    
                    "messages": [
                        SystemMessage(
                            content="Preperaring PPT for download: " + str(user_task_manage_response_parsed),
                            name="action",
                        ),
                    ]
                },
                goto="pptx_coder_node",
            )
        elif user_task_manage_response_parsed["agent"] == "slide_builder":
            return Command(
                update={
                    
                    "messages": [
                        SystemMessage(
                            content="Building the Slides : " + str(user_task_manage_response_parsed),
                            name="action",
                        ),
                    ]
                },
                goto="slide_builder_node",
            )   
        else:
            
            return Command(update={
                    
                    "messages": [
                        SystemMessage(
                            content="Exiting the loop : " + str(user_task_manage_response_parsed),
                            name="action",
                        ),
                    ]
                },
                goto="user_input_node")


def ppt_planner_node(
    state: PPTState,
) -> Command[Literal["user_input_node"]]:
    logger.info("PPT Planner working...")

    model = get_llm_by_type(AGENT_LLM_MAP["ppt_planner"])

    pptplaner_response = model.invoke(
        [
            SystemMessage(content=get_prompt_template("ppt_planner")),
            HumanMessage(content=state["requirement_cleaned"]),
        ],
    )
    parsed_response = parse_llm_json(pptplaner_response.content)
    key_messages = []
    if "key_messages" in parsed_response:
        for km_data in parsed_response["key_messages"]:
            key_message = create_key_message(
                message=km_data["message"],
                milestone_slide=km_data["milestone_slide_number"],
            )
            key_messages.append(key_message)

    # Process slides using helper functions from state.py
    slides = []
    if "slides" in parsed_response:
        for slide_data in parsed_response["slides"]:
            slide = create_slide(
                key_message_part=slide_data.get("key_message_part", ""),
                title=slide_data.get("title", ""),
                content=slide_data.get("content", ""),
                image=slide_data.get("image"),
                message_here=slide_data.get("message_here", ""),
                layout_description=slide_data.get(
                    "layout_description", "Standard content layout"
                ),
            )
            slides.append(slide)

    return Command(
        update={
            "file_name": parsed_response.get("file_name", state.get("file_name", "")),
            "ppt_title": parsed_response.get(
                "ppt_title", state.get("ppt_title", "")
            ),
            "number_of_slides": parsed_response.get(
                "number_of_slides", len(slides)
            ),
            "key_messages": key_messages,
            "slides": slides,
            "missing_information": parsed_response.get("missing_information", ""),
        },
        goto="user_input_node",
    )


def ppt_refiner_node(
    state: PPTState,
) -> Command[Literal["user_input_node"]]:
    logger.info("PPT refiner working...")

    model = get_llm_by_type(AGENT_LLM_MAP["ppt_refiner"])

    ppt_refiner_response = model.invoke(
        [
            SystemMessage(content=get_prompt_template("ppt_refiner")),
            HumanMessage(
                content=str({
                    "ppt_content": state["slides"],
                    "feedback": state["messages"][-1].content,
                }),
            ),
        ],
    )
    parsed_response = parse_llm_json(ppt_refiner_response.content)
    print("===============PARSED RESPONSE===============")
    print(parsed_response)
    print("===============PARSED RESPONSE===============")
    # key_messages = []
    # if "key_messages" in parsed_response:
    #     for km_data in parsed_response["key_messages"]:
    #         key_message = create_key_message(
    #             message=km_data["message"],
    #             milestone_slide=km_data["milestone_slide_number"],
    #         )
    #         key_messages.append(key_message)

    # Process slides using helper functions from state.py
    
    if "slides" in parsed_response:
        slides = []

        for slide_data in parsed_response["slides"]:
            print("===============SLIDE DATA===============")
            print(slide_data)
            print("===============SLIDE DATA===============")

            slide = create_slide(
                key_message_part=slide_data.get("key_message_part", ""),
                title=slide_data.get("title", ""),
                content=slide_data.get("content", ""),
                image=slide_data.get("image"),
                message_here=slide_data.get("message_here", ""),
                layout_description=slide_data.get(
                    "layout_description", "Standard content layout"
                ),
            )
            slides.append(slide)

    return Command(
        update={
            "slides": slides
        },
        goto="user_input_node",
    )

def pptx_coder_node(state: PPTState) -> Command[Literal["__end__"]]:
    logger.info("Gathering pptx code ...")
    model = get_llm_by_type(AGENT_LLM_MAP["pptx_coder"])
    print("STATE TYPE", type(state))
    print("STATE", state)
    coder_response = model.invoke(
        [
            SystemMessage(content=get_prompt_template("pptx_coder")),
            HumanMessage(content=str(state)),
        ],
    )
    print("CODER RESPONSE")
    parsed_response = coder_response.content
    code = extract_code_from_response(parsed_response)

    # Fixed imports with COM initialization for Windows
    pre_code = """
    import subprocess
    import sys
    import os

    # Windows COM initialization fix
    if os.name == 'nt':  # Windows
        try:
            import pythoncom
            pythoncom.CoInitialize()
            print("✅ COM initialized for Windows")
        except ImportError:
            print("⚠️ pythoncom not available, continuing without COM init")
        except Exception as e:
            print(f"⚠️ COM initialization warning: {e}")

    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        print("✅ All pptx imports successful")
    except ImportError:
        print("📦 Installing python-pptx...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        print("✅ python-pptx installed and imported")
    """

    print("EXECUTING PRE-CODE + GENERATED CODE")
    print("=" * 50)

    # Create a shared namespace for both exec calls
    exec_namespace = {}

    try:
        # Execute imports first
        clean_pre_code = textwrap.dedent(pre_code)
        exec(clean_pre_code, exec_namespace)

        # Execute generated code in the same namespace
        clean_code = textwrap.dedent(code)
        print(clean_code)
        exec(clean_code, exec_namespace)

        print("✅ PPT generation completed successfully!")

        # COM cleanup for Windows
        if os.name == 'nt':
            try:
                import pythoncom
                pythoncom.CoUninitialize()
                print("✅ COM cleaned up")
            except:
                pass

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        # COM cleanup even on error
        if os.name == 'nt':
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except:
                pass

    print("CODER RESPONSE END")
    print("=" * 50)

    return Command(
        goto="__end__"
    )

def slide_builder_node(state: PPTState) -> Command[Literal["__end__"]]:
    logger.info("Gathering pptx code ...")
    model = get_llm_by_type(AGENT_LLM_MAP["slide_builder"])
    print("STATE TYPE", type(state))
    print("STATE", state)
    slides = state["slides"].copy()
    for slide in slides:
        slide_response = model.invoke(
            [
                SystemMessage(content=get_prompt_template("slide_builder")),
                HumanMessage(content=str(slide)),
            ],
        )
        parsed_response = parse_llm_json(slide_response.content)
        slide["slide_content"] = parsed_response

    return Command(
        update={
            "slides": slides,
        },
        goto="user_input_node",
    )
