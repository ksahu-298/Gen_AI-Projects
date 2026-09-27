from langchain.agents import create_agent
from hr_assistant import config

def create_hr_policy_agent(llm, tools):
    """Return a LangChain agent for answering HR policy questions."""
    return create_agent(model= llm, tools=tools, system_prompt=config.SYSTEM_PROMPT)