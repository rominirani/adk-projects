import os.path
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json' # Downloaded from Google Cloud Console

def get_tasks_service():
    """Shows basic usage of the Google Tasks API.
    Returns the Tasks API service object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # If refresh fails, force re-authentication
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('tasks', 'v1', credentials=creds)
        return service
    except HttpError as err:
        print(f"An API error occurred: {err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while building the service: {e}")
        return None

def list_task_lists(service):
    """Lists all task lists."""
    print("--- Task Lists ---")
    try:
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get('items', [])

        if not items:
            print('No task lists found.')
            return []
        
        task_lists_info = []
        for item in items:
            print(f"- {item['title']} (ID: {item['id']})")
            task_lists_info.append({'id': item['id'], 'title': item['title']})
        return task_lists_info
    except HttpError as err:
        print(f"An API error occurred while listing task lists: {err}")
        return []

def list_tasks(service, task_list_id='@default'):
    """Lists tasks from a specific task list."""
    print(f"\n--- Tasks in list (ID: {task_list_id}) ---")
    try:
        # By default, completed tasks are not shown. Set showCompleted=True to see them.
        # For more options, see: https://developers.google.com/tasks/reference/rest/v1/tasks/list
        results = service.tasks().list(tasklist=task_list_id, showCompleted=False, maxResults=20).execute()
        items = results.get('items', [])

        if not items:
            print('No tasks found in this list or all are completed (and showCompleted=False).')
            return []
        
        tasks_info = []
        for item in items:
            status = "Completed" if item.get('status') == 'completed' else "Needs Action"
            due_date = item.get('due', 'No due date')
            if due_date != 'No due date':
                due_date = datetime.datetime.fromisoformat(due_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')

            print(f"- {item['title']} (ID: {item['id']}, Status: {status}, Due: {due_date})")
            notes = item.get('notes')
            if notes:
                print(f"  Notes: {notes}")
            tasks_info.append({'id': item['id'], 'title': item['title'], 'status': item.get('status')})
        return tasks_info
    except HttpError as err:
        print(f"An API error occurred while listing tasks: {err}")
        return []

def create_task(service, task_list_id='@default', title="New Task from Python", notes=None, due_date_str=None):
    """Creates a new task."""
    print(f"\n--- Creating Task: '{title}' ---")
    task_body = {
        'title': title
    }
    if notes:
        task_body['notes'] = notes
    if due_date_str: # Expected format: YYYY-MM-DD
        # Google Tasks API expects RFC 3339 timestamp
        # e.g., "2023-10-27T00:00:00.000Z" for a full day
        try:
            dt_object = datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
            task_body['due'] = dt_object.isoformat() + "Z"
        except ValueError:
            print(f"Warning: Invalid due date format '{due_date_str}'. Should be YYYY-MM-DD. Task created without due date.")


    try:
        created_task = service.tasks().insert(tasklist=task_list_id, body=task_body).execute()
        print(f"Task created: {created_task['title']} (ID: {created_task['id']})")
        return created_task
    except HttpError as err:
        print(f"An API error occurred while creating a task: {err}")
        return None

def update_task(service, task_list_id='@default', task_id=None, new_title=None, new_status=None, new_notes=None, new_due_date_str=None):
    """Updates an existing task.
    new_status can be 'needsAction' or 'completed'.
    """
    if not task_id:
        print("Error: Task ID is required to update a task.")
        return None

    print(f"\n--- Updating Task (ID: {task_id}) ---")
    try:
        # First, get the existing task to avoid overwriting fields unintentionally
        task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()

        update_body = {}
        updated_fields = []

        if new_title is not None:
            update_body['title'] = new_title
            updated_fields.append(f"title to '{new_title}'")
        if new_status is not None and new_status in ['needsAction', 'completed']:
            update_body['status'] = new_status
            updated_fields.append(f"status to '{new_status}'")
        if new_notes is not None:
            update_body['notes'] = new_notes
            updated_fields.append(f"notes to '{new_notes}'")
        if new_due_date_str is not None: # Expected format: YYYY-MM-DD
            try:
                dt_object = datetime.datetime.strptime(new_due_date_str, "%Y-%m-%d")
                update_body['due'] = dt_object.isoformat() + "Z"
                updated_fields.append(f"due date to '{new_due_date_str}'")
            except ValueError:
                print(f"Warning: Invalid new due date format '{new_due_date_str}'. Due date not updated.")
        
        if not update_body:
            print("No valid fields provided for update.")
            return task # Return original task if nothing to update

        # Merge existing task data with new updates
        # This is important as the update method replaces the entire task resource
        # if you don't provide the full resource.
        # Alternatively, you can use patch() for partial updates.
        # For simplicity here, we build a full body for update().
        final_body = task.copy() # Start with the existing task
        final_body.update(update_body) # Apply changes

        updated_task = service.tasks().update(
            tasklist=task_list_id,
            task=task_id,
            body=final_body
        ).execute()
        
        print(f"Task updated. Changed: {', '.join(updated_fields) if updated_fields else 'No changes applied'}.")
        print(f"New state: {updated_task['title']} (Status: {updated_task.get('status')})")
        return updated_task
    except HttpError as err:
        print(f"An API error occurred while updating task: {err}")
        return None

def delete_task(service, task_list_id='@default', task_id=None):
    """Deletes a task."""
    if not task_id:
        print("Error: Task ID is required to delete a task.")
        return False
        
    print(f"\n--- Deleting Task (ID: {task_id}) ---")
    try:
        service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
        # Delete API returns an empty response on success
        print(f"Task (ID: {task_id}) deleted successfully from list (ID: {task_list_id}).")
        return True
    except HttpError as err:
        print(f"An API error occurred while deleting task: {err}")
        return False

def main():
    """Main function to demonstrate Google Tasks API interaction."""
    service = get_tasks_service()

    if not service:
        print("Failed to get Tasks service. Exiting.")
        return

    # 1. List all task lists
    task_lists = list_task_lists(service)
    
    # Use the first task list found, or default if none.
    # For most users, '@default' refers to their primary "My Tasks" list.
    target_task_list_id = '@default'
    if task_lists:
        # You might want to pick a specific list by its title or let the user choose
        # For this demo, we'll just use the first one if available, otherwise @default
        # target_task_list_id = task_lists[0]['id'] 
        print(f"\nUsing task list ID: {target_task_list_id} (often 'My Tasks') for further operations.")
    else:
        print(f"\nNo task lists found. Using '{target_task_list_id}' for operations.")


    # 2. List tasks in the target list
    current_tasks = list_tasks(service, task_list_id=target_task_list_id)

    # 3. Create a new task
    new_task_title = "Grocery Shopping"
    new_task_notes = "Buy milk, eggs, and bread."
    new_task_due = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    created_task = create_task(service,
                               task_list_id=target_task_list_id,
                               title=new_task_title,
                               notes=new_task_notes,
                               due_date_str=new_task_due)
    
    if created_task:
        created_task_id = created_task['id']
        print(f"Successfully created task with ID: {created_task_id}")

        # 4. Update the created task (e.g., mark as complete, change title)
        updated_task = update_task(service,
                                   task_list_id=target_task_list_id,
                                   task_id=created_task_id,
                                   new_title="Grocery Shopping - DONE!",
                                   new_status='completed',
                                   new_notes="All items purchased.")
        if updated_task:
            print(f"Updated task title to: {updated_task['title']}, status: {updated_task.get('status')}")

        # 5. Delete the task (optional - uncomment to test)
        # print("\nAttempting to delete the task we just created and updated...")
        # if delete_task(service, task_list_id=target_task_list_id, task_id=created_task_id):
        #     print(f"Task {created_task_id} was deleted.")
        # else:
        #     print(f"Failed to delete task {created_task_id}.")
    else:
        print(f"Failed to create task '{new_task_title}'. Skipping update and delete.")

    # List tasks again to see changes
    print("\n--- Listing tasks again after operations ---")
    list_tasks(service, task_list_id=target_task_list_id)

if __name__ == '__main__':
    main()