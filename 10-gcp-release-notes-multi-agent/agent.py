from google.adk.agents import Agent, SequentialAgent, LlmAgent
from toolbox_core import ToolboxSyncClient

# Load the toolbox client and the toolset for Google Cloud Platform release notes
toolbox = ToolboxSyncClient("http://127.0.0.1:7000")
tools = toolbox.load_toolset('my_bq_toolset')

# Note: The two agents are designed to work together, with the first agent retrieving the release notes and the second agent translating them.
# The first agent can be used to fetch the release notes, and the second agent can be used to translate them into the desired language.
# The agents can be used independently as well, depending on the user's needs.

release_notes_retrieval_agent = LlmAgent(
    name="google_release_notes_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to help retrieve Google Cloud Platform release notes for the specific date."
    ),
    instruction=(
        """
        You are a helpful agent who can assist users in retrieving Google Cloud Platform release notes for the specific date. Use the tools provided to fetch the relevant information and include all the records. Do not skip any of the results returned by the tool. Group the results by the product_name.
        Summarize the release notes for each product in a concise manner, ensuring that the summary is clear and informative. If there are no release notes for a product, indicate that there are no updates available.
        Use the tools to answer the question. If you are unable to find any release notes, inform the user that there are no updates available for that product.
        """
    ),
    tools=tools,
    output_key="release_notes",
)

release_notes_translation_agent_cantonese = LlmAgent(
    name="google_release_notes_translation_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to help translate Google Cloud Platform release notes for the specific date into Cantonese."
    ),
    instruction=(
        """
        You are a helpful agent who can assist users in translating Google Cloud Platform release notes for the specific date into Cantonese language.
        Use the {release_notes} key from the previous agent to get the release notes.
        Ensure that the translations are accurate and maintain the original meaning of the release notes.
        Do not translate the product_name, only the release notes.
        """
    ),
    output_key="translated_release_notes_cantonese",
)

root_agent = SequentialAgent(
    name="google_release_notes_root_agent",
    sub_agents=[release_notes_retrieval_agent, release_notes_translation_agent_cantonese],
    description=(
        "Root agent to manage the retrieval and translation of Google Cloud Platform release notes."
    ),
)