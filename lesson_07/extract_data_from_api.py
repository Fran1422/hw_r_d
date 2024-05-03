from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

def fetch_sales_data(raw_dir, date):
    AUTH_TOKEN = os.getenv('AUTH_TOKEN')
    page = 1
    while True:
        response = requests.get(
            url=f'https://fake-api-vycpfa6oca-uc.a.run.app/sales',
            params={'date': date, 'page': page},
            headers={'Authorization': AUTH_TOKEN},
        )

        if response.status_code != 200 or not response.json():
            break

        sales_data = response.json()

        # Збереження даних у файл
        file_name = f'{raw_dir}/sales_{date}_{page}.json'
        with open(file_name, 'w') as file:
            json.dump(sales_data, file)

        print(f"Data saved to {file_name}")
        page += 1

@app.route('/sales', methods=['POST'])
def handle_sales_data():
    data = request.json
    date = data.get('date')
    raw_dir = data.get('raw_dir')

    # Перед запуском переконайтеся, що директорія чиста
    os.makedirs(raw_dir, exist_ok=True)
    # Очищення вмісту директорії перед записом нових файлів
    for file in os.listdir(raw_dir):
        os.remove(os.path.join(raw_dir, file))

    # Виклик функції для отримання та збереження даних
    fetch_sales_data(raw_dir, date)

    return jsonify({"message": f"Data for {date} has been fetched and saved to {raw_dir}."}), 201

if __name__ == '__main__':
    app.run(port=8081)
