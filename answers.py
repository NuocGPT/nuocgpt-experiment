# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index.evaluation import RelevancyEvaluator

from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.llms import OpenAI

gpt4 = OpenAI(temperature=0, model="gpt-4")
# llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

questions = []

with open("questions.txt", "r") as file:
    for line in file:
        # Remove the numbering and strip leading/trailing whitespace
        question = line.split('. ', 1)[-1].strip()
        questions.append(question)

reader = SimpleDirectoryReader("./data/")
documents = reader.load_data()

# create vector index
vector_index = VectorStoreIndex.from_documents(
    documents, service_context=service_context_gpt4
)

responses = []
source_nodes_contents = [] 

query_engine = vector_index.as_query_engine()
for question in questions:
    # Generate response for the current question
    response_vector = query_engine.query(question)
    responses.append(response_vector.response)

    # Generate the context for later evaluation
    current_source_contents = []
    for source_node in response_vector.source_nodes:
        current_source_contents.append(source_node.get_content())
    
    source_nodes_contents.append(current_source_contents)

    
# Generate QA file in prettier format
with open("questions_and_responses.txt", "w") as file:
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        file.write("{}. {}\n- {}\n".format(i, question, response))
