import argparse
import csv
import xml.etree.ElementTree as ET

# Обрабатываем аргументы командной строки
parser = argparse.ArgumentParser(description='Simple XML-to-CSV parser for nosql_system')
parser.add_argument('--input_path', help='Path to XML input file')
parser.add_argument('--output_path', help='Path to CSV output file')
args = parser.parse_args()

# Определяем пути к файлам ввода-вывода
input_path = args.input_path
output_path = args.output_path

# Открываем исходный XML-файл
tree = ET.parse(input_path)
root = tree.getroot()

# Открываем CSV-файл для записи
with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
    # Создаем объект writer
    fieldnames = ["Id", "Reputation", "CreationDate", "DisplayName", "LastAccessDate", "WebsiteUrl", "Location",
                  "AboutMe", "Views", "UpVotes", "DownVotes", "AccountId"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Записываем заголовки столбцов
    writer.writeheader()

    # Парсим XML и записываем данные в CSV
    for row in root.findall('row'):
        data = {
            "Id": row.get('Id'),
            "Reputation": row.get('Reputation'),
            "CreationDate": row.get('CreationDate'),
            "DisplayName": row.get('DisplayName'),
            "LastAccessDate": row.get('LastAccessDate'),
            "WebsiteUrl": row.get('WebsiteUrl'),
            "Location": row.get('Location'),
            # "AboutMe": row.get('AboutMe'),
            "Views": row.get('Views'),
            "UpVotes": row.get('UpVotes'),
            "DownVotes": row.get('DownVotes'),
            "AccountId": row.get('AccountId')
        }
        writer.writerow(data)
