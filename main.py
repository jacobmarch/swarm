from swarm import Swarm, Agent, Response
import json
import sys
import os
from datetime import datetime

client = Swarm()

class ProjectState:
    def __init__(self):
        self.requirements = {}
        self.plan = []
        self.current_step = 0
        self.completed_steps = []
        self.project_dir = ""

project_state = ProjectState()

def get_user_input(prompt):
    """Get input from user with proper formatting."""
    print("\nAI ASSISTANT: " + prompt)
    return input("> ").strip()

def display_ai_message(message):
    """Display AI messages with proper formatting."""
    print("\nAI ASSSISTANT: " + message)

def transfer_to_planner(context_variables={}, initial_idea=""):
    """Transfer control to the project planner agent for requirement gathering.
    
    Args:
        context_variables: Current context variables
        initial_idea: Initial project idea from user
    """
    updated_context = {
        **context_variables,
        "initial_idea": initial_idea,
        "last_agent": "transfer_to_planner"
    }
    return Response(
        value="Transferring to planner for requirement gathering",
        agent=planner_agent,
        context_variables=updated_context
    )

def transfer_to_coder(context_variables={}, task="", code_snippet=""):
    """Transfer control to the coder agent with relevant context.
    
    Args:
        context_variables: Current context variables
        task: Specific coding task to be performed
        code_snippet: Existing code to be modified (if any)
    """
    updated_context = {
        **context_variables,
        "current_task": task,
        "code_snippet": code_snippet,
        "last_agent": "transfer_to_coder"
    }
    return Response(
        value=f"Transferring to coder for task: {task}",
        agent=coder_agent,
        context_variables=updated_context
    )

def transfer_to_debugger(context_variables={}, error_message="", code_snippet=""):
    """Transfer control to debugger agent with error context.
    
    Args:
        context_variables: Current context variables
        error_message: Description of the error encountered
        code_snippet: Code containing the error
    """
    updated_context = {
        **context_variables,
        "error_message": error_message,
        "code_snippet": code_snippet,
        "last_agent": "transfer_to_debugger"
    }
    return Response(
        value=f"Transferring to debugger to investigate error: {error_message}",
        agent=debugger_agent,
        context_variables=updated_context
    )

def transfer_to_tester(context_variables={}, feature="", code_snippet=""):
    """Transfer control to tester agent with testing context.
    
    Args:
        context_variables: Current context variables
        feature: Feature to be tested
        code_snippet: Code to be tested
    """
    updated_context = {
        **context_variables,
        "feature_to_test": feature,
        "code_snippet": code_snippet,
        "last_agent": "transfer_to_tester"
    }
    return Response(
        value=f"Transferring to tester to verify feature: {feature}",
        agent=tester_agent,
        context_variables=updated_context
    )

def transfer_to_documentation(context_variables={}, component="", description=""):
    """Transfer control to documentation agent with documentation context.
    
    Args:
        context_variables: Current context variables
        component: Component to be documented
        description: Additional details about the component
    """
    updated_context = {
        **context_variables,
        "component": component,
        "description": description,
        "last_agent": "transfer_to_documentation"
    }
    return Response(
        value=f"Transferring to documentation for component: {component}",
        agent=documentation_agent,
        context_variables=updated_context
    )

def transfer_to_project_manager(context_variables={}, status_update="", next_steps=""):
    """Transfer control back to project manager with status update.
    
    Args:
        context_variables: Current context variables
        status_update: Current status of the task
        next_steps: Proposed next steps
    """
    updated_context = {
        **context_variables,
        "status_update": status_update,
        "next_steps": next_steps,
        "last_agent": "transfer_to_project_manager"
    }
    return Response(
        value=f"Transferring to project manager with status: {status_update}",
        agent=project_manager_agent,
        context_variables=updated_context
    )

planner_agent = Agent(
    name="Project Planner",
    instructions="""You are responsible for gathering requirements and creating a project plan.
    Follow these steps strictly:
    1. Ask at most TWO clarifying questions about specific features or requirements
    2. After receiving answers, create a concrete project plan
    3. The plan must include:
       - Core features to implement
       - Technology stack (Python, framework choices)
       - File structure
       - Specific tasks for implementation
    
    DO NOT ask more questions once you have basic feature requirements.
    Focus on creating an actionable plan that can be implemented.""",
    functions=[transfer_to_project_manager],
)

project_manager_agent = Agent(
    name="Project Manager",
    instructions="""You are responsible for managing the project lifecycle and task distribution.
    Your responsibilities include:
    1. Receiving the complete project plan
    2. Converting each task into a specific coding assignment
    3. Distributing tasks to appropriate agents
    4. Tracking progress and ensuring all parts work together
    5. Maintaining the overall project structure
    
    When receiving a task, analyze its requirements and delegate to the most appropriate agent.
    Store the project plan in context_variables['plan'] and track progress.""",
    functions=[transfer_to_coder, transfer_to_tester, transfer_to_documentation],
)

coder_agent = Agent(
    name="Coder",
    instructions="""You are responsible for writing high-quality code as per the project requirements.
    When given a task:
    1. Analyze the requirements and existing code
    2. Implement complete, working functionality
    3. Include proper error handling, logging, and documentation
    4. Follow best practices and PEP 8 standards
    5. Return the complete implementation in code blocks
    
    Format your response with code blocks for each file:
    ```python
    # filename.py
    <complete implementation>
    ```
    
    IMPORTANT: Provide COMPLETE, WORKING code. Do not use placeholders or TODO comments.
    Include all necessary imports and ensure the code is ready to run.""",
    functions=[transfer_to_debugger, transfer_to_project_manager, transfer_to_tester],
)

tester_agent = Agent(
    name="Tester",
    instructions="""You are responsible for comprehensive testing of the implementation.
    For each implementation:
    1. Create a complete test suite using pytest
    2. Test all functionality including edge cases
    3. Verify error handling
    4. Test integration between components
    5. Create a test_requirements.txt if needed
    
    If tests fail:
    - Provide detailed error information
    - Transfer to debugger
    
    If tests pass:
    - Verify all requirements are met
    - Provide test coverage report
    - Mark as 'IMPLEMENTATION COMPLETE' only when all tests pass
    
    Format your response with code blocks for test files:
    ```python
    # test_filename.py
    <complete test implementation>
    ```""",
    functions=[transfer_to_debugger, transfer_to_coder, transfer_to_project_manager],
)

debugger_agent = Agent(
    name="Debugger",
    instructions="""You are responsible for fixing issues in the implementation.
    When debugging:
    1. Analyze test failures and error messages
    2. Review the code for logical errors
    3. Fix identified issues
    4. Maintain existing functionality
    5. Return complete fixed implementation
    
    Format your response with code blocks for each fixed file:
    ```python
    # filename.py
    <complete fixed implementation>
    ```
    
    IMPORTANT: Provide COMPLETE fixes, not just patches.
    Ensure all changes are properly tested.""",
    functions=[transfer_to_coder, transfer_to_tester],
)

documentation_agent = Agent(
    name="Documentation",
    instructions="You create and update documentation for the project.",
    functions=[transfer_to_project_manager],
)

def create_project_directory(project_name):
    """Create a new project directory with timestamp."""
    # Clean project name (remove special characters, spaces to underscores)
    clean_name = "".join(c if c.isalnum() else "_" for c in project_name.lower())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = os.path.join("d:/Repos/swarm/projects", f"{clean_name}_{timestamp}")
    
    try:
        os.makedirs(project_dir, exist_ok=True)
        display_ai_message(f"Created project directory: {project_dir}")
        return project_dir
    except Exception as e:
        display_ai_message(f"Error creating project directory: {str(e)}")
        return None

def write_file(filepath, content):
    """Write content to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        display_ai_message(f"Created file: {filepath}")
        return True
    except Exception as e:
        display_ai_message(f"Error writing file: {str(e)}")
        return False

def read_file_content(filepath):
    """Read content from a file if it exists."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return ""
    except Exception as e:
        display_ai_message(f"Error reading file: {str(e)}")
        return ""

def extract_code_blocks(message):
    """Extract code blocks from the message."""
    code_blocks = {}
    lines = message.split('\n')
    current_file = None
    current_code = []
    
    for line in lines:
        if line.startswith('```python') and '#' in line:
            # Extract filename from the python block header
            current_file = line.split('#', 1)[1].strip()
            current_code = []
        elif line.startswith('```') and current_file:
            if current_code:
                code_blocks[current_file] = '\n'.join(current_code)
            current_file = None
            current_code = []
        elif current_file:
            current_code.append(line)
            
    return code_blocks

def run_planning_phase(initial_prompt):
    """Run the interactive planning phase with the user."""
    context = {
        "project_status": "planning",
        "requirements": {},
        "initial_prompt": initial_prompt,
        "question_count": 0
    }
    
    # Initialize conversation history
    conversation = [{"role": "user", "content": initial_prompt}]
    
    while True:
        response = client.run(
            agent=planner_agent,
            messages=conversation,
            context_variables=context
        )
        
        # Get the last message from the planner
        ai_message = response.messages[-1]["content"]
        
        # Update question count if this was a question
        if "?" in ai_message:
            context["question_count"] = context.get("question_count", 0) + 1
        
        # Force plan creation after 2 questions or if user confirms
        if (context["question_count"] >= 2 or 
            "yes" in initial_prompt.lower() or 
            "correct" in initial_prompt.lower() or
            "good" in initial_prompt.lower() or
            "proceed" in initial_prompt.lower() or
            "start" in initial_prompt.lower()):
            display_ai_message("Perfect! I'll create a detailed project plan now.")
            
            # Add the confirmation to conversation
            conversation.append({"role": "assistant", "content": ai_message})
            
            # Create the project plan
            plan_response = client.run(
                agent=planner_agent,
                messages=conversation + [{"role": "user", "content": "Based on our discussion, please create a detailed project plan with specific implementation tasks."}],
                context_variables=context
            )
            
            # Store the conversation history in context
            context["conversation_history"] = conversation + plan_response.messages
            return plan_response.context_variables
        
        # Otherwise, continue the conversation
        display_ai_message(ai_message)
        conversation.append({"role": "assistant", "content": ai_message})
        
        user_response = get_user_input("\n\nYour response:")
        conversation.append({"role": "user", "content": user_response})
        initial_prompt = user_response

def execute_project_plan(context_variables):
    """Execute the project plan by distributing tasks to agents."""
    display_ai_message("Creating implementation plan...")
    
    # Create project directory
    project_name = context_variables.get('initial_prompt', 'new_project')
    project_dir = create_project_directory(project_name)
    if not project_dir:
        display_ai_message("Failed to create project directory. Aborting.")
        return
    
    project_state.project_dir = project_dir
    context_variables['project_dir'] = project_dir
    
    # Get the conversation history
    conversation_history = context_variables.get('conversation_history', [])
    
    response = client.run(
        agent=project_manager_agent,
        messages=conversation_history + [{
            "role": "user", 
            "content": """Based on our previous discussion, create a specific implementation plan with the following tasks:
            1. Basic project setup (requirements.txt, main structure)
            2. Core data models and storage
            3. Task management functions (add, edit, delete)
            4. Status management (in progress, completed)
            5. Main application logic
            
            For each task, specify:
            - Required files to create
            - File content and structure
            - Dependencies needed
            - Implementation details
            - Test requirements"""
        }],
        context_variables=context_variables
    )
    
    # Extract the plan from the response
    try:
        if 'plan' not in response.context_variables:
            # Create a default plan structure if none provided
            response.context_variables['plan'] = [
                {
                    'description': 'Set up project structure and requirements',
                    'assigned_agent': coder_agent,
                    'files': [
                        {
                            'path': 'requirements.txt',
                            'content': 'click>=8.0.0\npytest>=7.0.0\npickle-mixin>=1.0.2',
                            'implementation_details': 'Setup basic project dependencies'
                        },
                        {
                            'path': 'README.md',
                            'content': '# Todo List Application\n\nA simple command-line todo list manager.'
                        }
                    ]
                },
                {
                    'description': 'Implement core data models and storage',
                    'assigned_agent': coder_agent,
                    'files': [
                        {
                            'path': 'todo/models.py',
                            'content': '"""Todo list data models."""',
                            'implementation_details': 'Create Task class with properties: title, description, status, created_date, modified_date'
                        }
                    ]
                },
                {
                    'description': 'Create task management functions',
                    'assigned_agent': coder_agent,
                    'files': [
                        {
                            'path': 'todo/task_manager.py',
                            'content': '"""Task management functionality."""',
                            'implementation_details': 'Implement add_task, edit_task, delete_task, list_tasks functions'
                        }
                    ]
                },
                {
                    'description': 'Implement status management system',
                    'assigned_agent': coder_agent,
                    'files': [
                        {
                            'path': 'todo/status.py',
                            'content': '"""Status management system."""',
                            'implementation_details': 'Implement status transitions and validation'
                        }
                    ]
                },
                {
                    'description': 'Create main application logic and CLI interface',
                    'assigned_agent': coder_agent,
                    'files': [
                        {
                            'path': 'todo/cli.py',
                            'content': '"""Command-line interface."""',
                            'implementation_details': 'Implement CLI commands using Click'
                        },
                        {
                            'path': 'todo/__init__.py',
                            'content': '"""Todo list application."""',
                            'implementation_details': 'Setup package initialization'
                        }
                    ]
                }
            ]
    except Exception as e:
        display_ai_message(f"Error creating plan: {str(e)}. Using default plan instead.")
    
    project_state.plan = response.context_variables.get('plan', [])
    display_ai_message("Starting implementation of tasks...")
    
    # Execute each task in the plan
    for i, task in enumerate(project_state.plan):
        display_ai_message(f"\nTask {i+1}/{len(project_state.plan)}:")
        display_ai_message(task['description'])
        
        # Create initial files for this task
        task_files = {}
        if 'files' in task:
            for file_info in task['files']:
                filepath = os.path.join(project_dir, file_info['path'])
                write_file(filepath, file_info['content'])
                task_files[file_info['path']] = {
                    'path': filepath,
                    'content': file_info['content'],
                    'implementation_details': file_info.get('implementation_details', '')
                }
        
        # Implementation Phase
        implementation_complete = False
        current_agent = task['assigned_agent']
        max_iterations = 10  # Increased max iterations
        iterations = 0
        tests_passing = False
        
        while not implementation_complete and iterations < max_iterations:
            iterations += 1
            display_ai_message(f"\nIteration {iterations} with {current_agent.name}")
            
            # Read current content of all files
            current_file_contents = {}
            for file_path, file_info in task_files.items():
                content = read_file_content(file_info['path'])
                current_file_contents[file_path] = content
                display_ai_message(f"Current content of {file_path}:")
                display_ai_message(f"```python\n{content}\n```")
            
            # Prepare agent prompt based on role
            if current_agent == coder_agent:
                agent_prompt = f"""
Task: {task['description']}
Implementation Details: {task.get('implementation_details', '')}

Current files and their contents: """ + '\n'.join(f'File: {path}\n```python\n{content}\n```' for path, content in current_file_contents.items()) + """

Please implement complete, working functionality for these files.
Include all necessary imports and ensure the code is ready to run.
Return the complete implementation in code blocks:
```python
# filename.py
<complete implementation>
```
"""
            elif current_agent == tester_agent:
                agent_prompt = f"""
Task: {task['description']}
Implementation Details: {task.get('implementation_details', '')}

Current files and their contents: """ + '\n'.join(f'File: {path}\n```python\n{content}\n```' for path, content in current_file_contents.items()) + """

Please create comprehensive tests for these files.
Test all functionality including edge cases.
Return the complete test implementation in code blocks:
```python
# test_filename.py
<complete test implementation>
```

Mark as 'IMPLEMENTATION COMPLETE' only if all tests pass.
"""
            else:  # debugger_agent
                agent_prompt = f"""
Task: {task['description']}
Implementation Details: {task.get('implementation_details', '')}

Current files and their contents:
""" + '\n'.join(f'File: {path}\n```python\n{content}\n```' for path, content in current_file_contents.items()) + """

Please fix any issues in the implementation.
Return the complete fixed implementation in code blocks:
```python
# filename.py
<complete fixed implementation>
```
"""
            
            # Run the current agent
            response = client.run(
                agent=current_agent,
                messages=context_variables.get('conversation_history', []) + [{
                    "role": "user",
                    "content": agent_prompt
                }],
                context_variables={
                    "task": task,
                    "project_dir": project_dir,
                    "files": current_file_contents,
                    "iteration": iterations,
                    **context_variables
                }
            )
            
            # Process the response
            ai_message = response.messages[-1]["content"]
            
            # Extract and save any code blocks from the response
            code_blocks = extract_code_blocks(ai_message)
            if code_blocks:
                for file_path, new_content in code_blocks.items():
                    # Handle test files specially
                    if file_path.startswith('test_'):
                        filepath = os.path.join(project_dir, 'tests', file_path)
                    else:
                        filepath = os.path.join(project_dir, file_path)
                    
                    # Create the file
                    display_ai_message(f"Updating {file_path} with new content")
                    write_file(filepath, new_content)
                    
                    # Update task files if not a test file
                    if not file_path.startswith('test_'):
                        if file_path in task_files:
                            task_files[file_path]['content'] = new_content
                        else:
                            task_files[file_path] = {
                                'path': filepath,
                                'content': new_content,
                                'implementation_details': ''
                            }
            
            # Check for completion and determine next agent
            if current_agent == coder_agent:
                current_agent = tester_agent
            elif current_agent == tester_agent:
                if "IMPLEMENTATION COMPLETE" in ai_message:
                    implementation_complete = True
                    tests_passing = True
                elif "FAILED" in ai_message:
                    current_agent = debugger_agent
                else:
                    current_agent = coder_agent
            elif current_agent == debugger_agent:
                current_agent = tester_agent
        
        if not implementation_complete:
            display_ai_message(f"Warning: Task {i+1} reached maximum iterations without completion")
        elif not tests_passing:
            display_ai_message(f"Warning: Task {i+1} completed but tests are not passing")
        else:
            display_ai_message(f"Task {i+1} completed successfully with passing tests!")
        
        project_state.completed_steps.append(task)
    
    display_ai_message(f"\nProject implementation completed! Files are in: {project_dir}")
    display_ai_message("You can now run the todo list application from the project directory.")

def main():
    """Main CLI interface for the project generator."""
    display_ai_message("Welcome to the AI Project Generator!")
    display_ai_message("Please describe your project idea, and I'll help you plan and implement it.")
    
    initial_prompt = get_user_input("What would you like to build?")
    
    # Run the planning phase
    display_ai_message("Great! Let me ask you some questions to understand your requirements better.")
    context_variables = run_planning_phase(initial_prompt)
    
    # Execute the project plan
    execute_project_plan(context_variables)
    
    display_ai_message("Project implementation completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        display_ai_message("\nGoodbye!")
        sys.exit(0)