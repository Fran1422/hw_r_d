from flask import Flask, request, jsonify
import os
import json
from fastavro import writer, parse_schema


app = Flask(__name__)

def convert_json_to_avro(raw_dir, stg_dir):
    # Створимо директорію, якщо її немає
    os.makedirs(stg_dir, exist_ok=True)

    # Якщо вона є і не пуста то очистимо її перед записом файлів
    for file in os.listdir(stg_dir):
        os.remove(os.path.join(stg_dir, file))

    # Задаємо схему avro
    avro_schema = {
        'doc': 'Sales',
        'name': 'Sales',
        'namespace': 'test',
        'type': 'record',
        'fields': [
            {'name': 'client', 'type': 'string'},
            {'name': 'purchase_date', 'type': 'string'},
            {'name': 'product', 'type': 'string'},
            {'name': 'price', 'type': 'int'},

        ],
    }

    parsed_schema = parse_schema(avro_schema)

    for filename in os.listdir(raw_dir):
        if filename.endswith('.json'):
            json_path = os.path.join(raw_dir, filename)
            avro_path = os.path.join(stg_dir, os.path.splitext(filename)[0] + '.avro')

            with open(json_path, 'r') as json_file:
                json_data = json.load(json_file)

            with open(avro_path, 'wb') as avro_file:
                writer(avro_file, parsed_schema, json_data)

    print("The conversion is successful!")

@app.route('/convert_to_avro', methods=['POST'])
def handle_conversion():
    data = request.json
    raw_dir = data.get('raw_dir')
    stg_dir = data.get('stg_dir')

    convert_json_to_avro(raw_dir, stg_dir)

    return jsonify({"message": f"Data from {raw_dir} has been converted to Avro and saved to {stg_dir}."}), 201

if __name__ == '__main__':
    app.run(port=8082)
