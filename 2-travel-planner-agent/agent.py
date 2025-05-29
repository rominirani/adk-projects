import os
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

from google.adk.agents import Agent
from dotenv import load_dotenv

root_agent = Agent(
    name="travel_planner_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a helpful agent who assist users with their travel planning."
    ),
)

#Agent Deployment to Agent Engine related code starts
load_dotenv()
GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_REGION"]
STAGING_BUCKET = "gs://" + os.environ["STORAGE_BUCKET_NAME"]

reasoning_engines.

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

remote_app = agent_engines.create(
    app,
    requirements=[
        "google-cloud-aiplatform[agent_engines,adk]>=1.88",
        "google-adk",
        "google-cloud-aiplatform",
        "cloudpickle==3.1.1",
        "pydantic==2.10.6",
        "pytest",
        "overrides",
        "google-auth",
        "google-cloud-storage",
    ],
)

print(remote_app.resource_name)

# Deployment to Agent Engine related code ends
