# import logging
# import sys
#
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.evaluation import DatasetGenerator
from llama_index import (
    SimpleDirectoryReader,
    ServiceContext,
)
from llama_index.llms import OpenAI

from llama_index.prompts import PromptTemplate

# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

text_question_template_str = (
    "Dưới đây là thông tin ngữ cảnh bằng tiếng Việt.\n---------------------\n{context_str}\n---------------------\n"
    "Dựa trên thông tin ngữ cảnh trên, hãy tạo ra các câu hỏi chỉ bằng tiếng Việt. "
    "Các câu hỏi phải liên quan đến nội dung ngữ cảnh và không sử dụng bất kỳ kiến thức ngoài ngữ cảnh đã cho.\n"
    "Truy vấn: {query_str}\n"
)
text_question_template = PromptTemplate(text_question_template_str)

reader = SimpleDirectoryReader("./data/")
documents = reader.load_data()

data_generator = DatasetGenerator.from_documents(documents, text_question_template=text_question_template, num_questions_per_chunk=2)

eval_questions = data_generator.generate_questions_from_nodes()

# Create a formatted string
formatted_questions = "\n".join("{}. {}".format(i+1, question) for i, question in enumerate(eval_questions))

# Save to a text file
with open("questions.txt", "w") as file:
    file.write(formatted_questions)
