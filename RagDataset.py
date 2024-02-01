from llama_index.llama_dataset import (
    LabelledRagDataset,
    CreatedBy,
    CreatedByType,
    LabelledRagDataExample,
)

example1 = LabelledRagDataExample(
    query="This is some user query.",
    query_by=CreatedBy(type=CreatedByType.HUMAN),
    reference_answer="This is a reference answer. Otherwise known as ground-truth answer.",
    reference_contexts=[
        "This is a list",
        "of contexts used to",
        "generate the reference_answer",
    ],
    reference_answer_by=CreatedBy(type=CreatedByType.HUMAN),
)

# a sad dataset consisting of one measely example
rag_dataset = LabelledRagDataset(examples=[example1])

from llama_index.llama_dataset.generator import RagDatasetGenerator
from llama_index import ServiceContext
from llama_index.llms import OpenAI
from llama_index import (
    SimpleDirectoryReader,
    ServiceContext,
)

import nest_asyncio

nest_asyncio.apply()

reader = SimpleDirectoryReader("./data/")
documents = reader.load_data()

llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo")
service_context = ServiceContext.from_defaults(llm=llm)

data_generator = RagDatasetGenerator.from_documents(
    documents=documents,
    service_context=service_context,
    num_questions_per_chunk=2
)

eval_questions = data_generator.generate_dataset_from_nodes()
