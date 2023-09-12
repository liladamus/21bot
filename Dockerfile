# Use an official Python runtime as a parent image
FROM python:3.6-slim-buster

WORKDIR /app

ADD ./requirements.txt /app


# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container to /app

# Add the current directory contents into the container at /app
ADD . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
