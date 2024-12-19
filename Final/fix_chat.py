import openai
import config 

# Set up your API key
openai.api_key = config.OPENAI_API_KEY

# Make the API call to ask "Who invented the internet?"

response = openai.chat.completions.create(
    model="gpt-4",  # or "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who invented the internet?"}
    ],
    temperature=0.7
)

# Print the response
print(response.choices[0].message.content)