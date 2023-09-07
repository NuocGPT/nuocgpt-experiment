import openai

# Initialize the OpenAI API client
openai.api_key = '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'

# Set the system level instruction
instruction = "You are a climate AI interface that only answers to questions and content related to salinity intrusion and Mekong Delta of Vietnam. For the unrelated questions, respond that you cannot answer, in the language of the query."

def get_answer(question, model="gpt-4", max_tokens=2000):
    """Query the OpenAI API for an answer with the given instruction."""
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": question}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages = messages,
        temperature=0.2,
        max_tokens=max_tokens,
        frequency_penalty=0.0
    )

    return response.choices[0]["message"]["content"].strip()

def main():
    with open('farmer_questions.txt', 'r') as file:
        questions = [line.strip() for line in file.readlines()]

    # Variables to manage chunks
    q_a_pairs = []
    file_counter = 1

    for question in questions:
        answer = get_answer(question)
        print("Question:", question)
        print("Answer:", answer)
        q_a_pairs.append((question, answer))

        if len(q_a_pairs) >= 20:
            with open(f'output_{file_counter}.txt', 'w') as out_file:
                for q, a in q_a_pairs:
                    out_file.write(f"Question: {q}\nAnswer: {a}\n-------\n")
            print(f"Saved to output_{file_counter}.txt")
            q_a_pairs = []
            file_counter += 1

    # Save any remaining Q&A pairs
    if q_a_pairs:
        with open(f'output_{file_counter}.txt', 'w') as out_file:
            for q, a in q_a_pairs:
                out_file.write(f"Question: {q}\nAnswer: {a}\n\n")

if __name__ == "__main__":
    main()
