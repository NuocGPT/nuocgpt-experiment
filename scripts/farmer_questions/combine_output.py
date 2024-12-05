def extract_questions_answers_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split the text by the delimiter
    sections = text.split('-------')

    # Extract questions and answers
    questions_answers = []
    for section in sections:
        if "Question:" in section and "Answer:" in section:
            question = section.split("Question:")[1].split("Answer:")[0].strip()
            answer = section.split("Answer:")[1].strip().replace("\n", "")
            questions_answers.append((question, answer))

    return questions_answers

def write_to_tsv(questions_answers, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("Question\tAnswer\n")
        for qa in questions_answers:
            f.write(f"{qa[0]}\t{qa[1]}\n")

if __name__ == "__main__":
    all_qa = []
    for i in range(1, 10):
        file_name = f"output_{i}.txt"
        qa_list = extract_questions_answers_from_file(file_name)
        all_qa.extend(qa_list)

    # Write to TSV
    write_to_tsv(all_qa, "combined_output.tsv")

    print("File exported to combined_output.tsv!")
