"""
NuocGPT main server class
"""

import os
from pathlib import Path
import json
from flask import Flask, request, jsonify, render_template
import openai
from openai.error import ServiceUnavailableError
from pymongo import MongoClient, errors
from llama_index import StorageContext, load_index_from_storage, download_loader, GPTSimpleKeywordTableIndex


app = Flask(__name__)

# Vars and constants
TOPICS = ["politics", "vietnamese history", "vietnam war"]
SYSTEM_INSTRUCTION = f"You are NuocGPT, a conversational AI designed to answer questions about climate and water" \
                     f" issues in Vietnam. You can only answer questions in Vietnamese or English. You will not" \
                     f" comment or answer any questions related to these topics: {TOPICS}."
GPT3 = "gpt-3.5-turbo"
GPT4 = "gpt-3.5-turbo"


@app.route("/")
def home():
    """Render the homepage."""
    return render_template("index.html")


def gpt4critique(chat_log):
    """
    Create a critique for the given chat log using the GPT-4 model.

    :param chat_log: The chat log to critique.
    :return: The critiqued response.
    """
    messages = [chat_log[-1]]
    messages.append(
        {
            "role": "system",
            "content": f"Look at the previous response from NuocGPT; if the response's content belongs to this list of"
                       f" topics {TOPICS}, say that you cannot answer. Else repeat verbatim the previous NuocGPT"
                       f" content, do not modify it or mention the list of topics.",
        }
    )
    print(messages)
    response = openai.ChatCompletion.create(
        model=GPT4,
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None)

    # Extract the response text from the API response
    print(response)
    assistant_response = response["choices"][0]["message"]["content"].strip()
    return assistant_response


def gpt3critique(chat_log):
    """
    Create a critique for the given chat log using the GPT-3 model.

    :param chat_log: The chat log to critique.
    :return: The critiqued response.
    """
    prev_response = chat_log[-1]["content"]
    messages = [
        {
            "role": "user",
            "content": f"Look at the previous response from NuocGPT: {prev_response}; if the response's content"
                       f" belongs to this list of topics {TOPICS}, say that you cannot answer. Else repeat verbatim"
                       f" the previous NuocGPT content, do not modify it or mention the list of topics.",
        }
    ]
    print(messages)
    response = openai.ChatCompletion.create(
        model=GPT4,
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None)

    # Extract the response text from the API response
    print(response)
    assistant_response = response["choices"][0]["message"]["content"].strip()
    return assistant_response


def critique(chat_log, critique_model=GPT3):
    """
    Critique the given chat log using the specified model.

    :param chat_log: The chat log to critique.
    :param critique_model: The model to use for the critique. Defaults to GPT3.
    :return: The critiqued response.
    """
    try:
        if critique_model == GPT4:
            response = gpt4critique(chat_log)
        elif critique_model == GPT3:
            response = gpt3critique(chat_log)
        else:
            return chat_log[-1]["content"]
        return response
    except ServiceUnavailableError:
        # the critique service is not available, return the original content
        print(f"Critique model {critique_model} timed out")
        return chat_log[-1]["content"]


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat requests from the user.

    :return: The response from the chat bot.
    """
    user_message = request.form.get("message")
    original_question = user_message

    # Call the OpenAI API to get a response

    try:
        print(user_message)

        # if the pattern starts with "Query:", we just query the index; this is a test pattern for the index
        if "Query:" in user_message:
            query_str = user_message.replace("Query:", "")
            final_response = app.query_engine.query(query_str)
        else:
            if user_message:
                if app.use_llama_index:
                    context_response = app.query_engine.query(user_message)
                    user_message = f"Additional context information: {context_response}\nMy question: {user_message}"

                messages = [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_message},
                ]
            else:
                messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

            response = openai.ChatCompletion.create(
                model=GPT4,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                n=1,
                stop=None,
            )
            # Extract the response text from the API response
            print(response)
            assistant_response = response["choices"][0]["message"]["content"].strip(
            )

            messages.append({"role": "assistant", "content": assistant_response})

            final_response = critique(messages, "passthrough")

        app.user_message = user_message
        app.assistant_response = final_response

        return render_template("index.html", question=original_question, response=final_response)
    except ServiceUnavailableError:
        return render_template(
            "index.html",
            response="I am sorry but it seems that OpenAI API is not \
            avaiable at the current moment. Please try"
                     " again later.",
        )


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Handle feedback from the user.

    :return: A response indicating the feedback was received.
    """
    reaction = request.json.get("reaction")
    collection = app.db["ResponseLog"]
    # Store the reaction in the MongoDB collection
    feedback_data = {
        "id": "reaction",
        "question": app.user_message,
        "response": app.assistant_response,
        "reaction": reaction,
    }
    collection.insert_one(feedback_data)

    print("Data received:", feedback_data)
    # Return a response to the client (optional)
    return jsonify({"message": "Feedback received"})

#Post request using given data


def init_query_engine(param):
    json_reader = download_loader("JSONReader")
    loader = json_reader()
    documents = loader.load_data(Path('./data/testing.json'))

    index = GPTSimpleKeywordTableIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    param.index = index
    param.query_engine = query_engine


init_query_engine(app)

@app.route("/testdata", methods=["POST"])
def testdata():
    """
    Responds based on data we use
    """
    question = request.form.get("question")
    response = app.query_engine.query(question)

    messages = [
        {"role": "system", "content": f"This is additional context from our database \
            {response}; you can reply on them for answering user question."},
        {"role": "user", "content": str(question)},
    ]

    response = openai.ChatCompletion.create(
        model=GPT4,
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
    )
    # Extract the response text from the API response
    print(response)
    assistant_response = response["choices"][0]["message"]["content"].strip(
    )

    return json.dumps({"question": question, "response": assistant_response})

def init_openai_key():
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Check if API key works
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Hello world")
    print(completion.choices[0].text)


def load_mongo_db():
    uri = os.environ.get("MONGODB_URI")
    print("MongoDB URI", uri)
    cluster = MongoClient(uri)
    mongo_db = cluster["NuocDB"]
    collections = mongo_db.list_collection_names()

    # Try to ping the deployment and handle any exceptions that arise
    try:
        cluster.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        print("Available collections:", collections)
    except errors.ConnectionFailure as failure_exception:
        print(f"Failed to connect to MongoDB: {failure_exception}")
    return mongo_db


def load_llama_index():
    storage_dir = os.environ.get("LLAMA_INDEX_DIR", 'preliminary-llama-index')
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context, 'vector_index')
    return index


init_openai_key()
app.db = load_mongo_db()
app.user_message = ""
app.assistant_response = ""
app.use_llama_index = False

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5010))

    # Only enable llama index locally for now
    app.use_llama_index = True
    app.index = load_llama_index()
    app.query_engine = app.index.as_query_engine()

    app.run(host="0.0.0.0", port=port)
