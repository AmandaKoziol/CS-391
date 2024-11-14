from openai import OpenAI
import config
import time

client = OpenAI(api_key=config.OPENAI_API_KEY)

def waiting_assistant_in_progress(thread_id, run_id, max_loops=20):
    for _ in range(max_loops):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run.status != "in_progress":
            break
        time.sleep(1)
    return run


# Add the files to the assistant's file search tool
vector_store = client.beta.vector_stores.create(name="CS 391 Books")
file_paths = ["devel_chap1.pdf","prompt_chap1.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)


#create assistant
assistant = client.beta.assistants.create(
    name="Study expert",
    instructions="You're an expert on making study guides, and you're going to answer \
                    my questions about soem books using the file I've given you.",
    model="gpt-4-turbo-preview",
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# create a thread
thread = client.beta.threads.create()

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What are the Five Principles of Prompting?"
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)


run = waiting_assistant_in_progress(thread.id, run.id)
messages = client.beta.threads.messages.list(thread_id=thread.id)
print(messages.data[0].content[0].text.value)

