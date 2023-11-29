# Use the alpine image with amd64 architecture as the base image
FROM --platform=linux/amd64 alpine

# Use the official Python image as the base image
FROM python

# Set the working directory inside the container
WORKDIR /

# Copy the requirements file to the working directory
COPY requirements.txt .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Upgrade pip and install dependencies from requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire current directory into the container
COPY . .

# Specify the command to run when the container starts
CMD [ "python", "api.py" ]
