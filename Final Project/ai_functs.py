from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from pydantic import BaseModel, Field, model_validator
from typing import List
import config

from flask import jsonify
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai.chat_models import ChatOpenAI
from openai import OpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Define your desired data structure.
class Book(BaseModel):
    title: str = Field(description="title of the book")
    author: str = Field(description="author of the book")

class Books(BaseModel):
    books: List[Book] = Field(description='''A list of books with book title and author''')

def get_recommendations(read_books:list):
    # Set up a parser + inject instructions into the prompt template:
    parser = PydanticOutputParser(pydantic_object=Books)

    # Chat Model Output Parser:
    model = ChatOpenAI(api_key=config.OPENAI_API_KEY)
    template = "You are a helpful assistant that has a lot of knowledge about books. \
                    When you are given a list of books the reader has read, provide 10 book suggestions that the reader may like based on their read books. \
                    Return the result as a list of the book titles and authors. \n\
                    {format_instructions}\n\
                    Give me 10 book suggestions if the user has read the following books: {history}"

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    chain = chat_prompt | model | parser

    read_books_str = ''
    for book in read_books:
        read_books_str += book.title + ' by ' + book.author + ', '

    result = chain.invoke(
        {
            "history": read_books_str,
            "format_instructions": parser.get_format_instructions(),
        }
    )
    print(f"result: {result}")
    return result

def get_image(page_text:str):
    # Use OpenAI to write an image description for Dall-E
    prompt = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an image prompt generator that picks the most important details from a page from a book and turns it into an image prompt for Dall-E. \
             Make it concise and format it so Dall-E can understand what image you want it to generate \
             The new page may start halfway through a sentence, so try your best to interpret the remaining information to use in your answer \
             In your output, specify for Dall-E to not include text in the image"},
            {
                "role": "user",
                "content": "Input book page: " + page_text,
            },
        ]
    )
    print(prompt.choices[0].message.content)

    # Generate the DALL-E image based on the page text
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt.choices[0].message.content,
        n=1,
        size="1024x1024",
        quality="standard",
    )
    image_url = response.data[0].url  # Return the URL of the generated image    
    print(image_url)
    return jsonify({'image_url': image_url})
