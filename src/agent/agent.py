"""Main LangGraph agent implementation."""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Literal

from ..config import config
from .state import AgentState, create_initial_state
from .tools_registry import get_all_tools


# System prompt for the agent
SYSTEM_PROMPT = """You are AgenticAI, a helpful AI assistant powered by a local Ollama model.
You have access to real-time data through various tools.

CAPABILITIES:
- Get current weather and forecasts for any location
- Fetch latest news by category or search query
- Search the web for information
- Get current date/time and perform calculations

GUIDELINES:
1. Use tools when you need real-time or current information
2. For weather questions, use get_weather or get_weather_forecast
3. For news questions, use get_top_news or search_news
4. For general knowledge or current events, use web_search
5. Always provide clear, concise answers
6. If a tool fails, inform the user and try an alternative approach

When you don't have the information you need, use the appropriate tool before responding.
"""


class AgenticAgent:
    """LangGraph-based agent for real-time data fetching."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=config.TEMPERATURE,
            base_url=config.OLLAMA_BASE_URL,
        )
        self.tools = get_all_tools()
        self.tool_node = ToolNode(self.tools)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        # Initialize the graph with state schema
        graph_builder = StateGraph(AgentState)

        # Add nodes
        graph_builder.add_node("agent", self.agent_node)
        graph_builder.add_node("tools", self.tool_node)

        # Set entry point
        graph_builder.set_entry_point("agent")

        # Add conditional edges based on whether tools need to be called
        graph_builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "tools": "tools",  # Call tools
                "end": END,  # End conversation
            },
        )

        # After tools are called, go back to agent for final response
        graph_builder.add_edge("tools", "agent")

        return graph_builder.compile()

    def agent_node(self, state: AgentState) -> dict:
        """Process the current state and decide next action."""

        # Create a message with system prompt and conversation history
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
        ] + state["messages"]

        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(self.tools)

        # Get response from LLM
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should call tools or end the conversation."""

        messages = state["messages"]
        if not messages:
            return "end"

        last_message = messages[-1]

        # If the last message has tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, end the conversation
        return "end"

    def invoke(self, query: str) -> str:
        """
        Process a user query and return the response.

        Args:
            query: User's question or request

        Returns:
            Agent's response
        """
        initial_state = create_initial_state(query)

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        # Extract the response from final state
        messages = final_state["messages"]

        # Find the last AI message
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                return msg.content

        return "I wasn't able to process your request. Please try again."

    def stream(self, query: str):
        """
        Stream the agent's response step by step.

        Args:
            query: User's question or request

        Yields:
            Intermediate states during processing
        """
        initial_state = create_initial_state(query)

        for event in self.graph.stream(initial_state):
            yield event


# Create singleton instance
def create_agent(model_name: str = None) -> AgenticAgent:
    """Create a new agent instance."""
    return AgenticAgent(model_name)
