import requests
import json
import lorem
import time

# Replace this URL with the actual URL of your Flask API
api_url = "http://localhost:5001/api/receiver"
counter = 0

while True:
    # Generate 10 paragraphs of Lorem Ipsum text
    num_paragraphs = 100000
    lorem_text = '\n'.join(lorem.paragraph() for _ in range(num_paragraphs))

    # Create the JSON payload
    data = {
        "text": lorem_text,
        "title": "Automatically Crafted Title"
    }

    # Send a POST request to the API
    response = requests.post(api_url, json=data)

    # Check the response
    if response.status_code == 200:
        print("Data sent successfully.")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        time.sleep(0.5)
    else:
        print(f"Failed to send data. Status code: {response.status_code}")
        print("Response:")
        print(response.text)
        counter += 1
        time.sleep(0.5)
    
    if counter > 20:
        break
