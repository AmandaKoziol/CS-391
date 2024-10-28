import base64
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

completion = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "wav"},
    messages=[
        { "role": "user", "content": "Is a golden retriever a good family dog?"},
        {
                "role": "assistant",
                "audio": {
                    "id": "audio_671ff0acdfcc81909e3caa0931b77b35"
                }
        },
        { "role": "user", "content": "Why do you say they are loyal?"}
    ]
)

# print(completion.choices[0])
print(completion.choices[0].message.audio.transcript)

wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
with open("loyal.wav", "wb") as f:
    f.write(wav_bytes)
