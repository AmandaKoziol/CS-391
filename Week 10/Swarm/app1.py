import os
import config
from swarm import Swarm, Agent
import requests

os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY

# Define the Greeting Agent
greeting_agent = Agent(
    name="Greeting Agent",
    instructions="You are a friendly assistant that greets the user and tells a joke.",
)

# Define the News Function
def fetch_news(country="us", category=None):
    """
    Fetches the top news headlines for a given country and category.

    Args:
        country (str): The country code (default is "us").
        category (str): The news category (optional).

    Returns:
        str: A string containing the top news headlines or an error message.
    """
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": country,
        "apiKey": config.NEWS_API_KEY
    }

    # Add a category if provided
    if category:
        params["category"] = category

    # Make a GET request to the News API
    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200 and 'articles' in data:
        # Extract the titles of the first 10 articles
        headlines = [article['title'] for article in data['articles'][:10]]
        return f"Here are the top news for {country.upper()} ({category or 'all categories'}):\n" + "\n".join(headlines)
    else:
        # Return an error message if the request failed
        return f"Sorry, I couldn't fetch the news at the moment: {data.get('message', 'Unknown error')}"

# Define the News Agent
news_agent = Agent(
    name="News Agent",
    instructions="You provide the top news headlines for a given country and category.",
    functions=[fetch_news]
)

# Define function that transfers the task to the agent
def transfer_to_agent(agent_name):
  agents = {
      "Greeting Agent": greeting_agent,
      "News Agent": news_agent
  }
  return agents[agent_name]

# Define the Main AI Agent
main_agent = Agent(
    name = "Main Agent",
    instructions = """
    You are the main assistant.
    Based on the user's request, you decide which specialized agent should handle the task.
    - If the user wants a greeting or a joke, transfer to the Greeting Agent.
    - If the user wants to fetch the news, transfer to the News Agent.
    """,
    functions = [transfer_to_agent]
)

# Start the connection the OpenAI API
client = Swarm()

# Run the application
response = client.run(
    agent = main_agent,
    messages = [{"role": "user",
                 "content": "give me the first 10 news headlines from the US"}]  #try good morning
)
print(response.messages[-1]['content'])