import requests
import lorem
import time
import os

def send_data_to_api(api_url, num_paragraphs):
    """
    Send a POST request to the API with Lorem Ipsum text.

    Parameters:
    - api_url (str): The URL of the Flask API.
    - num_paragraphs (int): The number of paragraphs to generate and send.

    Returns:
    - bool: True if the request was successful, False otherwise.
    """
    try:
        # Generate Lorem Ipsum text
        lorem_text = '\n'.join(lorem.paragraph() for _ in range(num_paragraphs))

        # Create the JSON payload
        data = {
            "text": lorem_text,
            "title": lorem.sentence(),
            "num_paragraphs": num_paragraphs
        }

        # Send a POST request to the API
        response = requests.post(api_url, json=data)

        # Check the response status code
        if response.status_code == 200:
            print("Success")
            return True
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
            print("Response:")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Replace this URL with the actual URL of your Flask API
counter = 0

# Define platforms and their corresponding endpoints
platforms = {
    "lightsail": os.environ['lightsail_endpoint'],
    "ec2": os.environ['ec2_endpoint']
}

# Iterate over platforms
for platform, endpoint in platforms.items():
    api_url = endpoint

    # Iterate over different numbers of paragraphs
    for i in range(6):
        start_time = time.time()  # Record the start time
        counter = 0

        while True:
            # Set the number of paragraphs to be sent
            num_paragraphs = 10000 * (i + 1)

            # Send data to the API
            success = send_data_to_api(api_url, num_paragraphs)

            # Check if the request was unsuccessful
            if not success:
                counter += 1

            # Break out of the loop if more than 20 consecutive failures
            if counter > 20:
                print("More than 20 consecutive fails!!!")
                break

            elapsed_time = time.time() - start_time
            # Break out of the loop if 30 minutes have passed
            if elapsed_time > 1800:  # 1800 seconds = 30 minutes
                print("Time limit reached. Breaking out of the loop.")
                break
