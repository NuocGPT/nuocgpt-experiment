import csv
import json

csv_file_path = 'sheet.csv'
json_file_path = 'testing.json'

data = []

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        data.append(row)

with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

print(f'CSV file "file" converted to JSON file "E" successfully.')







