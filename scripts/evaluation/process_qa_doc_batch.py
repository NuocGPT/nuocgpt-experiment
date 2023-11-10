import os
import time
import argparse

import openai
import pandas as pd
import boto3
import tempfile
import shutil
from llama_index import SimpleDirectoryReader, ServiceContext
from llama_index.llms import OpenAI
from llama_index.evaluation import DatasetGenerator
from llama_index import VectorStoreIndex

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key  = os.getenv('OPENAI_API_KEY')


GPT_4_CONTEXT = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-4", temperature=0)
)

QUESTION_GEN_QUERY = (
                     "You are a simple farmer "
                     "in Mekong Delta Vietnam. You are interested to learn about salinity intrusion and its effects in the Mekong Delta in Vietnam. "
                     "Using the provided context from a report on climate change and the Mekong Delta, formulate "
                     "a single question in Vietnamese that captures an important fact from the context. Restrict the question to the context information provided, "
                     "and do not include any reference to specific equation, figure, diagram or table, report, or paper. "
                     "Do not ask anything that requires deep technical and mathematical knowledge."
)

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a climate AI interface that only answers to questions and content "
        "related to salinity intrusion and Mekong Delta of Vietnam. For the unrelated "
        "questions, respond that you cannot answer, in the language of the query."
    )
}

s3 = boto3.client('s3')


def generate_qa_df(dir_path, llm_context=GPT_4_CONTEXT, question_gen_query=QUESTION_GEN_QUERY):
    qac = []
    # Iterate over each file in the directory
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        print('Processing the following document: ', filename)

        # Check if it's a file and not a sub-directory
        if os.path.isfile(file_path):
            doc = SimpleDirectoryReader(
                input_files=[file_path]
            ).load_data()

            dataset_generator = DatasetGenerator.from_documents(
                doc[:],
                num_questions_per_chunk=100,
                question_gen_query=question_gen_query,
                service_context=llm_context,
            )
            time.sleep(4)

            questions = dataset_generator.generate_questions_from_nodes()

            index = VectorStoreIndex.from_documents(doc, service_context=llm_context)

            query_engine = index.as_query_engine(similarity_top_k=4)

            contexts = []
            answers = []
            for question in questions:
                response = query_engine.query(question)
                # contexts.append([x.node.get_content() for x in response.source_nodes])
                contexts.append(filename)
                answers.append(str(response))
                time.sleep(1)

            for q, a, c in zip(questions, answers, contexts):
                qac.append({'Question': q, 'Answer': a, 'Document Source': c})
            time.sleep(2)

    qac_df = pd.DataFrame(qac)

    # Clean up dataframe
    qac_df['Question'] = qac_df['Question'].str.replace("\n", "")
    qac_df['Answer'] = qac_df['Answer'].str.replace("\n", "")
    qac_df = qac_df[~qac_df['Answer'].str.contains('The context does not provide')]
    qac_df.drop_duplicates(subset='Question', keep='last', inplace=True)
    
    return qac_df


def process_qa_df_for_gpt_finetuning(df, system_message=SYSTEM_MESSAGE):
    training_examples = []
    for q, a in zip(df['Question'].tolist(), df['Answer'].tolist()):
        q_message = {"role": "user", "content": q}
        a_message = {"role": "assistant", "content": a}
        training_examples.append([system_message, q_message, a_message])
    return pd.DataFrame({"messages": training_examples})


def download_doc_batch_to_tmpdir(bucket_name='qa-documents-to-process', prefix=''):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Temporary directory created at: {temp_dir}")

    if len(prefix) > 0 and prefix[-1] != '/':
        prefix += '/'

    # List all files in the bucket with the specified prefix
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Download each file to the temporary directory
    for obj in objects.get('Contents', []):
        file_name = obj['Key']

        # Skip if the object is a directory-like prefix
        if file_name.endswith('/'):
            continue

        print(f"Downloading {file_name}...")

        # Download the file to the temporary directory
        local_file_path = os.path.join(temp_dir, file_name.split('/')[-1])
        s3.download_file(bucket_name, file_name, local_file_path)

    print("All files downloaded!")
    return temp_dir


def save_df_to_temp_file(df, file_extension):
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
    
    if file_extension == '.tsv':
        df.to_csv(temp_file.name, sep='\t', index=False, encoding='utf-8')
    elif file_extension == '.jsonl':
        temp_file.close()
        with open(temp_file.name, 'w', encoding='utf-8') as file:
            df.to_json(file, force_ascii=False, orient='records', lines=True)
    else:
        raise ValueError("Please pass in either .tsv or .jsonl file extension")

    return temp_file


def upload_temp_file_to_s3(temp_file, s3_key, bucket_name='processed-qas', prefix=''):
    if len(prefix) > 0 and prefix[-1] != '/':
        prefix += '/'
    
    # Prepend the prefix to the s3_key
    full_s3_key = f"{prefix}{s3_key}" if prefix else s3_key
    
    with open(temp_file.name, 'rb') as file:
        s3.upload_fileobj(file, bucket_name, full_s3_key)

    print(f"File uploaded to {bucket_name}/{full_s3_key}")


def main(bucket_prefix, batch_name):
    doc_batch_temp_dir = download_doc_batch_to_tmpdir(prefix=bucket_prefix)
    qac_df = generate_qa_df(doc_batch_temp_dir)
    qac_tsv_tmp_file = save_df_to_temp_file(qac_df, '.tsv')
    upload_temp_file_to_s3(qac_tsv_tmp_file, batch_name + '.tsv', prefix='tsvs')
    gpt_df = process_qa_df_for_gpt_finetuning(qac_df)
    gpt_jsonl_tmp_file = save_df_to_temp_file(gpt_df, '.jsonl')
    upload_temp_file_to_s3(gpt_jsonl_tmp_file, batch_name + '.jsonl', prefix='jsonls')

    # Remove temporary directory and files
    shutil.rmtree(doc_batch_temp_dir)
    print(f"Temporary directory {doc_batch_temp_dir} removed.")
    os.remove(qac_tsv_tmp_file.name)
    os.remove(gpt_jsonl_tmp_file.name)
    print(f"Temporary files {qac_tsv_tmp_file} and {gpt_jsonl_tmp_file} removed as well.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process prefix of qa-documents-to-process S3 bucket and batch name.")
    
    # Add arguments for bucket prefix and batch name
    parser.add_argument("bucket_prefix", help="The prefix of the qa-documents-to-process S3 bucket.")
    parser.add_argument("batch_name", help="The name of the batch of files.")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with the provided arguments
    main(args.bucket_prefix, args.batch_name)
