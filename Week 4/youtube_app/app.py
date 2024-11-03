from flask import Flask, request, render_template_string
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

import config
import json

app = Flask(__name__)

# HTML template for a single-page app
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Summarizer</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { width: 50%; margin: 50px auto; text-align: center; }
        input[type="text"] { width: 80%; padding: 10px; margin-bottom: 20px; }
        input[type="submit"] { padding: 10px 20px; }
        .summary { margin-top: 20px; font-size: 1.2em; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Video Summarizer</h1>
        <form method="post">
            <input type="text" name="link" placeholder="Enter YouTube video link" required>
            <input type="submit" value="Summarize">
        </form>
        {% if summary %}
            <div class="summary">
                <h2>Summary:</h2>
                <p>{{ summary }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_video_id(url):
    # Extract YouTube video ID from URL
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": summary = 'Please enter a valid YouTube link'
    else:
        # Get input link
        link = request.form.get("link")
        if not link: return 'Enter a YouTube link'

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        # Download the transcript from the YouTube video
        video_id = extract_video_id(link)
        print(video_id)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en']).fetch()

        # Extract and concatenate all text elements
        concatenated_text = " ".join(item['text'] for item in transcript)

        #  Call the openai ChatCompletion endpoint, with the ChatGPT model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Summarize the following text."},
                {"role": "assistant", "content": "Yes."},
                {"role": "user", "content": concatenated_text}])

        summary = response.choices[0].message.content
    return render_template_string(HTML_TEMPLATE, summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
