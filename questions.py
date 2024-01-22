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

from llama_index.prompts import PromptTemplate

# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")
service_context_gpt4 = ServiceContext.from_defaults(llm=gpt4)

evaluator_gpt4 = RelevancyEvaluator(service_context=service_context_gpt4)

text_question_template_str = (
    "Dưới đây là thông tin ngữ cảnh bằng tiếng Việt.\n---------------------\n{context_str}\n---------------------\n"
    "Dựa trên thông tin ngữ cảnh trên, hãy tạo ra các câu hỏi chỉ bằng tiếng Việt. "
    "Các câu hỏi phải liên quan đến nội dung ngữ cảnh và không sử dụng bất kỳ kiến thức ngoài ngữ cảnh đã cho.\n"
    "Truy vấn: {query_str}\n"
)
text_question_template = PromptTemplate(text_question_template_str)

reader = SimpleDirectoryReader("./data/")
documents = reader.load_data()

data_generator = DatasetGenerator.from_documents(documents, text_question_template=text_question_template)

eval_questions = data_generator.generate_questions_from_nodes()

# Create a formatted string
formatted_questions = "\n".join("{}. {}".format(i+1, question) for i, question in enumerate(eval_questions))

# Print the formatted questions
# print(formatted_questions)

# Save to a text file
with open("questions.txt", "w") as file:
    file.write(formatted_questions)


# create vector index
vector_index = VectorStoreIndex.from_documents(
    documents, service_context=service_context_gpt4
)

# query_engine = vector_index.as_query_engine()
# response_vector = query_engine.query(eval_questions[3])
# eval_result = evaluator_gpt4.evaluate_response(query=eval_questions[3], response=response_vector)
# 
# print(eval_result)

all_results = []

query_engine = vector_index.as_query_engine()
for question in eval_questions[4:10]:
    # Generate response for the current question
    response_vector = query_engine.query(question)
    
    # Evaluate the response
    eval_result = evaluator_gpt4.evaluate_response(query=question, response=response_vector)

    result = {
        "Question": question,
        "Response": response_vector,
        "Evaluation": eval_result
    }
    
    print(eval_result)
    all_results.append(result)
    time.sleep(3)

df = pd.DataFrame(all_results)
df.to_csv("Some questions_and_answers.csv", index=False)
