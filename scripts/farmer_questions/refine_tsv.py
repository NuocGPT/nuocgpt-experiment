def extract_questions_answers_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        text = f.read()

    print(text)
    # Split the text by the delimiter

    chunks = text.split('\t')
    print(len(chunks))
    count = 0
    questions_answers = []
    while count < len(chunks):
        question = chunks[count].strip().replace("\n", "")
        answer = chunks[count + 1].strip().replace("\n", "")
        context = chunks[count + 2].strip().replace("\n", "")
        questions_answers.append((question, answer, context))
        print("question")
        print(question)
        print("--------")
        print("answer")
        print(answer)
        print("--------")
        print("context")
        print(context)
        count += 3

    return questions_answers

def write_to_tsv(questions_answers, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("Question\tAnswer\tContext\n")
        for qa in questions_answers:
            f.write(f"{qa[0]}\t{qa[1]}\t{qa[2]}\n")

if __name__ == "__main__":
    file_name = f"qa_gpt_finetuning.tsv"
    qa_list = extract_questions_answers_from_file(file_name)

    # Write to TSV
    write_to_tsv(qa_list, "qa_gpt_finetuning_improved.tsv")

    print("File exported to combined_output.tsv!")
