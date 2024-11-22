import google.generativeai as genai
import config
import PIL.Image

genai.configure(api_key=config.GEMINI_API_KEY)

img = PIL.Image.open('Zebras.jpg')
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content(["Count how many zebras are in the given picture.", img], stream=True)
response.resolve()

print(response.text)