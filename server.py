import os
from flask import Flask, request, jsonify, render_template
import openai
from openai.error import ServiceUnavailableError
from pymongo import MongoClient

uri = os.environ.get("MONGODB_URI")
print("MongoDB URI", uri)
cluster = MongoClient(uri)
db = cluster['NuocDB']
collections = db.list_collection_names()

try:
    cluster.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Check if API key works
completion = openai.Completion.create(model="text-davinci-003", prompt="Hello world")
print(completion.choices[0].text)

# Vars and constants
global_question = ""
global_response = ""
TOPICS = ["politics", "vietnamese history", "vietnam war"]
SYSTEM_INSTRUCTION = f"You are NuocGPT, a conversational AI designed to answer questions about climate and water issues in Vietnam. You can only answer questions in Vietnamese or English. You will not comment or answer any questions related to these topics: {TOPICS}."
GPT3 = "gpt-3.5-turbo"
GPT4 = "gpt-4"

@app.route('/')
def home():
    return render_template('index.html')


def critique(chat_log):
    try:
        messages = [chat_log[-1]]
        messages.append({"role": "system", "content": f"Look at the previous response from NuocGPT; if the response's content belongs to this list of topics {TOPICS}, say that you cannot answer. Else repeat verbatim the previous NuocGPT content, do not modify it or mention the list of topics."})
        print(messages)
        response = openai.ChatCompletion.create(
            model=GPT3,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            n=1,
            stop=None
        )

        # Extract the response text from the API response
        print(response)
        assistant_response = response['choices'][0]['message']["content"].strip()
        return assistant_response
    except ServiceUnavailableError:
        # the critique service is not available, return the original content
        return chat_log[-1]["content"]


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message')

    # Call the OpenAI API to get a response
    try:
        print(user_message)
        messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}, {"role": "user", "content": user_message}]
        response = openai.ChatCompletion.create(
            model=GPT4,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            n=1,
            stop=None
        )

        # Extract the response text from the API response
        print(response)
        assistant_response = response['choices'][0]['message']["content"].strip()

        messages.append({"role": "assistant", "content": assistant_response})

        critiqued_response = critique(messages)

        global global_question
        global_question = user_message
        global global_response
        global_response = critiqued_response

        return render_template('index.html', response=critiqued_response)
    except ServiceUnavailableError:
        return render_template('index.html', response="I am sorry but it seems that OpenAI API is not avaiable at the current moment. Please try again later.")


@app.route('/feedback', methods=['POST'])
def feedback():
    reaction = request.json.get('reaction')
    collection = db["ResponseLog"]
    # Store the reaction in the MongoDB collection
    feedback_data = {
        'id' : 'reaction',
        'question': global_question,
        'response':global_response,
        'reaction': reaction
    }
    collection.insert_one(feedback_data)

    print("Data received:", feedback_data)  # Add this line to print the data

    # Return a response to the client (optional)
    return jsonify({'message': 'Feedback received'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port)
