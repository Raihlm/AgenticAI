"""Multi-step task planning and execution - Improvisation feature."""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Optional
from ..config import config


# System prompt for the planner
PLANNER_PROMPT = """You are a task planner for an AI agent.
Your job is to break down complex queries into actionable steps.

GUIDELINES:
1. Identify if the query requires multiple steps
2. Break down into clear, sequential steps
3. Each step should be achievable with available tools
4. Consider dependencies between steps

AVAILABLE TOOLS:
- get_weather: Get current weather
- get_weather_forecast: Get weather forecast
- get_top_news: Get news by category
- search_news: Search news by keyword
- web_search: Search the web
- get_current_time: Get date/time
- calculate: Math calculations

EXAMPLES:

Query: "Compare weather in Dhaka and London, then find news about both cities"
Plan:
1. Get weather in Dhaka
2. Get weather in London
3. Search news about Dhaka
4. Search news about London
5. Compare and summarize findings

Query: "What's the temperature difference between New York and Tokyo, and what are the top business headlines?"
Plan:
1. Get weather in New York
2. Get weather in Tokyo
3. Calculate temperature difference
4. Get top business news

Query: "Is it raining in Seattle?"
Plan:
1. Get weather in Seattle
(Check conditions for rain)
"""


class Step:
    """Represents a single step in a plan."""

    def __init__(self, step_number: int, description: str, tool_hint: Optional[str] = None):
        self.step_number = step_number
        self.description = description
        self.tool_hint = tool_hint
        self.result = None
        self.completed = False


class Plan:
    """Represents a multi-step plan."""

    def __init__(self, query: str, steps: List[Step]):
        self.query = query
        self.steps = steps
        self.current_step = 0
        self.completed = False

    def next_step(self) -> Optional[Step]:
        """Get the next uncompleted step."""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None

    def mark_complete(self, step: Step, result: str):
        """Mark a step as complete with its result."""
        step.completed = True
        step.result = result

    def is_complete(self) -> bool:
        """Check if all steps are complete."""
        return all(s.completed for s in self.steps)

    def get_summary(self) -> str:
        """Get a summary of the plan progress."""
        lines = [f"Plan for: {self.query}", "Steps:"]
        for step in self.steps:
            status = "✓" if step.completed else "○"
            lines.append(f"  {status} Step {step.step_number}: {step.description}")
        return "\n".join(lines)


class TaskPlanner:
    """Plans and executes multi-step tasks."""

    def __init__(self, agent=None):
        self.llm = ChatOllama(
            model=config.DEFAULT_MODEL,
            temperature=0.3,  # Lower temperature for more deterministic planning
            base_url=config.OLLAMA_BASE_URL,
        )
        self.agent = agent
        self.current_plan: Optional[Plan] = None

    def create_plan(self, query: str) -> Plan:
        """
        Create a plan for a complex query.

        Args:
            query: User's query

        Returns:
            Plan object with steps
        """
        messages = [
            SystemMessage(content=PLANNER_PROMPT),
            HumanMessage(
                content=f"Create a step-by-step plan for this query:\n\nQuery: {query}"
            ),
        ]

        response = self.llm.invoke(messages)
        plan_text = response.content

        # Parse the plan into steps
        steps = self._parse_plan(plan_text)

        self.current_plan = Plan(query, steps)
        return self.current_plan

    def _parse_plan(self, plan_text: str) -> List[Step]:
        """Parse plan text into Step objects."""
        steps = []
        lines = plan_text.strip().split("\n")

        step_number = 1
        for line in lines:
            line = line.strip()
            # Look for numbered steps
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove numbering
                content = line.lstrip("0123456789.-) ")
                if content.lower().startswith("step"):
                    content = content[4:].lstrip(" :")

                # Extract tool hint if present
                tool_hint = None
                if ":" in content:
                    parts = content.split(":", 1)
                    if any(tool in parts[0].lower() for tool in ["weather", "news", "search", "calculate"]):
                        tool_hint = parts[0].strip()

                steps.append(Step(step_number, content, tool_hint))
                step_number += 1

        # If no steps were parsed, create a single step
        if not steps:
            steps = [Step(1, plan_text.strip())]

        return steps

    def execute_plan(self, plan: Optional[Plan] = None) -> str:
        """
        Execute a plan step by step.

        Args:
            plan: Plan to execute (uses current_plan if None)

        Returns:
            Final result summary
        """
        plan = plan or self.current_plan
        if not plan:
            return "No plan to execute"

        if self.agent is None:
            return "No agent available to execute plan"

        results = []

        while not plan.is_complete():
            step = plan.next_step()
            if not step:
                break

            print(f"\n[Executing Step {step.step_number}: {step.description}]")

            # Execute the step using the agent
            try:
                result = self.agent.invoke(step.description)
                plan.mark_complete(step, result)
                results.append(f"Step {step.step_number}: {result}")
                print(f"[Completed: {step.description[:50]}...]")
            except Exception as e:
                error_msg = f"Error in step {step.step_number}: {str(e)}"
                plan.mark_complete(step, error_msg)
                results.append(error_msg)

        # Generate final summary
        return self._generate_summary(plan, results)

    def _generate_summary(self, plan: Plan, results: List[str]) -> str:
        """Generate a final summary of all results."""

        summary_prompt = f"""Based on the following query and results, provide a comprehensive summary:

Query: {plan.query}

Results:
{chr(10).join(results)}

Provide a clear, well-organized answer that addresses the original query using all the gathered information."""

        messages = [
            SystemMessage(content="You are a helpful assistant that summarizes information."),
            HumanMessage(content=summary_prompt),
        ]

        response = self.llm.invoke(messages)
        return response.content

    def should_plan(self, query: str) -> bool:
        """
        Determine if a query needs multi-step planning.

        Args:
            query: User's query

        Returns:
            True if planning is needed
        """
        # Simple heuristics for now
        # Could be enhanced with LLM classification

        planning_keywords = [
            "compare",
            "and then",
            "first",
            "then",
            "both",
            "difference between",
            "versus",
            "vs",
            "list all",
            "analyze",
        ]

        query_lower = query.lower()

        # Check for multiple tool requirements
        tool_indicators = {
            "weather": any(w in query_lower for w in ["weather", "temperature", "forecast", "rain"]),
            "news": any(w in query_lower for w in ["news", "headline", "article"]),
            "search": any(w in query_lower for w in ["search", "find", "look up"]),
        }

        # If multiple tool types are needed, planning is beneficial
        if sum(tool_indicators.values()) > 1:
            return True

        # If planning keywords are present
        if any(kw in query_lower for kw in planning_keywords):
            return True

        return False


# Create singleton
def create_planner(agent=None) -> TaskPlanner:
    """Create a new planner instance."""
    return TaskPlanner(agent)
