"""Main Module"""

import requests
import json
import random
from time import sleep
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.stackoverflow
collection = db.questions

QUESTIONS_URL = "https://api.stackexchange.com/2.3/questions?page={page}&order=asc&sort=activity&site=stackoverflow"
QUESTION_ANSWERS = "https://api.stackexchange.com/2.3/questions/{qid}/answers?order=desc&sort=activity&site=stackoverflow"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

with open("proxies.json", "r") as json_file:
    json_data = json_file.read()

proxies = json.loads(json_data)


def update_proxy():
    new_proxy = {"http": random.choice(proxies)}
    return new_proxy


proxy = update_proxy()


def get_questions(page):
    url = QUESTIONS_URL.format(page=page)
    response = requests.get(url, headers=HEADERS, proxies=proxy)
    questions = json.loads(response.text)
    print("QUESTION", page, questions["quota_remaining"], sep=":")
    return questions["items"]


def get_question_answers(question_id):
    url = QUESTION_ANSWERS.format(qid=question_id)
    response = requests.get(url, headers=HEADERS, proxies=proxy)
    answers = json.loads(response.text)
    print("QUESTION ANSWERS", question_id, answers["quota_remaining"], sep=":")
    return answers


def main():
    pages = 100

    for page_num in range(2, pages):
        questions = get_questions(page_num)
        sleep(1)

        for question in questions:
            question_id = question["question_id"]
            answers = get_question_answers(question_id)
            question["answers"] = answers["items"]

            if answers["quota_remaining"] < 10:
                proxy = update_proxy()

            db_id = collection.insert_one(question).inserted_id

            sleep(1)


if __name__ == "__main__":
    main()
