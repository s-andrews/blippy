import ollama

prompt = ""

with open("prompt.txt","rt",encoding="utf8") as infh:
    for line in infh:
        prompt += line

client = ollama.Client(verify=False, timeout=300, host="https://capstone.babraham.ac.uk/ollama/JMMSIOJWZARIEXMEAWQZ/")


question = input("What do you want to ask: ")

prompt += question

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
    print(chunk['message']['content'], end='', flush=True)
