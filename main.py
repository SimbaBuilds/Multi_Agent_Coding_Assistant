from typing import TypedDict, List
import colorama
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, END
from langgraph.pregel import GraphRecursionError

from IPython.display import Image

# Define the paths.
base_path = os.path.join(os.getcwd(), "app")
src_path = os.path.join(base_path, "src")
test_path = os.path.join(base_path, "test")
code_file = os.path.join(src_path, "crud.py")
test_file = os.path.join(test_path, "test_crud.py")

# Create the folders and files if necessary.
os.makedirs(src_path, exist_ok=True)
os.makedirs(test_path, exist_ok=True)

# Create empty crud.py and test_crud.py if they do not exist
if not os.path.exists(code_file):
    with open(code_file, 'w') as f:
        f.write("# crud.py\n")

if not os.path.exists(test_file):
    with open(test_file, 'w') as f:
        f.write("# test_crud.py\n")

# llm = ChatOpenAI(base_url="https://api.together.xyz/v1",
#     api_key= "c27af21140685745a45bd67f89e1d6386343e46d3a025a5195826c55c21f9ba5",
#     model="deepseek-ai/deepseek-coder-33b-instruct")

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=1,  
    api_key="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",  # Optional if already set in env vars
)

class AgentState(TypedDict):
    class_source: str
    class_methods: List[str]
    tests_source: str

# Create the graph.
workflow = StateGraph(AgentState)

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

import_prompt_template = """Here is a path of a file with code: {code_file}.
Here is the path of a file with tests: {test_file}.
Write a proper import statement for the class in the file.
"""

# Discover the class and its methods.
def discover_function(state: AgentState):
    assert os.path.exists(code_file)
    with open(code_file, "r") as f:
        source = f.read()
    state["class_source"] = source

    # Get the methods.
    methods = []
    for line in source.split("\n"):
        if "def " in line:
            methods.append(line.split("def ")[1].split("(")[0])
    state["class_methods"] = methods

    # Generate the import statement and start the code.
    import_prompt = import_prompt_template.format(
        code_file=code_file,
        test_file=test_file
    )
    message = llm.invoke([HumanMessage(content=import_prompt)]).content
    code = extract_code_from_message(message)
    state["tests_source"] = code + "\n\n"

    return state

# Add a node for discovery.
workflow.add_node(
    "discover",
    discover_function
)

system_message_template = """You are a smart developer. You can do this! You will write unit 
tests that have a high quality. Use pytest.

Reply with the source code for the test only. 
Do not include the class in your response. I will add the imports myself.
If there is no test to write, reply with "# No test to write" and 
nothing more. Do not include the class in your response.

Example:

def test_function():


I will give you 200 EUR if you adhere to the instructions and write a high quality test. 
Do not write test classes, only methods.
"""

write_test_template = """Here is a class:
'''
{class_source}
'''

Implement a test for the method \"{class_method}\".
"""

# This method will write a test.
def write_tests_function(state: AgentState):
    # Get the next method to write a test for.
    class_method = state["class_methods"].pop(0)
    print(f"Writing test for {class_method}.")

    # Get the source code.
    class_source = state["class_source"]

    # Create the prompt.
    write_test_prompt = write_test_template.format(
        class_source=class_source,
        class_method=class_method
    )
    print(colorama.Fore.CYAN + write_test_prompt + colorama.Style.RESET_ALL)

    # Get the test source code.
    system_message = SystemMessage(system_message_template)
    human_message = HumanMessage(write_test_prompt)
    test_source = llm.invoke([system_message, human_message]).content
    test_source = extract_code_from_message(test_source)
    print(colorama.Fore.GREEN + test_source + colorama.Style.RESET_ALL)
    state["tests_source"] += test_source + "\n\n"

    return state

# Add the node.
workflow.add_node(
    "write_tests",
    write_tests_function
)

# Define the entry point. This is where the flow will start.
workflow.set_entry_point("discover")

# Always go from discover to write_tests.
workflow.add_edge("discover", "write_tests")

# Write the file.
def write_file(state: AgentState):
    with open(test_file, "w") as f:
        f.write(state["tests_source"])
    return state

# Add a node to write the file.
workflow.add_node(
    "write_file",
    write_file
)

# Find out if we are done.
def should_continue(state: AgentState):
    if len(state["class_methods"]) == 0:
        return "end"
    else:
        return "continue"

# Add the conditional edge.
workflow.add_conditional_edges(
    "write_tests",
    should_continue,
    {
        "continue": "write_tests",
        "end": "write_file"
    }
)

# Always go from write_file to end.
workflow.add_edge("write_file", END)

# Create the app and run it
app = workflow.compile()
initial_state = {
    "class_source": "",
    "class_methods": [],
    "tests_source": ""
}
config = RunnableConfig(recursion_limit=4)
try:
    result = app.invoke(initial_state, config)
    print(result)
except GraphRecursionError:
    print("Graph recursion limit reached.")





import pydot
from IPython.display import Image

def create_and_display_graph():
    # Create a new directed graph
    graph = pydot.Dot(graph_type='digraph')

    # Add nodes and edges
    node1 = pydot.Node("Start")
    node2 = pydot.Node("Discover")
    node3 = pydot.Node("Write Tests")
    node4 = pydot.Node("Write File")
    node5 = pydot.Node("End")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_node(node5)

    graph.add_edge(pydot.Edge(node1, node2))
    graph.add_edge(pydot.Edge(node2, node3))
    graph.add_edge(pydot.Edge(node3, node4))
    graph.add_edge(pydot.Edge(node4, node5))

    # Save the graph to a file
    graph.write_png('graph.png')

    # Display the graph
    return Image(filename='graph.png')

# Call the function to create and display the graph
# create_and_display_graph()

