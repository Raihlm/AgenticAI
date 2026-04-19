"""State management for the LangGraph agent."""

from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State schema for the agent.

    The state flows through the graph and is updated at each step.
    """

    # Messages exchanged between user and agent
    messages: Annotated[List, add_messages]

    # Current user query being processed
    current_query: str

    # Results from tool invocations
    tool_results: list

    # Final response to the user
    response: str

    # Track which tools have been called
    tools_called: List[str]

    # Number of iterations (for loop prevention)
    iteration_count: int

    # Any errors encountered
    errors: List[str]

    # Plan for multi-step tasks (improvisation feature)
    plan: Optional[List[str]]

    # Current step in the plan
    current_step: int

    # Whether the task is complete
    is_complete: bool


def create_initial_state(query: str) -> AgentState:
    """Create a new state for processing a query."""
    return AgentState(
        messages=[("user", query)],
        current_query=query,
        tool_results=[],
        response="",
        tools_called=[],
        iteration_count=0,
        errors=[],
        plan=None,
        current_step=0,
        is_complete=False,
    )
