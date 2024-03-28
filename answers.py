# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index.evaluation import RelevancyEvaluator

import nest_asyncio

nest_asyncio.apply()

import pandas as pd

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Settings,
)
    
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
    BatchEvalRunner,
)
    
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

gpt4 = OpenAI(temperature=0, model="gpt-4")
openai_embed_model = OpenAIEmbedding(model='text-embedding-3-small')

gemini=Gemini(models='gemini-pro')
gemini_embed_model = GeminiEmbedding(model_name="models/embedding-001")

Settings.llm = gemini
Settings.embed_model = gemini_embed_model

# faithfulness_gpt4 = FaithfulnessEvaluator(service_context=service_context_gpt4)
# relevancy_gpt4 = RelevancyEvaluator(service_context=service_context_gpt4)
# correctness_gpt4 = CorrectnessEvaluator(service_context=service_context_gpt4)

faithfulness_gemini = FaithfulnessEvaluator(llm=gemini)
relevancy_gemini = RelevancyEvaluator(llm=gemini)
correctness_gemini = CorrectnessEvaluator(llm=gemini)

runner = BatchEvalRunner(
    {"faithfulness": faithfulness_gemini,
     "relevancy": relevancy_gemini, 
     "correctness": correctness_gemini},
    workers=8,
)

questions = []

with open("questions_gemini.txt", "r") as file:
    for line in file:
        # Remove the numbering and strip leading/trailing whitespace
        question = line.split('. ', 1)[-1].strip()
        questions.append(question)

questions = questions[18:20]
reader = SimpleDirectoryReader("./data/Set_1/")
documents = reader.load_data()

# create vector index
vector_index = VectorStoreIndex.from_documents(documents)

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

# df = pd.DataFrame(data)

# existing_df = pd.read_excel("evaluation_results_gemini_3.xlsx")
    
# updated_df = pd.concat([existing_df, df], ignore_index=True)

# Export to Excel
# updated_df.to_excel("evaluation_results_gemini_3.xlsx", index=False)
# df.to_excel("evaluation_results_gemini_3.xlsx", index=False)

print(responses)



