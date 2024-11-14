from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What are the differences between the two input images? Provide specific details"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://cdn.glitch.global/2eb408ff-8f25-4476-8ee1-bd969ab3033d/image1.png",
          },
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://cdn.glitch.global/2eb408ff-8f25-4476-8ee1-bd969ab3033d/image2.png",
          },
        },
      ],
    }
  ],
  max_tokens=300,
)
print(response.choices[0].message.content)