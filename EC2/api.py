from flask import Flask, request, jsonify
from collections import Counter
import re
import psutil
from waitress import serve  # Import the waitress server

app = Flask(__name__)

@app.route('/api/receiver', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the POST request

        text = data.get('text')  # Assuming the text data is sent as 'text' in the JSON

        words = re.findall(r'\w+', text.lower())  # Tokenize the text into words
        word_count = Counter(words)  # Count the frequency of each word

        top_10_words = word_count.most_common(10)  # Top 10 words by frequency

        sentiment = 'Positive' if 'good' in words else 'Neutral'  # Sample sentiment analysis

        response_data = {"word_frequency": dict(top_10_words), "sentiment": sentiment}

        # Get CPU and memory usage using psutil
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        response_data['cpu_percent'] = cpu_percent
        response_data['memory_percent'] = memory_percent

        return jsonify(response_data)  # Sending a response as JSON

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=1)  # Run the Flask app with Waitress server using 1 thread
