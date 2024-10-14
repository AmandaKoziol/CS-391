from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

prompt = '''You are a movie critic that follows the style of Siskel & Ebert. 
You are given a movie and are helping write a headline article about the movie.
In the article, you share your opinion and give a thumbs up or thumbs down rating.
Use the following two enumerated examples in the triple quotes when making your answer:
"""
1. "I Still Know What You Did Last Summer" is a deadening series of setups and slashings, setups and slashings, setups and slashings, and for its viewers, it's a waste of ninety precious minutes that they can *never* get back. Just think Gene, that's three hours between the two of us, if you multiply that by the thousands of the people who will see this movie, it adds up to months, years, even *centuries* lost forever to the human race.
2. Two tumbs up on "Terminator 2 Judment Day". They spent alot of money on this movie they are going to get it back.
"""
'''

# For GPT 3.5 Turbo, the endpoint is ChatCompletion
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": "Help me write the body of a headline article about the movie Harry Potter and the Sorcerer's Stone.",
        },
        {
            "role": "system", 
            "content": "'Harry Potter and the Sorcerer's Stone' is a magical adventure that enchants viewers of all ages. From the captivating world of Hogwarts to the lovable characters such as Harry, Ron, and Hermione, this film brings J.K. Rowling's beloved book to life in a spellbinding way. The visual effects are impressive, the score is enchanting, and the storytelling is truly captivating. Director Chris Columbus did a fantastic job of setting the stage for the rest of the Harry Potter series. With its mix of magic, friendship, and bravery, 'Harry Potter and the Sorcerer's Stone' is a must-watch for fans of the wizarding world. Thumbs up for this fantastical film!"
        },
        {
            "role": "user",
            "content": "Give me the title of the headline for the review you just gave me.",
        },
        {
            "role": "system", 
            "content": "Harry Potter and the Sorcerer's Stone Casts a Magical Spell on Audiences: A Must-See Adventure for Fans of All Ages!"
        },
        {
            "role": "user",
            "content": "Give me the headline article and title as a JSON object.",
        }
    ]
)

print(response.choices[0].message.content)