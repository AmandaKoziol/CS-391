import google.generativeai as genai
import config


genai.configure(api_key=config.API_KEY)
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("Write a story about a magic backpack.")
print(response.text)
