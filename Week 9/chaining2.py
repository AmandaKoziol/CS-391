from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import config

# Initialize the language model
llm = OpenAI(temperature=0.7, api_key=config.OPENAI_API_KEY)

# Template for generating a story outline
outline_template = PromptTemplate.from_template("""
Create a short story outline with the following parameters:
- Genre: {genre}
- Main character: {main_character}
- Setting: {setting}

Provide a brief outline with 3-5 main plot points.

Outline:
""")

# Template for expanding the outline into a full story
story_template = PromptTemplate.from_template("""
Based on the following outline, write a short story:

{outline}

Expand this outline into a coherent short story with dialogue and descriptive language. 
The story should be between 500-1000 words.

Story:
""")

# Create the outline chain
outline_chain = outline_template | llm | StrOutputParser()

# Create the story chain
story_chain = (
    RunnablePassthrough.assign(outline=outline_chain) 
    | story_template 
    | llm 
    | StrOutputParser()
)

overall_chain = RunnablePassthrough.assign(
    outline=outline_chain,
    story=story_chain
)

# Run the chain
result = overall_chain.invoke({
    "genre": "science fiction",
    "main_character": "a time-traveling archaeologist",
    "setting": "ancient Egypt and futuristic Mars colony"
})

print("Outline:")
print(result["outline"])
print("\nFull Story:")
print(result["story"])