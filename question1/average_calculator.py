from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

window_size = 10
number_store = []
lock = threading.Lock()

def fetch_numbers(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return response.json().get("numbers", [])
    except requests.exceptions.RequestException:
        pass
    return []

def get_url(number_id):
    if number_id == 'p':
        return "http://20.244.56.144/test/prime"
    elif number_id == 'f':
        return "http://20.244.56.144/test/fibo"
    elif number_id == 'e':
        return "http://20.244.56.144/test/even"
    elif number_id == 'r':
        return "http://20.244.56.144/test/rand"
    else:
        return None

def update_store(new_numbers):
    with lock:
        for num in new_numbers:
            if num not in number_store:
                number_store.append(num)
        while len(number_store) > window_size:
            number_store.pop(0)

def calculate_average(numbers):
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    url = get_url(number_id)
    if url is None:
        return jsonify({"error": "Invalid number ID"}), 400

    prev_state = list(number_store)
    new_numbers = fetch_numbers(url)
    update_store(new_numbers)

    avg = calculate_average(number_store)
    return jsonify({
        "windowPrevState": prev_state,
        "windowCurrState": list(number_store),
        "numbers": new_numbers,
        "avg": avg
    })

if __name__ == '__main__':
    app.run(port=9876)
