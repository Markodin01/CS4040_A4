from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the models for your existing tables
class TextProcessingMetrics(db.Model):
    """Model for the 'text_processing_metrics' table."""
    __tablename__ = 'text_processing_metrics'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String)
    text_length = db.Column(db.Integer)
    time_elapsed = db.Column(db.Float)
    cpu_utilized = db.Column(db.Float)
    vmemory_utilized = db.Column(db.Float)
    success = db.Column(db.Float)
    timestamp = db.Column(db.TIMESTAMP)
    num_paragraphs = db.Column(db.Integer)

class TimeMetrics(db.Model):
    """Model for the 'time_metrics' table."""
    __tablename__ = 'time_metrics'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String)
    requests_handled = db.Column(db.Integer)
    words_processed = db.Column(db.Integer)
    avg_cpu_utilized = db.Column(db.Float)
    avg_vmemory_utilized = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    timestamp = db.Column(db.TIMESTAMP)
    num_paragraphs = db.Column(db.Integer)