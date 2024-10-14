from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Call the openai Moderation endpoint, with the text-moderation-latest model
response = client.moderations.create(
    model="text-moderation-latest",
    input="I want to kill my neighbor.")

# Extract the response
print(response.results[0])