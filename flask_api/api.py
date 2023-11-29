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
from flask_cors import CORS  # Import the CORS module
from models import TextProcessingMetrics, TimeMetrics

# Create a Flask web application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in your app

# Access variables from environment
db_user = os.environ["db_user"]
db_password = os.environ["db_password"]
db_host = os.environ["db_host"]
db_name = os.environ["db_name"]
db_port = os.environ["db_port"]
platform = os.environ["platform"]

# Configure PostgreSQL database using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)



# Create the tables before running the app
with app.app_context():
    db.create_all()

# Scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()

def save_text_processing_metrics(platform, text_length, time_elapsed, cpu_utilized, vmemory_utilized, success, timestamp, num_paragraphs):
    """Save text processing metrics to the database."""
    metrics = TextProcessingMetrics(
        platform=platform,
        text_length=text_length,
        time_elapsed=time_elapsed,
        cpu_utilized=cpu_utilized,
        vmemory_utilized=vmemory_utilized,
        success=success,
        timestamp=timestamp,
        num_paragraphs=num_paragraphs
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
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        # Count words processed in the last 1 minute
        words_processed = (
            db.session
            .query(func.sum(TextProcessingMetrics.text_length))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        cpu_percent = (
            db.session
            .query(func.avg(TextProcessingMetrics.cpu_utilized))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        memory_percent = (
            db.session
            .query(func.avg(TextProcessingMetrics.vmemory_utilized))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        # Average success rate
        success_rate = (
            db.session
            .query(func.avg(func.cast(TextProcessingMetrics.success, db.Float)))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        # Show how many paragraphs are being handled in current batch in the last 1 minute
        num_paragraphs = (
            db.session
            .query(func.min(func.cast(TextProcessingMetrics.num_paragraphs, db.Float)))
            .filter(TextProcessingMetrics.timestamp >= one_minute_ago.isoformat())
            .filter(TextProcessingMetrics.platform == platform)
            .scalar()
        )

        metrics = TimeMetrics(
            platform=platform,
            requests_handled=requests_handled,
            words_processed=words_processed,
            avg_cpu_utilized=cpu_percent,
            avg_vmemory_utilized=memory_percent,
            success_rate=success_rate,
            timestamp=datetime.now().isoformat(),
            num_paragraphs=num_paragraphs
        )
        db.session.add(metrics)
        db.session.commit()
    print("Successfully sent data to time_metrics table")

# API endpoint to receive data
@app.route('/', methods=['Post'])
def receive_data():
    try:
        """API endpoint to receive data."""
        if request.method == 'POST':
            start = time.time()

            data = request.get_json()
            text = data.get('text')

            num_paragraphs = data.get('num_paragraphs')

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

            # Use psutil to get the cpu and memory metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Save processing metrics after each API call
            save_text_processing_metrics(
                platform=platform,
                text_length=len(words),
                time_elapsed=time_elapsed,
                cpu_utilized=cpu_percent,
                vmemory_utilized=memory_percent,
                success=1,
                timestamp=datetime.now().isoformat(),
                num_paragraphs=num_paragraphs
            )

            return jsonify(request_info)
    except:
            
            # Return no success if there was a problem with
            # sending the metircs

            save_text_processing_metrics(
                platform=platform,
                text_length=None,
                time_elapsed=None,
                cpu_utilized=None,
                vmemory_utilized=None,
                success=0,
                timestamp=datetime.now().isoformat(),
                num_paragraphs=None
            )

            return jsonify()

# Run the application if it's the main module
if __name__ == '__main__':
    # Schedule the background job to run every 1 minute
    scheduler.add_job(save_time_metrics, 'interval', minutes=1)
    
    # Set the port for the Flask app
    port = 5000
    print("App starting...")
    print(f"Listening on {port}")
    
    # Run the Flask app with debug mode
    app.run(host='0.0.0.0', port=port, debug=True)
