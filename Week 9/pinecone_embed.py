from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm  # For printing a progress bar
from time import sleep
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Function to get the vector embedding for a given text:
def get_vector_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002" 
    )
    embeddings = [r.embedding for r in response.data]
    return embeddings[0]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, # 100 tokens
    chunk_overlap=20, # 20 tokens of overlap
)

text = """
Welcome to the "Unicorn Enterprises: Where Magic Happens" Employee Handbook! We're thrilled to have you join our team of dreamers, doers, and unicorn enthusiasts. At Unicorn Enterprises, we believe that work should be as enchanting as it is productive. This handbook is your ticket to the magical world of our company, where we'll outline the principles, policies, and practices that guide us on this extraordinary journey. So, fasten your seatbelts and get ready to embark on an adventure like no other!
Certainly, here are five middle paragraphs for your fake employee handbook:

**1: Our Magical Culture**

At Unicorn Enterprises, we take pride in our unique and enchanting company culture. We believe that creativity and innovation flourish best when people are happy and inspired. From our weekly "Wear Your Favorite Mythical Creature Costume" day on Fridays to our in-house unicorn petting zoo, we aim to infuse magic into every corner of our workplace. So, don't be surprised if you find a fairy tale book in the breakroom or a gnome guiding you to the restroom. Our culture is designed to spark your imagination and encourage collaboration among our magical team.

**2: Unicorn Code of Conduct**

While we embrace creativity, we also value professionalism. Our Unicorn Code of Conduct ensures that we maintain a harmonious and respectful environment. Treating all team members, regardless of their unicorn species, with kindness and respect is essential. We also encourage open communication and constructive feedback because, in our world, every opinion matters, just like every horn on a unicorn's head!

**3: Magical Work-Life Balance**

At Unicorn Enterprises, we understand the importance of maintaining a balanced life. We offer flexible work hours, magical mental health days, and even an on-site wizard to provide stress-relief spells when needed. We believe that a happy and well-rested employee is a creative and productive employee. So, don't hesitate to use our relaxation chambers or join a group meditation session under the office rainbow.

**4: Enchanted Benefits**

Our commitment to your well-being extends to our magical benefits package. You'll enjoy a treasure chest of perks, including unlimited unicorn rides, a bottomless cauldron of coffee and potions, and access to our company library filled with spellbinding books. We also offer competitive health and dental plans, ensuring your physical well-being is as robust as your magical spirit.

**5: Continuous Learning and Growth**

At Unicorn Enterprises, we believe in continuous learning and growth. We provide access to a plethora of online courses, enchanted workshops, and wizard-led training sessions. Whether you're aspiring to master new spells or conquer new challenges, we're here to support your personal and professional development.

As we conclude this handbook, remember that at Unicorn Enterprises, the pursuit of excellence is a never-ending quest. Our company's success depends on your passion, creativity, and commitment to making the impossible possible. We encourage you to always embrace the magic within and outside of work, and to share your ideas and innovations to keep our enchanted journey going. Thank you for being a part of our mystical family, and together, we'll continue to create a world where magic and business thrive hand in hand!
"""

chunks = text_splitter.split_text(text=text)
print(chunks[0:3])

index_name = "employee-handbook-kozi8540"
environment = "us-east-1"
pc = Pinecone(api_key=config.PINECONE_API_KEY)  # This reads the PINECONE_API_KEY env var

# Check if index already exists
# (it shouldn't if this is first time)
if index_name not in pc.list_indexes().names():
    # if does not exist, create index
    pc.create_index(
        index_name,
        dimension=1536,  # Using the same vector dimensions as text-embedding-ada-002
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=environment),
    )

# Connect to index
index = pc.Index(index_name)

# View index stats
print(index.describe_index_stats())


# How many embeddings you create and insert at once
batch_size = 10
retry_limit = 5  # maximum number of retries

for i in tqdm(range(0, len(chunks), batch_size)):
    # Find end of batch
    i_end = min(len(chunks), i + batch_size)
    meta_batch = chunks[i:i_end]
    # Get ids
    ids_batch = [str(j) for j in range(i, i_end)]
    # Get texts to encode
    texts = [x for x in meta_batch]
    # Create embeddings
    # (try-except added to avoid RateLimitError)
    done = False
    try:
        # Retrieve embeddings for the whole batch at once
        embeds = []
        for text in texts:
            embedding = get_vector_embeddings(text)
            embeds.append(embedding)
        done = True
    except:
        retry_count = 0
        while not done and retry_count < retry_limit:
            try:
                for text in texts:
                    embedding = get_vector_embeddings(text)
                    embeds.append(embedding)
                done = True
            except:
                sleep(5)
                retry_count += 1

    if not done:
        print(
            f"""Failed to get embeddings after
        {retry_limit} retries."""
        )
        continue

    # Cleanup metadata
    meta_batch = [{"batch": i, "text": x} for x in meta_batch]
    to_upsert = list(zip(ids_batch, embeds, meta_batch))

    # Upsert to Pinecone
    index.upsert(vectors=to_upsert)


# Retrieve from Pinecone
user_query = "do we get free unicorn rides?"



def pinecone_vector_search(user_query, k):
    xq = get_vector_embeddings(user_query)
    res = index.query(vector=xq, top_k=k, include_metadata=True)
    return res


print(pinecone_vector_search(user_query, k=1))