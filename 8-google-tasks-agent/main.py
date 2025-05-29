import os
import time

# Important: Import your modified agent_todo
from tasks_store import google_agent_todo # This will now use Google Tasks

from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL", "gemini-1.5-flash-latest") # Ensure this matches or is compatible
AGENT_APP_NAME = 'google_tasks_agent_app'


def send_query_to_agent(agent, query):
    """
    Sends a query to the specified agent and prints the response.

    Args:
        agent: The agent to send the query to.
        query: The query to send to the agent.

    Returns:
        A tuple containing the elapsed time (in milliseconds) and the final response from the agent.
    """
    # Create a new session per query. For history, move session creation outside.
    session = session_service.create_session(app_name=AGENT_APP_NAME, user_id='user')

    print(f'\nUser Query: {query}')
    content = types.Content(role='user', parts=[types.Part(text=query)])

    start_time = time.time()
    runner = Runner(app_name=AGENT_APP_NAME, agent=agent, artifact_service=artifact_service, session_service=session_service)
    events = runner.run(user_id='user', session_id=session.id, new_message=content)

    final_response = None
    elapsed_time_ms = 0.0

    for _, event in enumerate(events):
        is_final_response = event.is_final_response()
        function_calls = event.get_function_calls()
        function_responses = event.get_function_responses()

        if not event.content and not function_calls and not function_responses: # Check all relevant event parts
            continue

        print("-----------------------------")
        if is_final_response:
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 3)
            print('>>> Inside final response <<<')
            if event.content and event.content.parts:
                 final_response = event.content.parts[0].text
                 print(f'Agent: {event.author}')
                 print(f'Response time: {elapsed_time_ms} ms\n')
                 print(f'Final Response:\n{final_response}')
            else:
                print("Final response event, but no content.")
        elif function_calls:
            print('+++ Inside function call +++')
            print(f'Agent: {event.author}')
            for function_call in function_calls:
                print(f'Call Function: {function_call.name}')
                print(f'Argument: {function_call.args}')
        elif function_responses:
            print('-- Inside function response --')
            print(f'Agent: {event.author}')
            for function_response in function_responses:
                print(f'Function Name: {function_response.name}')
                # Function response can be complex, print carefully
                if isinstance(function_response.response, dict) and 'parts' in function_response.response:
                     # Assuming response is structured like ADK expects for function results
                     response_text = function_response.response['parts'][0].get('text', str(function_response.response))
                     print(f'Function Results: {response_text}')
                else:
                     print(f'Function Results: {function_response.response}') # Fallback
        elif event.content and event.content.parts: # Interim model responses
            print("...Interim Agent Message...")
            print(f'Agent: {event.author}')
            print(event.content.parts[0].text)

        print("----------------------------------------------------------\n")

    return elapsed_time_ms, final_response