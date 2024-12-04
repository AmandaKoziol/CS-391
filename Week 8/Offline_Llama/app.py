import requests
import json

url = "http://localhost:11434/api/generate"

headers = { 
    "Content-Type": "application/json"
}

# Read input text file
input = open('input.txt', 'r').read()

data = {
    "model": "llama2",
    "prompt": f"Generate a summary for the given text. The output should be in French and should be simple enough for a 5th grader to understand. Input text: {input}",
    "stream": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    response_text = response.text 
    data = json.loads(response_text)
    actual_response = data["response"]
    print(actual_response)
else:
    print("Error:", response.status_code, response.text)
