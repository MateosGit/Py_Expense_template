import json

def read_json_file(file):
    with open(file, 'r') as openfile:
        return json.load(openfile)

def write_json_file(file, json_data):
    with open(file, "w") as outfile:
        json.dump(json_data, outfile)