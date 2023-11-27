from flask import Flask, request, jsonify
from collections import Counter
import re
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
import time
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
import psutil
from datetime import datetime, timedelta
import os
import os

app = Flask(__name__)

# Access variables
db_user = os.environ["db_user"]
db_password = os.environ["db_password"]
db_host = os.environ["db_host"]
db_name = os.environ["db_name"]
db_port = os.environ["db_port"]
platfrom = os.environ["platform"]

# Configure PostgreSQL database using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy

# Define the models for your existing tables
class TextProcessingMetrics(db.Model):
    __tablename__ = 'text_processing_metrics'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String)
    text_length = db.Column(db.Integer)
    time_elapsed = db.Column(db.Float)
    cpu_utilized = db.Column(db.Float)
    vmemory_utilized = db.Column(db.Float)
    success = db.Column(db.Float)
    timestamp = db.Column(db.TIMESTAMP)

class TimeMetrics(db.Model):
    __tablename__ = 'time_metrics'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String)
    requests_handled = db.Column(db.Integer)
    words_processed = db.Column(db.Integer)
    avg_cpu_utilized = db.Column(db.Float)
    avg_vmemory_utilized = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    timestamp = db.Column(db.TIMESTAMP)

# Create the tables before running the app
with app.app_context():
    db.create_all()

# Scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()

def save_text_processing_metrics(platform, text_length, time_elapsed, cpu_utilized, vmemory_utilized, success, timestamp):
    """Save text processing metrics to the database."""
    metrics = TextProcessingMetrics(
        platform=platform,
        text_length=text_length,
        time_elapsed=time_elapsed,
        cpu_utilized=cpu_utilized,
        vmemory_utilized=vmemory_utilized,
        success=success,
        timestamp=timestamp
    )
    db.session.add(metrics)
    db.session.commit()
    print("Successfully sent data to text_processing_metrics table")

def save_time_metrics():
    """Save time metrics to the database."""
    with app.app_context():
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)

        # Count requests handled in the last 1 minute
        requests_handled = (
            db.session
            .query(func.count())
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .scalar()
        )

        words_processed = (
            db.session
            .query(func.sum(TextProcessingMetrics.text_length))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .scalar()
        )

        cpu_percent = (
            db.session
            .query(func.avg(TextProcessingMetrics.cpu_utilized))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .scalar()
        )

        memory_percent = (
            db.session
            .query(func.avg(TextProcessingMetrics.vmemory_utilized))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .scalar()
        )

        success_rate = (
            db.session
            .query(func.avg(func.cast(TextProcessingMetrics.success, db.Float)))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .scalar()
        )

        metrics = TimeMetrics(
            platform=platfrom,
            requests_handled=requests_handled,
            words_processed=words_processed,
            avg_cpu_utilized=cpu_percent,
            avg_vmemory_utilized=memory_percent,
            success_rate=success_rate,
            timestamp=datetime.now().isoformat()
        )
        db.session.add(metrics)
        db.session.commit()
    print("Successfully sent data to time_metrics table")

# API endpoint to query data
@app.route('/api/query', methods=['GET'])
def texts_query():
    """API endpoint to query data."""
    # Replace the query based on your requirements
    result = db.session.query(TextProcessingMetrics).filter(TextProcessingMetrics.length > 10).count()
    print("Executed the query...")
    return jsonify(result)

# API endpoint to receive data
@app.route('/api/receiver', methods=['POST'])
def receive_data():
    """API endpoint to receive data."""
    if request.method == 'POST':
        start = time.time()

        data = request.get_json()
        text = data.get('text')

        words = re.findall(r'\w+', text.lower())
        word_count = Counter(words)
        top_10_words = word_count.most_common(10)

        end = time.time()
        time_elapsed = end - start

        # Convert the tuple to a dictionary
        request_info = {
            "title": data.get('title'),
            "length": len(words),
            "mostCommonWord": top_10_words[0][0],
            "time_elapsed": time_elapsed,
            "timestamp": datetime.now().isoformat(),  # Convert datetime to ISO format
        }

        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        # Save processing metrics after each API call
        save_text_processing_metrics(
            platform=platfrom,
            text_length=len(words),
            time_elapsed=time_elapsed,
            cpu_utilized=cpu_percent,
            vmemory_utilized=memory_percent,
            success=1,
            timestamp=datetime.now().isoformat()
        )

        return jsonify(request_info)

if __name__ == '__main__':
    # Schedule the task to save time metrics every minute
    scheduler.add_job(save_time_metrics, 'interval', minutes=1)
    
    port = 5001
    print("App starting...")
    print(f"Listening on {port}")
    serve(app, host='0.0.0.0', port=port)
