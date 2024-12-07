from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage

# Define our agent types
agent_types = ["Ingester", "Ranker", "Summarizer", "Formatter", "Emailer"]

# Create a function to route messages between agents
def route_message(message: Union[HumanMessage, AIMessage]) -> Union[str, Literal["END"]]:
    if "task_complete" in message.content.lower():
        return END
    for agent_type in agent_types:
        if agent_type.lower() in message.content.lower():
            return agent_type
    return "Human"  # Default to human if no agent is specified

# Create our graph
workflow = Graph()

# Add nodes for each agent type
for agent_type in agent_types:
    workflow.add_node(agent_type, agent_factory(agent_type))

# Add human node for potential intervention
workflow.add_node("Human", human_intervention)

# Add edges
workflow.add_edge(route_message)

# Set the entry point
workflow.set_entry_point("Ingester")

# Compile the graph
app = workflow.compile()