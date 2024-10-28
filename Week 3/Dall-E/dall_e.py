from openai import OpenAI
import config
client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.images.generate(
  model="dall-e-3",
  prompt="a white dog",#siamese cat",
  size="1024x1024",
  quality="hd",
  n=1,
)

image_url = response.data[0].url

print(image_url)