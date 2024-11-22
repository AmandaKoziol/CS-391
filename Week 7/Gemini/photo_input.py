import google.generativeai as genai
import config
import PIL.Image

genai.configure(api_key=config.API_KEY)

img = PIL.Image.open('image.jpg')
model = genai.GenerativeModel('gemini-1.5-flash')
#response = model.generate_content(img)

response = model.generate_content(["Write a short, engaging blog post based on this picture. \
                                   It should include a description of the meal in the photo and \
                                   talk about my journey meal prepping.", img], stream=True)
response.resolve()

print(response.text)


