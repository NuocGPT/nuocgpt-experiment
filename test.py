import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index import (
    TreeIndex,
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    Response,
)
from llama_index.llms import OpenAI
from llama_index.evaluation import RelevancyEvaluator
import pandas as pd

pd.set_option("display.max_colwidth", 0)

gpt3 = OpenAI(temperature=0, model="gpt-3.5-turbo")
service_context_gpt3 = ServiceContext.from_defaults(llm=gpt3)

evaluator = RelevancyEvaluator(service_context=service_context_gpt3)

documents = SimpleDirectoryReader("./data/").load_data()

vector_index = VectorStoreIndex.from_documents(
    documents, service_context=ServiceContext.from_defaults(chunk_size=512)
)

query_str = (
    "Xâm nhập mặn đã gây thiệt hại đối với ngành nào?"
)
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query(query_str)
eval_result = evaluator.evaluate_response(
    query=query_str, response=response_vector
)


