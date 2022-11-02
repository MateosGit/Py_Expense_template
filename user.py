from PyInquirer import prompt
import json
import uuid

USERS_DATA_FILE = "users.json"

def read_json_file():
    with open(USERS_DATA_FILE, 'r') as openfile:
        return json.load(openfile)

users_data = read_json_file()

def write_json_file():
    with open(USERS_DATA_FILE, "w") as outfile:
        json.dump(users_data, outfile)

user_questions = [
    {
        "type": "input",
        "name": "name",
        "message": "User name: ",
    }
]

def add_user():
    infos = prompt(user_questions)
    user_id = str(uuid.uuid4())
    users_data[user_id] = infos
    write_json_file()
    return True