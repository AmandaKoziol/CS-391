from openai import OpenAI
import config
client = OpenAI(api_key=config.OPENAI_API_KEY)

client.fine_tuning.jobs.create(
    model = "gpt-4o-mini-2024-07-18"
    #needs training_file=file_id so it knows to train on the uploaded file
)

completion = client.chat.completions.create(
  messages=[
    {'role': 'system', 'content': "You're a helpful assistant"},
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  model="ft:gpt-3.5-turbo-0125:kettering-university-computer-science::ASA7UpRv",
)

print(completion)