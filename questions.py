# import logging
# import sys
#
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index.legacy.evaluation import DatasetGenerator
# from llama_index.legacy import (
#     SimpleDirectoryReader,
#     ServiceContext,
# )
# from llama_index.legacy.llms import OpenAI
#
# from llama_index.legacy.prompts import PromptTemplate

from llama_index.core.evaluation import DatasetGenerator 
from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
)
    
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SentenceSplitter

# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")
openai_embed_model = OpenAIEmbedding(model='text-embedding-3-small')
# service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

# Gemini
gemini=Gemini(models='gemini-pro')
gemini_embed_model=GeminiEmbedding(model_name="models/embedding-001")
# service_context = ServiceContext.from_defaults(llm=gpt4)

Settings.llm = gemini
Settings.embed_model = gemini_embed_model
Settings.node_parser = SentenceSplitter(chunk_size=6900)
Settings.num_output = 80


text_question_template_str = (
    "Dưới đây là thông tin ngữ cảnh bằng tiếng Việt.\n---------------------\n{context_str}\n---------------------\n"
    "Dựa trên thông tin ngữ cảnh trên, hãy tạo ra các câu hỏi chỉ bằng tiếng Việt. "
    "Các câu hỏi phải liên quan đến nội dung ngữ cảnh và không sử dụng bất kỳ kiến thức ngoài ngữ cảnh đã cho.\n"
    "Truy vấn: {query_str}\n"
)
text_question_template = PromptTemplate(text_question_template_str)

reader = SimpleDirectoryReader("./data/Set_2/")
documents = reader.load_data()

data_generator = DatasetGenerator.from_documents(
    documents=documents,
    text_question_template=text_question_template,
    # service_context=service_context,
    # num_questions_per_chunk=2
)

eval_questions = data_generator.generate_questions_from_nodes()

# Create a formatted string
formatted_questions = "\n".join("{}. {}".format(i+1, question) for i, question in enumerate(eval_questions))

# print(formatted_questions)

# Save to a text file
with open("questions_gemini_2.txt", "w") as file:
    file.write(formatted_questions)
