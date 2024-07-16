from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
number_store = []
lock = threading.Lock()

# Function to fetch numbers from a given URL
def fetch_numbers_from_url(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return response.json().get("numbers", [])
    except requests.exceptions.RequestException:
        return []
    return []

# Function to get URL based on number ID
def construct_url(number_id):
    base_url = "http://20.244.56.144/test/"
    endpoints = {
        'p': 'prime',
        'f': 'fibo',
        'e': 'even',
        'r': 'rand'
    }
    return base_url + endpoints.get(number_id, '')

# Function to update the number store with new numbers
def update_number_store(new_numbers):
    with lock:
        for num in new_numbers:
            if num not in number_store:
                number_store.append(num)
        while len(number_store) > WINDOW_SIZE:
            number_store.pop(0)

# Function to calculate the average of the numbers in the store
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# Route to handle fetching numbers based on the number ID
@app.route('/numbers/<number_id>', methods=['GET'])
def fetch_numbers(number_id):
    url = construct_url(number_id)
    if not url:
        return jsonify({"error": "Invalid number ID"}), 400

    previous_state = list(number_store)
    new_numbers = fetch_numbers_from_url(url)
    update_number_store(new_numbers)

    average = calculate_average(number_store)
    return jsonify({
        "previousState": previous_state,
        "currentState": list(number_store),
        "fetchedNumbers": new_numbers,
        "average": average
    })

if __name__ == '__main__':
    app.run(port=9876)
