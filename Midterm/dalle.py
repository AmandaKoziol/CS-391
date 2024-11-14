from openai import OpenAI
import config
client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.images.generate(
  model="dall-e-3",
  prompt="a white siamese cat",
  size="1024x1024",
  quality="standard",
  n=2,
)

image_url = response.data[0].url
print(image_url)