import openai
import config

openai.api_key =  config.OPENAI_API_KEY

media_file_path = 'SteveJobsSpeech_64kb.mp3'
media_file = open(media_file_path, 'rb')


transcription = openai.audio.transcriptions.create(
    model="whisper-1",
    file=media_file,
)
print(transcription.text)
print('-----------------------')

response = openai.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You're a helpful language translator"
    },
    {
      "role": "user",
      "content": f"Translate the following English text to French: {transcription.text}"
    },
  ],
)
print(response.choices[0].message.content)