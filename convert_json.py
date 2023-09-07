import json
import csv

# Load JSON data from file
with open('gpt_finetuning_dataset.json', 'r') as json_file:
    data = json.load(json_file)

# Initialize a list to store selected messages
selected_messages = []

# Loop through messages and select those with roles "user" and "assistant"
for message in data['messages']:
    role = message.get('role')
    content = message.get('content')
    if role in ['user', 'assistant'] and content:
        selected_messages.append(content)

# Write selected messages to a TSV file
with open('output.tsv', 'w', newline='', encoding='utf-8') as tsv_file:
    tsv_writer = csv.writer(tsv_file, delimiter='\t')
    tsv_writer.writerow(['content'])  # Write header

    for message in selected_messages:
        tsv_writer.writerow([message])
