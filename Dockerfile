# Set the arch to amd64 for linux
FROM --platform=linux/amd64  alpine:3.10

# Set base image (host OS)
FROM python

WORKDIR /

COPY requirements.txt .

EXPOSE 5001

# Install any dependencies
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "api.py" ]