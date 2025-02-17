# Use an official Python runtime as a parent image
FROM python:3.11.9

# Set the working directory in the container to /app
WORKDIR /app

# Update 
RUN apt-get update && apt-get install -y rsync

# Fix vulnerabilities with old packages
RUN apt-get upgrade -y libaom3 git libexpat openexr zlib

# Add the current directory contents into the container at /app
ADD . .

# Remove the .env.sample and .env files from the image if they exist
RUN rm -f .env.sample && rm -f .env

# Create the debug.log file and make it group read-writable
RUN mkdir logs && touch logs/debug.log && chmod g+rw logs/debug.log

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME=World

# Run start.py when the container launches
CMD ["python", "start.py"]
