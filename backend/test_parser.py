from app.engines.question_parser import QuestionPaperParser
parser = QuestionPaperParser()
text = """
Q 31. This is the first line of the question.
This is the second line of the question.
And this is the third line.
A. Option A
B. Option B
This is an extra line for Option B.
C. Option C
"""
questions = parser._parse_text_content(text, "Assamese", 8)
for q in questions:
    print("Q_TEXT:", q.question_text)
    for opt in q.options:
        print(f"OPT {opt.label}: {opt.text}")
