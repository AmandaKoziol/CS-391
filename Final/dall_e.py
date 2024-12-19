from openai import OpenAI
import config, base64
client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.images.generate(
  model="dall-e-3",
  prompt="a white siamese cat",
  size="1792x1024",
  quality="hd",
  n=1,
  response_format="b64_json"
)

img_data = response.data[0].b64_json.encode()

with open("imageToSave.png", "wb") as fh:
   fh.write(base64.decodebytes(img_data))