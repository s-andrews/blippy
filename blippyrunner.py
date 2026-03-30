#!/usr/bin/env python3

# This script polls the questions asked of blippy and answers
# them in turn.

from pathlib import Path
import time
from queue import Queue
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ollama

task_queue = Queue()

prompt_template = ""

with open("prompt.txt","rt",encoding="utf8") as infh:
    for line in infh:
        prompt_template += line

# Your processing function
def process_directory(path):
    path = Path(path)

    print(f"Processing: {path}")

    if (path/"done").exists():
        return # Don't process questions we've already done.

    question = ""
    with open(path / "question.txt","rt",encoding="utf8") as infh:
        for line in infh:
            question += line


    answer = ask_blippy(question)

    with open(path / "answer.txt","wt",encoding="utf8") as out:
        print(answer, file=out)

    with open(path / "done","w"):
        pass

    print(f"Done: {path}")

# Worker thread
def worker():
    while True:
        path = task_queue.get()
        try:
            process_directory(path)
        finally:
            task_queue.task_done()

# Event handler
class NewDirHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print(f"Detected new directory: {event.src_path}")
            task_queue.put(event.src_path)


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


if __name__ == "__main__":
    path_to_watch = Path(__file__).parent / "questions"

    event_handler = NewDirHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()

    # Start worker threads
    for _ in range(4):  # adjust concurrency
        Thread(target=worker, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
