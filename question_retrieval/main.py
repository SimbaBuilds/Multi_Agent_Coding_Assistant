from typing import TypedDict, List
import os
import colorama

from interpreter import interpreter

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.pydantic_v1 import BaseModel


from langgraph.graph import StateGraph, END
from langgraph.pregel import GraphRecursionError

# Define the paths
base_path = os.path.join(os.getcwd(), "app")
src_path = os.path.join(base_path, "src")
test_path = os.path.join(base_path, "test")
code_file = os.path.join(src_path, "crud.py")
test_file = os.path.join(test_path, "test_crud.py")

# Create the folders and files if necessary
os.makedirs(src_path, exist_ok=True)
os.makedirs(test_path, exist_ok=True)

# Create empty crud.py and test_crud.py if they do not exist
if not os.path.exists(code_file):
    with open(code_file, 'w') as f:
        f.write("# crud.py\n")

if not os.path.exists(test_file):
    with open(test_file, 'w') as f:
        f.write("# test_crud.py\n")

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=1,  
    api_key="your_openai_api_key",  # Replace with your actual API key
)


GENERATOR_PROMPT = """
You are an expert software engineer.  Use this script {template_script} to write a program that {task}.  
You also may need access to these files: {relevant_files} """

RUN_TIME_CHECKER_PROMPT = """

"""

PRODUCTION_CHECKER_PROMPT = """
You are a 
"""

class AgentState(TypedDict):
    code_files: List[str]
    has_runtime_error: bool
    runtime_error_fix: str
    has_production_error: bool
    production_error_fix: str

# Create the graph
builder = StateGraph(AgentState)


def extract_code_from_message(message):
    lines = message.split("\n")
    code = ""
    in_code = False
    for line in lines:
        if "```" in line:
            in_code = not in_code
        elif in_code:
            code += line + "\n"
    return code

# Node1: Write/Edit Code
def write_edit_code(state: AgentState):
    scripts = state["code_files"] 
    rt = state["has_runtime_error"]
    rt_fix = state["runtime_error_fix"]
    pe = state["has_production_error"]
    pe_fix = state["production_error_fix"]


    #Implement write/edit code logic here

    return state


# Node2: Test for Runtime Errors
def test_runtime_errors(state: AgentState):
    
    scripts = state["code_files"] 
    rt = state["has_runtime_error"]
    rt_fix = state["runtime_error_fix"]
    pe = state["has_production_error"]
    pe_fix = state["production_error_fix"]
    
    #Implement logic for testing if LLM generated code produces a runtime error
    

    #Simulate runtime error testing
    state["has_runtime_errors"] = True  # Example: Found runtime errors
    
    
    if state["has_runtime_errors"]:
        # Analyze the error
        error_analysis = "Example error: deprecated function used"
        
        if "easy fix" in error_analysis:
            state["error_fix"] = "Replace deprecated function with new_function()"
        elif "deprecated" in error_analysis:
            # Search the web for a fix (simulated here)
            state["error_fix"] = "Found solution online: use alternative_function() instead of deprecated_function()"
        return state

    state["error_fix"] = ""
    return state


# Node3: Test Effectiveness
def test_in_production(state: AgentState):
    scripts = state["code_files"] 
    rt = state["has_runtime_error"]
    rt_fix = state["runtime_error_fix"]
    pe = state["has_production_error"]
    pe_fix = state["production_error_fix"]
   
   
   
    # Simulate querying the bot to test effectiveness
    query = "Check if script works as intended"
    response = llm.invoke([HumanMessage(query)]).content
    
    # Simulated check
    if "right questions" in response:
        state["tests_effective"] = True
    else:
        state["tests_effective"] = False
    return state


# Define the conditions
def should_fix_runtime_errors(state: AgentState):
    scripts = state["code_files"] 
    rt = state["has_runtime_error"]
    rt_fix = state["runtime_error_fix"]
    pe = state["has_production_error"]
    pe_fix = state["production_error_fix"]
    
    if state["has_runtime_error"]:
        return "YES"
    return "NO"

def should_improve_tests(state: AgentState):
    scripts = state["code_files"] 
    rt = state["has_runtime_error"]
    rt_fix = state["runtime_error_fix"]
    pe = state["has_production_error"]
    pe_fix = state["production_error_fix"]
    
    if state["had_production_error"]:
        return "YES"
    return "END"

#Add the nodes to the graph
builder.add_node("write_edit_code", write_edit_code)
builder.add_node("test_runtime_errors", test_runtime_errors)
builder.add_node("test_in_production", test_in_production)

#Add the edges
builder.add_edge("write_edit_code", "test_runtime_errors")
builder.add_edge("test_runtime_errors", "test_in_production")
builder.add_conditional_edges(
    "test_runtime_errors",
    should_fix_runtime_errors,
    {
        "YES": "write_edit_code",
        "NO": "test_in_production"
    }
)
builder.add_conditional_edges(
    "test_in_production",
    should_improve_tests,
    {
        "YES": "write_edit_code",
        "END": END
    }
)

# Set entry point
builder.set_entry_point("write_edit_code")

# Create the graph and run it
graph = builder.compile()

initial_state = {
    "code_files" : "",
    "has_runtime_error" : False,
    "runtime_error_fix" : "",
    "has_production_error" : False,
    "production_error_fix" : ""
}
config = RunnableConfig(recursion_limit=4)
try:
    result = graph.invoke(initial_state, config)
    print(result)
except GraphRecursionError:
    print("Graph recursion limit reached.")


# source myenv/bin/activate
