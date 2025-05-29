from google.adk.agents import Agent

root_agent = Agent(
    name="travel_planner_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a helpful agent who assist users with their travel planning."
    ),
)
