import openai
import config

openai.api_key =  config.OPENAI_API_KEY

media_file_path = 'Week 3\Dall-E and Whisper\SteveJobsSpeech_64kb.mp3'
media_file = open(media_file_path, 'rb')


transcription = openai.audio.transcriptions.create(
    model="whisper-1",
    file=media_file,
)
print(transcription.text)
    