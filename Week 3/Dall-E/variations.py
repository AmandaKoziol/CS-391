from openai import OpenAI
import config
client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.images.create_variation(
  image=open("Week 3\Dall-E and Whisper\img-N2fyaKxmmMY4eOV6DWFRRAjs.png", "rb"),
  n=2,
  size="1024x1024"
)

image_url = response.data[0].url
print(image_url)