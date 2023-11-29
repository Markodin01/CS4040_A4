from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import csv
from models import TextProcessingMetrics, TimeMetrics
import os

# Set the connection parameters
# Access variables from environment
db_user = os.environ["db_user"]
db_password = os.environ["db_password"]
db_host = os.environ["db_host"]
db_name = os.environ["db_name"]
db_port = os.environ["db_port"]
platform = os.environ["platform"]

# Create a PostgreSQL engine
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

def query_text_processing_metrics(platform):
    """
    Query text processing metrics for a specific platform and time range.

    Parameters:
    - platform (str): The platform to query (e.g., 'lightsail', 'ec2').
    - start_time (datetime): The start time of the time range.
    - end_time (datetime): The end time of the time range.

    Returns:
    - list: A list of TextProcessingMetrics objects.
    """
    metrics = (
        session.query(TextProcessingMetrics)
        .filter(TextProcessingMetrics.platform == platform)
        .filter(TextProcessingMetrics.timestamp >= 10000)
        .all()
    )
    return metrics

def query_time_metrics(platform):
    """
    Query time metrics for a specific platform and time range.

    Parameters:
    - platform (str): The platform to query (e.g., 'lightsail', 'ec2').
    - start_time (datetime): The start time of the time range.
    - end_time (datetime): The end time of the time range.

    Returns:
    - list: A list of TimeMetrics objects.
    """
    metrics = (
        session.query(TimeMetrics)
        .filter(TimeMetrics.platform == platform)
        .filter(TimeMetrics.num_paragraphs >= 10000)
        .all()
    )
    return metrics

# Function to save metrics to a CSV file
def save_metrics_to_csv(metrics, file_path):
    """
    Save metrics to a CSV file.

    Parameters:
    - metrics (list): A list of SQLAlchemy model objects.
    - file_path (str): The path to the CSV file.
    """
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = metrics[0].__dict__.keys()  # Assumes all metrics have the same fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()

        # Write data
        for metric in metrics:
            writer.writerow(metric.__dict__)

if __name__ == "__main__":
    platforms_to_query = ['lightsail', 'ec2']


    for platform in platforms_to_query:
        
        # Query and save text processing metrics
        text_processing_metrics = query_text_processing_metrics(platform)
        print(f"Text Processing Metrics for '{platform}':")
        for metric in text_processing_metrics:
            save_metrics_to_csv(metric.__dict__, f"/metrics_analysis/data/text_processing_metrics_{platform}")

        # Query and save time metrics
        time_metrics = query_time_metrics(platform)
        print(f"Time Metrics for '{platform}':")
        for metric in time_metrics:
            save_metrics_to_csv(metric.__dict__, f"/metrics_analysis/data/time_metrics_{platform}")
