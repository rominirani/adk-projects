import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

load_dotenv()

ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        ask_vertex_retrieval,
    ]
)