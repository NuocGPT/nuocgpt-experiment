# attach to the same event-loop
import nest_asyncio

nest_asyncio.apply()

import pandas as pd

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
)
from llama_index.llms import OpenAI
from llama_index.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
)

# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")
# llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

faithfulness_gpt4 = FaithfulnessEvaluator(service_context=service_context_gpt4)
relevancy_gpt4 = RelevancyEvaluator(service_context=service_context_gpt4)
correctness_gpt4 = CorrectnessEvaluator(service_context=service_context_gpt4)

# Loading Data
reader = SimpleDirectoryReader("./data/")
documents = reader.load_data()

# create vector index
vector_index = VectorStoreIndex.from_documents(
    documents, service_context=service_context_gpt4
)

from llama_index.evaluation import BatchEvalRunner

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
        
from answers import (responses, source_nodes_contents)

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

# Create DataFrame
df = pd.DataFrame(data)

# Export to Excel
df.to_excel("evaluation_results.xlsx", index=False)
