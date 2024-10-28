import openai
import config

openai.api_key =  config.OPENAI_API_KEY

speech_file = "french.mp3"

with openai.audio.speech.with_streaming_response.create(
	model="tts-1",
	voice="nova",
	input="Le rapide renard brun sauta par dessus le chien paresseux"
) as response:
    response.stream_to_file(speech_file)


	