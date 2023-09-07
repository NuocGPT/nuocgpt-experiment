import re

# Read the content of the input file
with open('gpt_finetuning_dataset.json', 'r', encoding='utf-8') as input_file:
    data = input_file.read()

# Split the input data into individual message blocks
message_blocks = re.split(r'\s*\{\s*"\w+"\s*:\s*\[\s*', data)[1:]

# Reformat and encapsulate the message blocks in standard JSON format
formatted_blocks = []
for block in message_blocks:
    formatted_block = '{\n  "messages": [\n' + re.sub(r'\n\s*', '\n    ', block.strip()) + '\n  ]\n}'
    formatted_blocks.append(formatted_block)

# Write the formatted blocks to an output file
with open('output.json', 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(formatted_blocks))
