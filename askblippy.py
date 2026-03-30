from flask import Flask, request, render_template, Response

import random
import string
from pathlib import Path
import re

app = Flask(__name__)

prompt_template = ""

with open("prompt.txt","rt",encoding="utf8") as infh:
    for line in infh:
        prompt_template += line


def ask_question(question):
    # We make a random code and folder in the questions folder
    blippycode = ''.join(random.choices(string.ascii_uppercase, k=20))
    question_folder = Path(__file__).parent / "questions" / blippycode
    question_folder.mkdir()

    question_path = question_folder / "question.txt"
    with open(question_path,"wt",encoding="utf8") as out:
        print(question,file=out)

    return("BLIPPYCODE:"+blippycode)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Serve the fixed HTML template
        return render_template("blippy.html")

    elif request.method == "POST":
        # Extract "question" from form data

        if ("question") in request.form:
            # They're asking a question
            question = request.form.get("question", "")

            answer = ""

            if not question.isascii():
                answer = "Sorry, but unless your question is ASCII you can't ask-y it to Blippy"

            elif len(question) > 1000:
                answer = "Whoa there - it's supposed to be a question, not an essay - how about you give me the TLDR version of that?"

            else:
                # Pass to ask_blippy function
                answer = ask_question(question)

            # Return the result as plain text response
            return Response(answer, mimetype="text/plain")
        
        elif "BLIPPYCODE" in request.form:
            # They're checking to see if the asnwer is ready yet.
            blippycode = request.form.get("BLIPPYCODE")

            if not re.findall("^[A-Z]{20}$",blippycode):
                raise Exception("Not a valid blippy code")
            
            question_folder = Path(__file__).parent / "questions" / blippycode

            if not question_folder.exists():
                raise Exception("Not a valid blippy code")
            
            if (question_folder / "done").exists():
                answer = "ANSWER"
                with open(question_folder / "answer.txt","rt", encoding="utf8") as infh:
                    for line in infh:
                        answer += line

                return answer
            
            else:
                return "WAITING"



if __name__ == "__main__":
    app.run(debug=True)