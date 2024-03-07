# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index.evaluation import RelevancyEvaluator

import nest_asyncio

nest_asyncio.apply()

import pandas as pd

from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.llms import OpenAI
from llama_index.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
)
from llama_index.evaluation import BatchEvalRunner

gpt4 = OpenAI(temperature=0, model="gpt-4")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

faithfulness_gpt4 = FaithfulnessEvaluator(service_context=service_context_gpt4)
relevancy_gpt4 = RelevancyEvaluator(service_context=service_context_gpt4)
correctness_gpt4 = CorrectnessEvaluator(service_context=service_context_gpt4)

runner = BatchEvalRunner(
    {"faithfulness": faithfulness_gpt4,
     "relevancy": relevancy_gpt4, 
     "correctness": correctness_gpt4},
    workers=8,
)

questions = []

with open("questions.txt", "r") as file:
    for line in file:
        # Remove the numbering and strip leading/trailing whitespace
        question = line.split('. ', 1)[-1].strip()
        questions.append(question)

questions = questions[240:]
reader = SimpleDirectoryReader("./data/Set_2/")
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

eval_results = runner.evaluate_response_strs(
    queries=questions, 
    response_strs=responses,
    contexts_list=source_nodes_contents,
)
    
data = {
    "Question": questions,
    "Response": responses,
    "Evaluation Faithfulness": [eval_results["faithfulness"][i].feedback for i in range(len(questions))],
    "Evaluation Relevancy": [eval_results["relevancy"][i].feedback for i in range(len(questions))],
    "Evaluation Correctness": [eval_results["correctness"][i].feedback for i in range(len(questions))]
}

df = pd.DataFrame(data)

existing_df = pd.read_excel("evaluation_results.xlsx")
    
updated_df = pd.concat([existing_df, df], ignore_index=True)

# Export to Excel
updated_df.to_excel("evaluation_results.xlsx", index=False)


