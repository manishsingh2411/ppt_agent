from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv
import logging
from phase1.state import PPTState
from phase1.nodes import user_task_manager_node, user_input_node, ppt_planner_node, ppt_initiator_node, ppt_refiner_node, pptx_coder_node, slide_builder_node
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()


logger = logging.getLogger(__name__)
load_dotenv()

def build_graph():
    """Build and return the ppt workflow graph."""
    # build state graph
    print("Building graph Agsin")
    print(PPTState)
    builder = StateGraph(PPTState)
    builder.add_edge(START, "user_input_node")
    builder.add_node("user_input_node", user_input_node)
    builder.add_node("user_task_manager_node", user_task_manager_node)
    builder.add_node("ppt_planner_node", ppt_planner_node)
    builder.add_node("ppt_initiator_node",  ppt_initiator_node)
    builder.add_node("ppt_refiner_node",  ppt_refiner_node)
    builder.add_node("pptx_coder_node", pptx_coder_node)
    builder.add_node("slide_builder_node", slide_builder_node)
    builder.add_edge("user_task_manager_node", END)
    return builder.compile(checkpointer=checkpointer)


# def build_graph():
#     """Build and return the ppt workflow graph."""
#     builder = StateGraph(PPTState)
#     builder.add_edge(START, "requirement_gathrer_node")
#     builder.add_node("", requirement_gathrer_node)
#     builder.add_node("ppt_planner_node", ppt_planner_node)
#     builder.add_node("pptx_coder_node", pptx_coder_node)
#     builder.add_edge("ppt_planner_node", END)
#     return builder.compile()

if __name__ == "__main__":
    print("Building graph")
    workflow = build_graph()
    report_content = "Why water is scares in rajesthan"
    final_state = workflow.invoke({"user_requirement": report_content})
    # print(final_state)