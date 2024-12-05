import json

instruction = "You are a climate AI interface that only answers to questions and content related to salinity intrusion and Mekong Delta of Vietnam. For the unrelated questions, respond that you cannot answer, in the language of the query."


def tsv_to_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding="utf-8") as infile, open(output_file, 'w', encoding="utf-8") as outfile:
        # Get the headers (column names) from the first line
        headers = infile.readline().strip().split('\t')
        assert headers[0] == "Question"
        assert headers[1] == "Answer"

        # For each line in the TSV
        for line in infile:
            # Split the line into fields
            fields = line.strip().split('\t')

            # Create a dictionary using the headers and the fields
            record = {"question": fields[0], "answer": fields[1]}
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": record["question"]},
                {"role": "assistant", "content": record["answer"]}
            ]

            # Write the dictionary as a JSON-formatted string to the output file
            outfile.write(json.dumps({"messages": messages}) + '\n')


input_name = "qa_gpt_finetuning_09_05.tsv"
output_name = input_name.replace("tsv", "jsonl")
# Use the function
tsv_to_jsonl(input_name, output_name)
