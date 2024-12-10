from crewai import Agent
from langchain_openai import ChatOpenAI

class CustomAgents:
    def __init__(self):
        self.gpt_model = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    def create_agent(self, role):
        descriptions = {
            "Market Analyst": "I specialize in market research and analysis, providing insights that are crucial for strategic planning.",
            "Marketing Strategist": "I develop marketing strategies that effectively target key demographics and maximize market penetration."
        }

        return Agent(
            role=role,
            backstory=descriptions[role],
            goal=f"Develop detailed, actionable insights for {role}.",
            verbose=True,
            llm=self.gpt_model
        )