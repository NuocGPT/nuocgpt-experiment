import logging
import sys
import pandas as pd
import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.evaluation import DatasetGenerator, RelevancyEvaluator

from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
    Response,
)
from llama_index.llms import OpenAI

gpt4 = OpenAI(temperature=0, model="gpt-4")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

evaluator_gpt4 = RelevancyEvaluator(service_context=service_context_gpt4)

questions = []

with open("result/questions.txt", "r") as file:
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


# query_engine = vector_index.as_query_engine()
# response_vector = query_engine.query(questions[3])
# result = evaluator_gpt4.evaluate_response(query=questions[3], response=response_vector)
# 
# print(result)

responses= []

query_engine = vector_index.as_query_engine()
for question in questions:
    # Generate response for the current question
    response_vector = query_engine.query(question)
    
    responses.append(response_vector)

# Generate QA file in pretty format
with open("questions_and_responses.txt", "w") as file:
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        file.write("{}. {}\n- {}\n".format(i, question, response))

# df = pd.DataFrame(all_results)
# df.to_csv("Some questions_and_answers.csv", index=False)
