from openai import OpenAI
import config

client = OpenAI(
  api_key=config.TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)

chat_completion = client.chat.completions.create(
  messages=[
    {
      "role": "system",
      "content": "You are an expert travel guide.",
    },
    {
      "role": "user",
      "content": "Tell me fun things to do in San Francisco.",
    }
  ],
  model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
)

print(chat_completion.choices[0].message.content)