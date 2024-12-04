import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
import config

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, # 100 tokens
    chunk_overlap=20, # 20 tokens of overlap
    )

text = """
Welcome to the "Unicorn Enterprises: Where Magic Happens"
Employee Handbook! We're thrilled to have you join our team
of dreamers, doers, and unicorn enthusiasts. At Unicorn
Enterprises, we believe that work should be as enchanting as
it is productive. This handbook is your ticket to the
magical world of our company, where we'll outline the
principles, policies, and practices that guide us on this
extraordinary journey. So, fasten your seatbelts and get
ready to embark on an adventure like no other!

...

As we conclude this handbook, remember that at Unicorn
Enterprises, the pursuit of excellence is a never-ending
quest. Our company's success depends on your passion,
creativity, and commitment to making the impossible
possible. We encourage you to always embrace the magic
within and outside of work, and to share your ideas and
innovations to keep our enchanted journey going. Thank you
for being a part of our mystical family, and together, we'll
continue to create a world where magic and business thrive
hand in hand!
"""

chunks = text_splitter.split_text(text=text)


client = OpenAI(api_key=config.OPENAI_API_KEY)

# Function to get the vector embedding for a given text:
def get_vector_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embeddings = [r.embedding for r in response.data]
    return embeddings[0]

# Get vector embeddings for the chunks from last example
emb = [get_vector_embeddings(chunk) for chunk in chunks]
vectors = np.array(emb)

# Create a FAISS index
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

# Function to perform a vector search
def vector_search(query_text, k=1):
    query_vector = get_vector_embeddings(query_text)
    distances, indices = index.search(
        np.array([query_vector]), k)
    return [(chunks[i], float(dist)) for dist,
        i in zip(distances[0], indices[0])]

# Example search
user_query = "do we get free unicorn rides?"
search_results = vector_search(user_query)
print(f"Search results for {user_query}:", search_results)

# Function to perform a vector search and then ask # GPT-3.5-turbo a question
def search_and_chat(user_query, k=1):
  # Perform the vector search
  search_results = vector_search(user_query, k)
  print(f"Search results: {search_results}\n\n")

  prompt_with_context = f"""Context:{search_results}\
  Answer the question: {user_query}"""

  # Create a list of messages for the chat
  messages = [
      {"role": "system", "content": """Please answer the
      questions provided by the user. Use only the context
      provided to you to respond to the user, if you don't
      know the answer say \"I don't know\"."""},
      {"role": "user", "content": prompt_with_context},
  ]

  # Get the model's response
  response = client.chat.completions.create(
    model="gpt-4o-mini", messages=messages)

  # Print the assistant's reply
  print(f"""Response:
  {response.choices[0].message.content}""")

# Example search and chat
search_and_chat("What is Unicorn Enterprises' mission?")

# Save the index to a file
faiss.write_index(index, "my_index_file.index")
# Load the index from a file
index = faiss.read_index("my_index_file.index")