"""Simple script to extract text from PDFs"""

import argparse
import json
import os
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader


def extract_text_from_pdf(pdf_path):
    print(f"Loading PDF data from {pdf_path}...")
    required_exts = [".pdf"]
    documents = SimpleDirectoryReader(pdf_path, required_exts=required_exts, recursive=True).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index, documents


def generate_document_summary(documents, output_path="extracted_files.txt"):
    document_data = []
    for document in documents:
        document_data.append(
            {
                "file_name": document.metadata["file_name"],
                "page": document.metadata["page_label"],
                "text_length": len(document.text),
            }
        )
    document_data.sort(key=lambda d: (d["file_name"], int(d["page"])))

    with open(output_path, 'w', encoding="utf-8") as writer:
        for document in document_data:
            writer.write(json.dumps(document) + "\n")


def persist_index_to_storage(index, output_path='preliminary-llama-index'):
    print(f"Persisting index to {output_path}")
    index.set_index_id("vector_index")
    index.storage_context.persist(output_path)


def interactive_mode(index):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        print("Invalid OpenAI API key - please check your env variable")
        return

    query_engine = index.as_query_engine()
    prompt = input("Input a question:")
    while prompt not in ["quit", "q"]:
        response = query_engine.query(prompt)
        print(response)
        prompt = input("Input a question, type [quit, q] to quit:")


def main():
    parser = argparse.ArgumentParser(description="PDF Text Extractor")
    parser.add_argument("--interactive", help="Enter interactive mode to query your index", action="store_true")
    parser.add_argument("--input_path", help="Directory to read PDFs from", default="data/PDFs")
    parser.add_argument("--output_path", help="Directory to save the index data", default="preliminary-llama-index")
    args = parser.parse_args()

    index, documents = extract_text_from_pdf(args.input_path)
    persist_index_to_storage(index, args.output_path)
    generate_document_summary(documents, output_path=args.output_path + "/extracted_files.jsonl")
    if args.interactive:
        interactive_mode(index)


if __name__ == "__main__":
    main()
