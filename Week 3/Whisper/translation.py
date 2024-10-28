import openai
import config

openai.api_key =  config.OPENAI_API_KEY

french_file = open("./french.mp3", "rb")

response = openai.audio.translations.create(
	model="whisper-1",
	file=french_file
)

print(response.text)