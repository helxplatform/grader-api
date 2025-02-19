ARG BASE_IMAGE=containers.renci.org/helxplatform/grader-api-poetry-base
ARG BASE_IMAGE_TAG=v1.0.3
# Use our base image
FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . .

# Create the debug.log file and make it group read-writable
RUN mkdir logs && touch logs/debug.log && chmod g+rw logs/debug.log

# Install any needed packages with poetry bundle plugin
RUN poetry install --only main --no-root --no-ansi

# Set PATH variable to include virtual environment directory
ENV PATH="/app/.venv/bin:$PATH"

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run start.py when the container launches
CMD ["python3", "start.py"]
