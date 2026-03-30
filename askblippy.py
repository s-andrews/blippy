from flask import Flask, request, render_template, Response
import ollama


app = Flask(__name__)

prompt_template = ""

with open("prompt.txt","rt",encoding="utf8") as infh:
    for line in infh:
        prompt_template += line

def ask_blippy(question):
    client = ollama.Client(verify=False, timeout=300, host="https://capstone.babraham.ac.uk/ollama/BAEBMJGBFMOGTCQAEFQH/")

    prompt=prompt_template+question

    stream = client.chat(
        model="gpt-oss:20b",
        stream=True,
        messages=[
            {
                "role":"user",
                "content": prompt
            }
        ]
    )
    output = ""

    for chunk in stream:
        output = output + chunk['message']['content']

    return output


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Serve the fixed HTML template
        return render_template("blippy.html")

    elif request.method == "POST":
        # Extract "question" from form data
        question = request.form.get("question", "")

        answer = ""

        if not question.isascii():
            answer = "Sorry, but unless your question is ASCII you can't ask-y it to Blippy"

        elif len(question) > 1000:
            answer = "Whoa there - it's supposed to be a question, not an essay - how about you give me the TLDR version of that?"

        else:
            # Pass to ask_blippy function
            answer = ask_blippy(question)

        # Return the result as plain text response
        return Response(answer, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)