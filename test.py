from swarm import Swarm, Agent, Response

client = Swarm()

# Define agent handoff functions with context passing
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

# Create all agents with their specific roles and handoff capabilities
project_manager_agent = Agent(
    name="Project Manager",
    instructions="""You are responsible for managing the project lifecycle, including task delegation and progress tracking. 
    You are also responsible for making project decisions such as the tech stack and project layout. 
    This includes creating necessary files and installing required dependencies.
    When a user presents requirements, break them down into tasks and delegate to appropriate agents.""",
    functions=[transfer_to_coder, transfer_to_tester, transfer_to_documentation],
)

coder_agent = Agent(
    name="Coder",
    instructions="You are responsible for writing high-quality code as per the project requirements.",
    functions=[transfer_to_debugger, transfer_to_project_manager, transfer_to_tester],
)

debugger_agent = Agent(
    name="Debugger",
    instructions="""You help debug and identify why errors are occurring in the codebase. 
    Generate feedback and provide it to the coder agent to ensure debugging goes as smoothly as possible.""",
    functions=[transfer_to_coder, transfer_to_project_manager],
)

tester_agent = Agent(
    name="Tester",
    instructions="You ensure that the code meets quality standards by writing and executing tests.",
    functions=[transfer_to_debugger, transfer_to_coder, transfer_to_project_manager],
)

documentation_agent = Agent(
    name="Documentation",
    instructions="You create and update documentation for the project.",
    functions=[transfer_to_project_manager],
)

# Start with the project manager agent to handle initial requirements
response = client.run(
    agent=project_manager_agent,
    messages=[{"role": "user", "content": "I need a simple web application that displays a todo list."}],
)

print(response.messages[-1]["content"])