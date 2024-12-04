from langchain_core.prompts.chat import ChatPromptTemplate
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import config
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import pandas as pd


character_generation_prompt = ChatPromptTemplate.from_template(
    """I want you to brainstorm three to five characters for my short story. The
    genre is {genre}. Each character must have a Name and a Biography.
    You must provide a name and biography for each character, this is very
    important!
    ---
    Example response:
    Name: CharWiz, Biography: A wizard who is a master of magic.
    Name: CharWar, Biography: A warrior who is a master of the sword.
    ---
    Characters: """
)

plot_generation_prompt = ChatPromptTemplate.from_template(
    """Given the following characters and the genre, create an effective
    plot for a short story:
    Characters:
    {characters}
    ---
    Genre: {genre}
    ---
    Plot: """
    )

scene_generation_plot_prompt = ChatPromptTemplate.from_template(
    """Act as an effective content creator.
    Given multiple characters and a plot, you are responsible for
    generating the various scenes for each act.

    You must decompose the plot into multiple effective scenes:
    ---
    Characters:
    {characters}
    ---
    Genre: {genre}
    ---
    Plot: {plot}
    ---
    Example response:
    Scenes:
    Scene 1: Some text here.
    Scene 2: Some text here.
    Scene 3: Some text here.
    ----
    Scenes:
    """
)

chain = RunnablePassthrough() | {
    "genre": itemgetter("genre"),
  }
print(chain.invoke({"genre": "fantasy"}))
{'genre': 'fantasy'}

# Create the chat model:
model = ChatOpenAI(api_key=config.OPENAI_API_KEY)

# Create the sub-chains:
character_generation_chain = character_generation_prompt | model |  StrOutputParser()
plot_generation_chain = plot_generation_prompt | model | StrOutputParser()                                                               
scene_generation_plot_chain = scene_generation_plot_prompt | model | StrOutputParser()

master_chain = (
    {"characters": character_generation_chain, "genre": RunnablePassthrough()}
    | RunnableParallel(
        characters=itemgetter("characters"),
        genre=itemgetter("genre"),
        plot=plot_generation_chain,
    )
    | RunnableParallel(
        characters=itemgetter("characters"),
        genre=itemgetter("genre"),
        plot=itemgetter("plot"),
        scenes=scene_generation_plot_chain,
    )
)

story_result = master_chain.invoke({"genre": "Fantasy"})
# print(story_result)

# Extracting the scenes using .split('\n') and removing empty strings:
scenes = [scene for scene in story_result["scenes"].split("\n") if scene]
generated_scenes = []
previous_scene_summary = ""

character_script_prompt = ChatPromptTemplate.from_template(
    template="""Given the following characters: {characters} and the genre: {genre}, create an effective character script for a scene.

    You must follow the following principles:
    - Use the Previous Scene Summary: {previous_scene_summary} to avoid repeating yourself.
    - Use the Plot: {plot} to create an effective scene character script.
    - Currently you are generating the character dialogue script for the following scene: {scene}

    ---
    Here is an example response:
    SCENE 1: ANNA'S APARTMENT

    (ANNA is sorting through old books when there is a knock at the door. She opens it to reveal JOHN.)
    ANNA: Can I help you, sir?
    JOHN: Perhaps, I think it's me who can help you. I heard you're researching time travel.
    (Anna looks intrigued but also cautious.)
    ANNA: That's right, but how do you know?
    JOHN: You could say... I'm a primary source.

    ---
    SCENE NUMBER: {index}

    """,
)

summarize_prompt = ChatPromptTemplate.from_template(
    template="""Given a character script create a summary of the scene. Character script: {character_script}""",
)

# Loading a chat model:
model = ChatOpenAI(model='gpt-4o', api_key=config.OPENAI_API_KEY)

# Create the LCEL chains:
character_script_generation_chain = (
    {
        "characters": RunnablePassthrough(),
        "genre": RunnablePassthrough(),
        "previous_scene_summary": RunnablePassthrough(),
        "plot": RunnablePassthrough(),
        "scene": RunnablePassthrough(),
        "index": RunnablePassthrough(),
    }
    | character_script_prompt
    | model
    | StrOutputParser()
)

summarize_chain = summarize_prompt | model | StrOutputParser()

# You might want to use tqdm here to track the progress, or use all of the scenes:
for index, scene in enumerate(scenes[0:5]):
    
    # # Create a scene generation:
    scene_result = character_script_generation_chain.invoke(
        {
            "characters": story_result["characters"],
            "genre": "fantasy",
            "previous_scene_summary": previous_scene_summary,
            "index": index,
        }
    )

    # Store the generated scenes:
    generated_scenes.append(
        {"character_script": scene_result, "scene": scenes[index]}
    )

    # If this is the first scene then we don't have a previous scene summary:
    if index == 0:
        previous_scene_summary = scene_result
    else:
        # If this is the second scene or greater then we can use and generate a summary:
        summary_result = summarize_chain.invoke(
            {"character_script": scene_result}
        )
        previous_scene_summary = summary_result

df = pd.DataFrame(generated_scenes)
all_character_script_text = "\n".join(df.character_script.tolist())

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1500, chunk_overlap=200
)

docs = text_splitter.create_documents([all_character_script_text])
chain = load_summarize_chain(llm=model, chain_type="map_reduce")
summary = chain.invoke(docs)
print(summary['output_text'])