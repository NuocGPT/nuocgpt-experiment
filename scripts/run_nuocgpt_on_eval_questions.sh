#!/bin/bash

# The output file
output_file="../nuocgpt_eval_answers.jsonl"

# Ensure the output file is empty
> "$output_file"

# Check if environment variables are set
if [[ -z "$CONVERSATION_ID" ]] || [[ -z "$NUOCGPT_API_TOKEN" ]]; then
  echo "Error: CONVERSATION_ID and NUOCGPT_API_TOKEN must be set as environment variables." >&2
  exit 1
fi

# Base API URL
api_url="https://api-beta.nuocgpt.ai/v1/conversations/$CONVERSATION_ID/messages"

# Iterate over each line in ../eval_questions.txt
while IFS= read -r line
do
  # Use the line to replace QUESTION in the JSON data
  json_data=$(jq -nc --arg question "$line" '{"message": $question}')

  # Execute the cURL command
  curl -X 'POST' \
    "$api_url" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $NUOCGPT_API_TOKEN" \
    -d "$json_data" >> "$output_file"

  # Append a newline to separate JSON objects
  echo "" >> "$output_file"
done < "../eval_questions.txt"
