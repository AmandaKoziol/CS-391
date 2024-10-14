from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# For GPT 3.5 Turbo, the endpoint is ChatCompletion
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    # Conversation as a list of messages.
    messages=[
        {"role": "system", "content": "You are a helpful teacher."},
        {
            "role": "user",
            "content": "Are there other measures than time complexity for an \
            algorithm?",
        },
        {
            "role": "assistant",
            "content": "Yes, there are other measures besides time complexity \
            for an algorithm, such as space complexity.",
        },
        {"role": "user", "content": "What is it?"},
    ]
)

print(response.choices[0].message.content)