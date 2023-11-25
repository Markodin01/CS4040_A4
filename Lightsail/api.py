from flask import Flask, request, jsonify
from collections import Counter
import re
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
import time

app = Flask(__name__)

# Configure SQLite in-memory database using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking, as it's not needed for SQLite

db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy

# Define the Text model
class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String)
    length = db.Column(db.Integer)
    mostCommonWord = db.Column(db.String)
    time_elapsed = db.Column(db.Float)

# Create the tables before running the app
with app.app_context():
    db.create_all()


@app.route('/api/query', methods=['GET'])
def texts_query():
    result = db.session.query(Text).filter(Text.sentiment == "Neutral", Text.length > 10).count()
    print("Executed the query...")
    return jsonify(result)

@app.route('/api/receiver', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        start = time.time()

        data = request.get_json()

        text = data.get('text')

        words = re.findall(r'\w+', text.lower())
        word_count = Counter(words)
        top_10_words = word_count.most_common(10)
        

        end = time.time()

        time_elapsed = end - start

        response_data = {"word_frequency": dict(top_10_words), "time_elapsed": time_elapsed}

        # Save information to the database
        request_info = Text(
            title=data.get('title'),
            length=len(words),
            mostCommonWord=top_10_words[0][0],
            time_elapsed = time_elapsed
        )

        db.session.add(request_info)
        db.session.commit()

        return jsonify(response_data)

if __name__ == '__main__':
    port = 5001
    print("app starting...")
    print(f"listening on {port}")
    serve(app, host='0.0.0.0', port=port)
