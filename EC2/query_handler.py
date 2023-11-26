# query_handler.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta

db = SQLAlchemy()

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

def save_text_processing_metrics(platform, text_length, time_elapsed, cpu_utilized, vmemory_utilized, success, timestamp):
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
    with db.app.app_context():
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)

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
            platform='lightsail',
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

def get_text_metrics():
    # Implement the function to retrieve and return text metrics as needed
    pass
